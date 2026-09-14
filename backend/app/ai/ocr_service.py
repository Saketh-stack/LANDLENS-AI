"""
OCRService facade connecting to the unified PaddleOCR service in backend.app.services.ocr_service.
Maintains full backward compatibility.
"""
from typing import Dict, Any, Optional

class OCRService:
    """
    Real Pan-India OCR & Document Extraction Provider.
    Powered by PaddleOCR (PP-OCRv4 Deep Learning ONNX Engine).
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider
        self._impl = None

    def get_impl(self):
        if self._impl is None:
            from backend.app.services.ocr_service import OCRService as PrimaryPaddleOCRService
            self._impl = PrimaryPaddleOCRService(provider=self.provider)
        return self._impl

    def process_document(self, file_path: str) -> Dict[str, Any]:
        return self.get_impl().process_document(file_path)

    def process_image(self, file_path: str) -> Dict[str, Any]:
        return self.get_impl().process_document(file_path)

    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        return self.get_impl().process_document(file_path)

    def extract_text(self, file_path: str) -> str:
        res = self.get_impl().process_document(file_path)
        return res.get("text", "")

    def detect_language(self, text: str) -> str:
        from backend.app.ai.multilingual.language_detector import LanguageDetectionService
        return LanguageDetectionService.detect_languages(text).get("summary", "English")

    def extract_handwritten_text(self, file_path: str) -> Dict[str, Any]:
        res = self.get_impl().process_document(file_path)
        res["is_handwritten"] = True
        return res
