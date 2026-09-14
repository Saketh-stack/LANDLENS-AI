"""
MultilingualOCRService: Script-aware OCR and text extraction for Indian land documents.
Powered by PaddleOCR (PP-OCRv4 ONNX Runtime), integrated preprocessing,
and deep Indian language detection.
"""
from typing import Dict, Any, Optional
from backend.app.ai.multilingual.normalizer import TextNormalizationService

class MultilingualOCRService:
    """
    Multilingual Document Recognition Pipeline.
    Supports English + 12 Indian languages across printed and scanned documents.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider
        self._engine = None

    def get_engine(self):
        if self._engine is None:
            from backend.app.services.ocr_service import OCRService as UnifiedPaddleOCRService
            self._engine = UnifiedPaddleOCRService(provider=self.provider)
        return self._engine

    def process_document(self, file_path: str) -> Dict[str, Any]:
        engine = self.get_engine()
        res = engine.process_document(file_path)
        raw_text = res.get("text", "")
        # Add numeral normalization
        normalized_text = TextNormalizationService.normalize_numerals(raw_text)
        res["normalized_text"] = normalized_text
        return res

    def process_image(self, file_path: str) -> Dict[str, Any]:
        return self.process_document(file_path)

    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        return self.process_document(file_path)
