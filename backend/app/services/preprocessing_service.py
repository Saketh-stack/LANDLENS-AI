"""
PreprocessingService: Non-destructive image enhancement and quality analysis
for scanned historical Indian land records, cadastral maps, and deeds.
"""
import os
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List, Tuple, Optional
from backend.app.core.logging import logger

class PreprocessingService:
    """
    Production Preprocessing Pipeline for Indian Land Documents.
    Strictly preserves the original uploaded file unaltered.
    """

    @staticmethod
    def compute_phash(image: np.ndarray, hash_size: int = 8) -> str:
        """Computes difference hash (dHash) for visual perceptual duplicate detection."""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            resized = cv2.resize(gray, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)
            diff = resized[:, 1:] > resized[:, :-1]
            return format(int("".join(["1" if v else "0" for v in diff.flatten()]), 2), f"0{hash_size*hash_size // 4}x")
        except Exception as e:
            logger.warning(f"pHash calculation failed: {e}")
            return ""

    @staticmethod
    def analyze_quality(image: np.ndarray) -> Dict[str, Any]:
        """
        Analyzes image quality: resolution, estimated DPI, blur level (Laplacian variance),
        brightness, and contrast uniformity.
        """
        h, w = image.shape[:2]
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # 1. Blur score: Laplacian variance (standard measure of edge sharpness)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # 2. Estimated DPI assuming standard A4 document (8.27 x 11.69 inches)
        est_dpi = round(max(w / 8.27, h / 11.69), 1)

        # 3. Brightness and contrast
        mean_brightness = float(np.mean(gray))
        contrast_std = float(np.std(gray))

        # 4. Determine Quality Tier
        is_low_res = w < 1200 or h < 1200 or est_dpi < 150
        is_blurry = laplacian_var < 80.0
        is_poor_contrast = contrast_std < 35.0

        if is_blurry and is_low_res:
            quality_tier = "POOR_QUALITY"
            quality_score = max(35.0, round(min(laplacian_var, 60.0), 1))
        elif is_low_res or is_blurry or is_poor_contrast:
            quality_tier = "MEDIUM"
            quality_score = min(85.0, max(65.0, round(laplacian_var * 0.5, 1)))
        else:
            quality_tier = "HIGH"
            quality_score = min(98.5, round(75.0 + min(laplacian_var * 0.05, 23.5), 1))

        return {
            "resolution": f"{w}x{h}",
            "width": w,
            "height": h,
            "estimated_dpi": est_dpi,
            "blur_metric": round(laplacian_var, 1),
            "mean_brightness": round(mean_brightness, 1),
            "contrast_std": round(contrast_std, 1),
            "quality_tier": quality_tier,
            "quality_score": quality_score,
            "is_low_res": is_low_res,
            "is_blurry": is_blurry,
            "requires_enhancement": is_low_res or is_blurry or is_poor_contrast
        }

    @staticmethod
    def convert_pdf_to_images(pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
        """Renders PDF pages to high-resolution PNG images using pypdfium2."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        out_dir = output_dir or os.path.dirname(pdf_path)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        rendered_paths = []

        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(pdf_path)
            num_pages = len(pdf)
            for page_idx in range(min(num_pages, 5)):  # Render up to 5 pages
                page = pdf[page_idx]
                pil_img = page.render(scale=2.5).to_pil()
                page_filename = f"{base_name}_page_{page_idx + 1}.png"
                page_dest = os.path.join(out_dir, page_filename)
                pil_img.save(page_dest, "PNG")
                rendered_paths.append(page_dest)
            logger.info(f"Rendered {len(rendered_paths)} pages from PDF: {pdf_path}")
        except Exception as e:
            logger.error(f"Failed to render PDF with pypdfium2: {e}")

        return rendered_paths

    @staticmethod
    def deskew(gray_image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Detects skew angle and rotates image to level text lines."""
        try:
            thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            coords = np.column_stack(np.where(thresh > 0))
            if coords.shape[0] < 50:
                return gray_image, 0.0

            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            if abs(angle) < 0.25 or abs(angle) > 45.0:
                return gray_image, 0.0

            h, w = gray_image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(gray_image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated, float(round(angle, 2))
        except Exception as e:
            logger.warning(f"Deskew error: {e}")
            return gray_image, 0.0

    @staticmethod
    def detect_perspective_correction(image_bgr: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Detects quadrilateral document boundaries and applies four-point perspective warp.
        If no quadrilateral is found, returns original image.
        """
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 150)

            # Morphological close to bridge edge gaps
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
            closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return image_bgr, False

            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            img_area = image_bgr.shape[0] * image_bgr.shape[1]

            for c in contours[:5]:
                area = cv2.contourArea(c)
                if area < 0.35 * img_area:
                    continue

                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)

                if len(approx) == 4:
                    pts = approx.reshape(4, 2)
                    rect = np.zeros((4, 2), dtype="float32")

                    s = pts.sum(axis=1)
                    rect[0] = pts[np.argmin(s)]  # top-left
                    rect[2] = pts[np.argmax(s)]  # bottom-right

                    diff = np.diff(pts, axis=1)
                    rect[1] = pts[np.argmin(diff)]  # top-right
                    rect[3] = pts[np.argmax(diff)]  # bottom-left

                    (tl, tr, br, bl) = rect
                    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
                    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
                    maxWidth = max(int(widthA), int(widthB))

                    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
                    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
                    maxHeight = max(int(heightA), int(heightB))

                    if maxWidth < 400 or maxHeight < 400:
                        continue

                    dst = np.array([
                        [0, 0],
                        [maxWidth - 1, 0],
                        [maxWidth - 1, maxHeight - 1],
                        [0, maxHeight - 1]], dtype="float32")

                    M = cv2.getPerspectiveTransform(rect, dst)
                    warped = cv2.warpPerspective(image_bgr, M, (maxWidth, maxHeight))
                    return warped, True
        except Exception as e:
            logger.warning(f"Perspective detection exception: {e}")

        return image_bgr, False

    @classmethod
    def preprocess_document(cls, input_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the full preprocessing pipeline:
        1. Preserves original document unaltered
        2. Converts PDF to raster images if needed
        3. Analyzes resolution, blur, illumination
        4. Applies deskew, CLAHE, bilateral denoise, unsharp sharpening
        5. Saves preprocessed version with metadata
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        out_dir = output_dir or os.path.dirname(input_path)
        base_name, ext = os.path.splitext(os.path.basename(input_path))
        ext_lower = ext.lower()

        applied_steps: List[str] = []

        # Handle PDF
        if ext_lower == ".pdf":
            pages = cls.convert_pdf_to_images(input_path, out_dir)
            if pages:
                source_img_path = pages[0]
                applied_steps.append(f"PDF Rasterization ({len(pages)} pages extracted via pypdfium2)")
            else:
                source_img_path = input_path
        else:
            source_img_path = input_path

        # Load image with OpenCV / Pillow
        img = cv2.imread(source_img_path)
        if img is None:
            pil_img = Image.open(source_img_path).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        orig_h, orig_w = img.shape[:2]

        # Compute perceptual hash of original
        phash_val = cls.compute_phash(img)

        # Quality Analysis of original
        quality_meta = cls.analyze_quality(img)

        # 1. Perspective correction if quadrilateral document frame exists
        perspective_corrected, did_warp = cls.detect_perspective_correction(img)
        if did_warp:
            applied_steps.append("Perspective Correction (Quadrilateral Document Alignment)")
            img_to_process = perspective_corrected
        else:
            img_to_process = img

        # 2. Upscaling for low-resolution documents
        if quality_meta["is_low_res"] and (orig_w < 1200 or orig_h < 1200):
            scale_factor = min(2.0, 1600.0 / max(orig_w, orig_h))
            img_to_process = cv2.resize(
                img_to_process,
                (int(img_to_process.shape[1] * scale_factor), int(img_to_process.shape[0] * scale_factor)),
                interpolation=cv2.INTER_CUBIC
            )
            applied_steps.append(f"Bicubic Upscaling ({scale_factor:.1f}x for Low-Resolution Scan)")

        # 3. Grayscale conversion
        gray = cv2.cvtColor(img_to_process, cv2.COLOR_BGR2GRAY)
        applied_steps.append("Grayscale Normalization")

        # 4. Deskew detection & rotation
        deskewed, skew_angle = cls.deskew(gray)
        if abs(skew_angle) >= 0.3:
            applied_steps.append(f"Skew Correction ({skew_angle:.1f}° rotation)")
        else:
            deskewed = gray
            applied_steps.append("Alignment Verified (Optimal Angle)")

        # 5. Denoising: Bilateral filtering preserves crisp text edges while smoothing noise
        denoised = cv2.bilateralFilter(deskewed, d=7, sigmaColor=50, sigmaSpace=50)
        applied_steps.append("Bilateral Noise Filtering (Edge-Preserving Smoothing)")

        # 6. Contrast Enhancement: CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        applied_steps.append("Contrast Enhancement (CLAHE 8x8 Grid)")

        # 7. Sharpening: Unsharp masking for faded ink/scanned text
        blurred_clahe = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
        sharpened = cv2.addWeighted(enhanced, 1.4, blurred_clahe, -0.4, 0)
        applied_steps.append("Unsharp Mask Sharpening (Faded Script Recovery)")

        # Save preprocessed image (never overwrite original!)
        preprocessed_filename = f"{base_name}_preprocessed.png"
        preprocessed_dest = os.path.join(out_dir, preprocessed_filename)
        cv2.imwrite(preprocessed_dest, sharpened)

        # Quality check: decide primary path for OCR
        primary_ocr_path = preprocessed_dest if os.path.exists(preprocessed_dest) else input_path

        return {
            "original_path": input_path,
            "preprocessed_path": preprocessed_dest,
            "primary_ocr_path": primary_ocr_path,
            "phash": phash_val,
            "quality_analysis": quality_meta,
            "skew_angle": skew_angle,
            "steps_applied": applied_steps,
            "original_preserved": True
        }
