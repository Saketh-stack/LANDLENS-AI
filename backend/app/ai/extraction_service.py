import json
from typing import Dict, Any
import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.ai.mock_ai_service import MockAIService
from backend.app.ai.confidence_service import ConfidenceService

class ExtractionService:
    """
    AI Field Extraction Engine:
    - Calls OpenAI API if OPENAI_API_KEY is configured and MOCK_MODE is False.
    - Uses deterministic MockAIService when key is absent or MOCK_MODE=True.
    """
    @classmethod
    async def extract_fields_from_text(cls, raw_text: str) -> Dict[str, Any]:
        if settings.is_gemini_enabled:
            try:
                return await cls._extract_with_gemini(raw_text)
            except Exception as e:
                logger.error(f"Gemini extraction failed: {e}. Trying OpenAI or fallback.")

        if settings.is_openai_enabled:
            try:
                return await cls._extract_with_openai(raw_text)
            except Exception as e:
                logger.error(f"OpenAI extraction failed: {e}. Falling back to deterministic engine.")

        mock_data = MockAIService.get_deterministic_extraction(raw_text)
        evaluated = ConfidenceService.evaluate_field_confidences(mock_data["record_data"])
        mock_data["confidence_evaluation"] = evaluated
        return mock_data

    @classmethod
    def extract_fields_sync(cls, raw_text: str) -> Dict[str, Any]:
        if settings.is_gemini_enabled or settings.is_openai_enabled:
            from backend.app.services.ai_extractor import AIExtractorService
            llm_res = AIExtractorService._extract_with_llm(raw_text)
            if llm_res:
                evaluated = ConfidenceService.evaluate_field_confidences(llm_res)
                return {
                    "record_data": llm_res,
                    "average_confidence": evaluated["average_confidence"],
                    "confidence_evaluation": evaluated,
                    "source": "Google Gemini" if settings.is_gemini_enabled else f"OpenAI {settings.OPENAI_MODEL}"
                }
        mock_data = MockAIService.get_deterministic_extraction(raw_text)
        evaluated = ConfidenceService.evaluate_field_confidences(mock_data["record_data"])
        mock_data["confidence_evaluation"] = evaluated
        return mock_data

    @classmethod
    async def _extract_with_gemini(cls, raw_text: str) -> Dict[str, Any]:
        prompt = f"""You are an expert Indian land deed digitization system.
Extract the following structured JSON fields from this land document text:
owner_name, father_husband_name, survey_number, khasra_number, khata_number, plot_number, village, tehsil, district, state, land_area (float in acres), land_classification, registration_number, registration_date, document_type.

Document text:
\"\"\"{raw_text[:4000]}\"\"\"

Return ONLY valid JSON matching these keys."""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        for model in ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-flash-latest"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["candidates"][0]["content"]["parts"][0]["text"]
                        clean_json = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                        parsed = json.loads(clean_json)
                        evaluated = ConfidenceService.evaluate_field_confidences(parsed)
                        return {
                            "record_data": parsed,
                            "average_confidence": evaluated["average_confidence"],
                            "confidence_evaluation": evaluated,
                            "source": f"Google Gemini ({model})"
                        }
            except Exception as ex:
                logger.warning(f"Gemini {model} async extraction error: {ex}")
        raise RuntimeError("All Gemini models failed")


    @classmethod
    async def _extract_with_openai(cls, raw_text: str) -> Dict[str, Any]:
        prompt = f"""You are an expert Indian land deed digitization system.
Extract the following structured JSON fields from this land document text:
owner_name, father_husband_name, survey_number, khasra_number, khata_number, plot_number, village, tehsil, district, state, land_area (float in acres), land_classification, registration_number, registration_date, document_type.

Document text:
\"\"\"{raw_text}\"\"\"

Return ONLY valid JSON matching these keys."""
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": "You are a precise land records extraction parser."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            evaluated = ConfidenceService.evaluate_field_confidences(parsed)
            return {
                "record_data": parsed,
                "average_confidence": evaluated["average_confidence"],
                "confidence_evaluation": evaluated,
                "source": f"OpenAI {settings.OPENAI_MODEL}"
            }
