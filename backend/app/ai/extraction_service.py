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
        if settings.MOCK_MODE or not settings.is_llm_enabled:
            data = MockAIService.get_deterministic_extraction(raw_text)
            eval_res = ConfidenceService.evaluate_field_confidences(data["record_data"])
            data["confidence_evaluation"] = eval_res
            data["average_confidence"] = eval_res["average_confidence"]
            return data

        from backend.app.ai.multilingual.extraction_service import LandFieldExtractionService
        return await LandFieldExtractionService.extract_structured_record(raw_text)

    @classmethod
    def extract_fields_sync(cls, raw_text: str) -> Dict[str, Any]:
        if settings.MOCK_MODE or not settings.is_llm_enabled:
            data = MockAIService.get_deterministic_extraction(raw_text)
            eval_res = ConfidenceService.evaluate_field_confidences(data["record_data"])
            data["confidence_evaluation"] = eval_res
            data["average_confidence"] = eval_res["average_confidence"]
            return data

        from backend.app.ai.multilingual.extraction_service import LandFieldExtractionService
        return LandFieldExtractionService.extract_structured_record_sync(raw_text)

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
    async def _extract_with_openrouter(cls, raw_text: str) -> Dict[str, Any]:
        prompt = f"""You are an expert Indian land deed digitization system.
Extract the following structured JSON fields from this land document text:
owner_name, father_husband_name, survey_number, khasra_number, khata_number, plot_number, village, tehsil, district, state, land_area (float in acres), land_classification, registration_number, registration_date, document_type.

Document text:
\"\"\"{raw_text[:4000]}\"\"\"

Return ONLY valid JSON matching these keys."""
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://sih26018-smart-land-records.gov.in",
            "X-Title": "SIH Smart Land Records Digitization",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": "You are a precise land records extraction parser. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 1500
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload)
            if resp.status_code == 400 and ("response_format" in resp.text or "unsupported" in resp.text.lower()):
                payload.pop("response_format", None)
                resp = await client.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            clean_json = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            if "{" in clean_json and "}" in clean_json:
                start = clean_json.find("{")
                end = clean_json.rfind("}") + 1
                clean_json = clean_json[start:end]
            parsed = json.loads(clean_json)
            evaluated = ConfidenceService.evaluate_field_confidences(parsed)
            return {
                "record_data": parsed,
                "average_confidence": evaluated["average_confidence"],
                "confidence_evaluation": evaluated,
                "source": f"OpenRouter ({settings.OPENROUTER_MODEL})"
            }

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
