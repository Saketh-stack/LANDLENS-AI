"""
OCRService: Primary Document Recognition Layer powered by PaddleOCR.
Provides clean service abstraction for text detection, text recognition,
region extraction, and multilingual Indian land record processing.
"""
import os
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List, Optional, Tuple

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.services.preprocessing_service import PreprocessingService
from backend.app.ai.multilingual.language_detector import LanguageDetectionService

class OCRService:
    """
    Primary OCR & Document Recognition Service.
    Uses PaddleOCR (PP-OCRv4 Deep Learning detection and recognition models via ONNX Runtime)
    with clean abstraction for pluggability.
    """
    _paddle_engine = None

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or getattr(settings, 'OCR_PROVIDER', 'PADDLEOCR')

    @classmethod
    def get_paddle_engine(cls):
        """Initializes and caches the PaddleOCR PP-OCRv4 ONNX engine."""
        if cls._paddle_engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                # RapidOCR is the official ONNX runtime implementation of PaddleOCR PP-OCRv4 models
                cls._paddle_engine = RapidOCR()
                logger.info("PaddleOCR engine (PP-OCRv4 ONNX Runtime) initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR engine: {e}")
                cls._paddle_engine = False
        return cls._paddle_engine if cls._paddle_engine is not False else None

    def detect_text(self, image: np.ndarray) -> List[List[List[float]]]:
        """
        Text Detection Layer:
        Detects bounding boxes / polygons of text lines in the document.
        """
        engine = self.get_paddle_engine()
        if engine is not None:
            try:
                results, _ = engine(image)
                if results:
                    return [r[0] for r in results]
            except Exception as e:
                logger.warning(f"Text detection failed: {e}")
        return []

    def recognize_text(self, image: np.ndarray, boxes: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Text Recognition Layer:
        Recognizes text content, character confidence, and bounding boxes.
        """
        engine = self.get_paddle_engine()
        recognized_lines = []
        if engine is not None:
            try:
                results, _ = engine(image)
                if results:
                    for r in results:
                        box = r[0]  # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                        text = str(r[1]).strip()
                        raw_conf = float(r[2])
                        conf = raw_conf if raw_conf <= 1.0 else round(raw_conf / 100.0, 4)
                        conf_pct = round(conf * 100.0, 1)

                        # Bounding box as [x1, y1, x2, y2]
                        xs = [p[0] for p in box]
                        ys = [p[1] for p in box]
                        x1, y1, x2, y2 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))

                        # Script detection per line
                        line_lang = LanguageDetectionService.detect_languages(text).get("primary_code", "en")

                        recognized_lines.append({
                            "text": text,
                            "confidence": conf,
                            "confidence_pct": conf_pct,
                            "bbox": [x1, y1, x2, y2],
                            "polygon": [[int(p[0]), int(p[1])] for p in box],
                            "language": line_lang
                        })
            except Exception as e:
                logger.warning(f"Text recognition failed: {e}")
        return recognized_lines

    def extract_regions(self, image_h: int, image_w: int, ocr_lines: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Region/Layout Detection:
        Associates OCR text lines with spatial/functional document zones:
        - registration_section
        - parties_section
        - parcel_survey_section
        - area_extent_section
        - boundaries_section
        - general_section
        """
        regions = {
            "registration_section": [],
            "parties_section": [],
            "parcel_survey_section": [],
            "area_extent_section": [],
            "boundaries_section": [],
            "general_section": []
        }

        for line in ocr_lines:
            t_low = line["text"].lower()

            # Classification into regions based on legal keyword markers
            if any(k in t_low for k in ["registration", "deed no", "reg no", "book no", "stamp", "पंजीयन", "రిజిస్ట్రేషన్", "பதிவு"]):
                regions["registration_section"].append(line)
            elif any(k in t_low for k in ["owner", "purchaser", "vendor", "buyer", "seller", "pattadar", "father", "husband", "son of", "s/o", "w/o", "d/o", "shri", "smt", "భూయజమాని", "मालिक", "खातेदार"]):
                regions["parties_section"].append(line)
            elif any(k in t_low for k in ["survey", "khasra", "khata", "plot", "sy.no", "sy no", "s.no", "gut no", "dag no", "सर्वे", "खसरा", "సర్వే", "ఖాతా"]):
                regions["parcel_survey_section"].append(line)
            elif any(k in t_low for k in ["acres", "guntas", "cents", "bigha", "extent", "area", "रकबा", "क्षेत्रफल", "విస్తీర్ణం", "பரப்பளவு"]):
                regions["area_extent_section"].append(line)
            elif any(k in t_low for k in ["boundary", "boundaries", "north", "south", "east", "west", "चौहद्दी", "సరిహద్దులు", "எல்லைகள்"]):
                regions["boundaries_section"].append(line)
            else:
                # Spatial heuristic fallback based on document vertical location
                y_center = (line["bbox"][1] + line["bbox"][3]) / 2.0
                rel_y = y_center / max(float(image_h), 1.0)
                if rel_y < 0.25:
                    regions["registration_section"].append(line)
                elif rel_y < 0.50:
                    regions["parties_section"].append(line)
                elif rel_y < 0.75:
                    regions["parcel_survey_section"].append(line)
                else:
                    regions["general_section"].append(line)

        return regions

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        End-to-End Recognition Pipeline:
        1. Preprocess document (PDF conversion, deskew, CLAHE, denoising, quality analysis)
        2. Execute PaddleOCR PP-OCRv4
        3. Detect document scripts / languages
        4. Extract regions and bounding box coordinates
        5. Return clean structured output
        """
        logger.info(f"PaddleOCR processing document: {file_path}")
        if not os.path.exists(file_path):
            return self._fallback_response(os.path.basename(file_path), "File not found on disk")

        # 1. Non-destructive Preprocessing & Quality Analysis
        try:
            preproc_result = PreprocessingService.preprocess_document(file_path)
            ocr_image_path = preproc_result.get("primary_ocr_path", file_path)
        except Exception as e:
            logger.warning(f"Preprocessing exception, falling back to raw input: {e}")
            preproc_result = {
                "original_path": file_path,
                "preprocessed_path": file_path,
                "quality_analysis": {"quality_tier": "UNKNOWN", "quality_score": 75.0},
                "phash": "",
                "steps_applied": []
            }
            ocr_image_path = file_path

        # 2. Load image for OCR processing
        img = cv2.imread(ocr_image_path)
        if img is None:
            try:
                pil_img = Image.open(ocr_image_path).convert("RGB")
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except Exception as e:
                logger.error(f"Cannot load image {ocr_image_path}: {e}")
                return self._fallback_response(os.path.basename(file_path), str(e))

        h, w = img.shape[:2]

        # 3. Text Recognition using PaddleOCR PP-OCRv4
        lines = self.recognize_text(img)

        # 4. If primary OCR produced 0 lines on preprocessed, retry original image if different
        if not lines and preproc_result.get("original_path") != ocr_image_path:
            logger.info("Preprocessed image yielded 0 text lines. Retrying on original image...")
            orig_img = cv2.imread(preproc_result["original_path"])
            if orig_img is not None:
                lines = self.recognize_text(orig_img)
                if lines:
                    h, w = orig_img.shape[:2]

        # 5. Compile structured outputs
        if lines:
            text_lines = [l["text"] for l in lines]
            full_text = "\n".join(text_lines)
            avg_conf = round(sum([l["confidence_pct"] for l in lines]) / len(lines), 1)

            # Language and script detection
            lang_meta = LanguageDetectionService.detect_languages(full_text)

            # Extract layout regions
            regions = self.extract_regions(h, w, lines)

            # Bounding boxes dictionary format for frontend compatibility
            boxes_map = {}
            for i, l in enumerate(lines):
                boxes_map[f"line_{i}"] = {
                    "text": l["text"],
                    "confidence": l["confidence_pct"],
                    "x": l["bbox"][0],
                    "y": l["bbox"][1],
                    "w": l["bbox"][2] - l["bbox"][0],
                    "h": l["bbox"][3] - l["bbox"][1]
                }

            return {
                "text": full_text,
                "raw_text": full_text,
                "confidence": avg_conf,
                "lines": lines,
                "bounding_boxes": boxes_map,
                "regions": regions,
                "language": lang_meta.get("summary", "English"),
                "primary_language": lang_meta.get("primary_code", "en"),
                "primary_language_name": lang_meta.get("primary_name", "English"),
                "is_mixed_language": lang_meta.get("is_mixed", False),
                "detected_languages": lang_meta.get("distributions", []),
                "detected_scripts": lang_meta.get("scripts", ["Latin"]),
                "preprocessing_metadata": preproc_result,
                "phash": preproc_result.get("phash", ""),
                "provider": "PaddleOCR (PP-OCRv4 Multilingual Deep Learning Engine)",
                "success": True
            }

        # If OCR completely failed to recognize any text, return honest review required response
        return {
            "text": "",
            "raw_text": "",
            "confidence": 35.0,
            "lines": [],
            "bounding_boxes": {},
            "regions": {},
            "language": "Unknown",
            "preprocessing_metadata": preproc_result,
            "phash": preproc_result.get("phash", ""),
            "provider": "PaddleOCR (PP-OCRv4)",
            "requires_manual_review": True,
            "reason": "LOW_OCR_CONFIDENCE",
            "message": "The document could not be reliably recognized. Manual officer review is required.",
            "success": False
        }

    def _fallback_response(self, filename: str, error_msg: str) -> Dict[str, Any]:
        """Provides graceful structured response for unreadable or missing documents."""
        return {
            "text": "",
            "raw_text": "",
            "confidence": 0.0,
            "lines": [],
            "bounding_boxes": {},
            "regions": {},
            "language": "Unknown",
            "provider": "PaddleOCR Service",
            "requires_manual_review": True,
            "reason": "UNREADABLE_OR_MISSING_DOCUMENT",
            "message": f"Document {filename} could not be processed: {error_msg}",
            "success": False
        }
