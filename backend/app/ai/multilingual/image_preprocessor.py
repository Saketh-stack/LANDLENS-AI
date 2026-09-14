"""
ImagePreprocessor: Backward-compatible facade connecting to PreprocessingService.
Provides image enhancement, deskew, noise removal, and adaptive binarization
for scanned land records, cadastral maps, and registry documents.
"""
from typing import Dict, Any, Tuple
import numpy as np
from backend.app.services.preprocessing_service import PreprocessingService

class ImagePreprocessor:
    """
    Computer Vision Preprocessing Pipeline for Indian Land Documents.
    Applies non-destructive enhancements to improve OCR accuracy on real scanned documents.
    """

    @staticmethod
    def preprocess_image(input_path: str, output_path: str = None) -> Dict[str, Any]:
        res = PreprocessingService.preprocess_document(input_path, output_dir=None)
        return {
            "preprocessed_path": res["preprocessed_path"],
            "original_path": res["original_path"],
            "primary_ocr_path": res["primary_ocr_path"],
            "original_resolution": res["quality_analysis"]["resolution"],
            "skew_angle": res["skew_angle"],
            "quality_analysis": res["quality_analysis"],
            "steps_applied": res["steps_applied"],
            "phash": res["phash"]
        }

    @staticmethod
    def deskew(image: np.ndarray) -> Tuple[np.ndarray, float]:
        return PreprocessingService.deskew(image)
