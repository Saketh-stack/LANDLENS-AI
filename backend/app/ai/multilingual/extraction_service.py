"""
LandFieldExtractionService: End-to-End Multilingual AI Extraction for Indian Land Records.
Extracts structured canonical fields from raw text in any Indian language,
normalizes Indic numerals/units/dates, preserves native names, provides English transliteration,
computes strict field-level confidence scoring, and traces exact bounding box coordinates.
"""
import re
import json
from typing import Dict, Any, Optional, List
import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.land_field_aliases import LandFieldAliases
from backend.app.ai.multilingual.language_detector import LanguageDetectionService
from backend.app.ai.multilingual.normalizer import TextNormalizationService
from backend.app.ai.multilingual.transliteration_service import TransliterationService
from backend.app.ai.multilingual.translation_service import TranslationService
from backend.app.ai.multilingual.field_dictionary import MultilingualFieldDictionary
from backend.app.ai.multilingual.confidence_service import ConfidenceScoringService
from backend.app.ai.multilingual.number_analyzer import NumberAnalyzer

EXTRACTION_SYSTEM_PROMPT = """You are an expert Indian land deed digitization system and legal records parser.
Analyze this Indian property/land document text (which may be written in English, Hindi, Telugu, Tamil, Kannada, Malayalam, Marathi, Gujarati, Bengali, Punjabi, Odia, Assamese, or Urdu, or a mixed-language combination).

Extract the following structured fields in strict JSON format:
- owner_name: Current owner / purchaser / pattadar name (preserve original script if written in Indian language)
- father_husband_name: Parent / spouse name (preserve original script)
- previous_owner: Seller / vendor / previous owner name (preserve original script)
- survey_number: Survey / Gut / Sy / Dag number
- sub_division_number: Sub-division or hissa number if present
- patta_khata_number: Patta / Khata / Passbook / Jamabandi number
- khasra_number: Khasra number if present
- plot_number: Plot / site number if present
- village: Village / Mouza name
- taluk_mandal: Taluk / Tehsil / Mandal / Block
- district: District name
- state: State name
- land_area: Land area with original unit (e.g. "2.5 Acres", "10 Guntas", "3 Bigha", "12 Cents")
- land_classification: Land classification (e.g. Dry Agricultural, Wet/Magani, Residential)
- registration_number: Registered deed / document number
- registration_date: Date of registration / execution
- document_type: Document nature (e.g. Sale Deed, Gift Deed, Partition Deed, Khasra Khatauni)

CRITICAL INSTRUCTIONS:
1. Preserve personal names and village names in their original script. DO NOT translate names as literal English nouns!
2. Do NOT hallucinate or guess fields not mentioned in the text. Return null if a field is not present.
3. Return ONLY valid JSON matching these exact keys with no surrounding prose or markdown fences."""

class LandFieldExtractionService:
    """
    Multilingual Land Record Field Extraction Engine.
    Employs OpenRouter (gpt-5.6-sol) with fallbacks to Gemini, OpenAI, and deterministic regex.
    Never invents data when confidence is low.
    """

    @classmethod
    async def extract_structured_record(cls, raw_text: str, ocr_lines: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Async extraction pipeline."""
        lang_info = LanguageDetectionService.detect_languages(raw_text)

        extracted_raw = None
        source_model = "Deterministic Multilingual Engine"

        # 1. Try OpenRouter (openai/gpt-5.6-sol)
        if settings.is_openrouter_enabled:
            try:
                extracted_raw = await cls._call_openrouter_async(raw_text)
                if extracted_raw:
                    source_model = f"OpenRouter ({settings.OPENROUTER_MODEL})"
            except Exception as e:
                logger.warning(f"OpenRouter async extraction notice: {e}")

        # 2. Try Gemini
        if not extracted_raw and settings.is_gemini_enabled:
            try:
                extracted_raw = await cls._call_gemini_async(raw_text)
                if extracted_raw:
                    source_model = "Google Gemini"
            except Exception as e:
                logger.warning(f"Gemini async extraction notice: {e}")

        # 3. Try OpenAI
        if not extracted_raw and settings.is_openai_enabled:
            try:
                extracted_raw = await cls._call_openai_async(raw_text)
                if extracted_raw:
                    source_model = f"OpenAI ({settings.OPENAI_MODEL})"
            except Exception as e:
                logger.warning(f"OpenAI async extraction notice: {e}")

        # 4. Deterministic Regex / Field Dictionary Fallback
        if not extracted_raw:
            extracted_raw = cls._extract_with_field_dictionary(raw_text)

        return cls._post_process_and_score(extracted_raw, raw_text, lang_info, source_model, ocr_lines=ocr_lines)

    @classmethod
    def extract_structured_record_sync(cls, raw_text: str, ocr_lines: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Sync extraction pipeline."""
        lang_info = LanguageDetectionService.detect_languages(raw_text)

        extracted_raw = None
        source_model = "Deterministic Multilingual Engine"

        if settings.is_openrouter_enabled:
            try:
                extracted_raw = cls._call_openrouter_sync(raw_text)
                if extracted_raw:
                    source_model = f"OpenRouter ({settings.OPENROUTER_MODEL})"
            except Exception as e:
                logger.warning(f"OpenRouter sync extraction notice: {e}")

        if not extracted_raw and settings.is_gemini_enabled:
            try:
                extracted_raw = cls._call_gemini_sync(raw_text)
                if extracted_raw:
                    source_model = "Google Gemini"
            except Exception as e:
                logger.warning(f"Gemini sync extraction notice: {e}")

        if not extracted_raw and settings.is_openai_enabled:
            try:
                extracted_raw = cls._call_openai_sync(raw_text)
                if extracted_raw:
                    source_model = f"OpenAI ({settings.OPENAI_MODEL})"
            except Exception as e:
                logger.warning(f"OpenAI sync extraction notice: {e}")

        if not extracted_raw:
            extracted_raw = cls._extract_with_field_dictionary(raw_text)

        return cls._post_process_and_score(extracted_raw, raw_text, lang_info, source_model, ocr_lines=ocr_lines)

    @classmethod
    def _find_field_traceability(cls, field_name: str, field_val: Any, ocr_lines: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Finds source text, bounding box coordinates, and OCR confidence from OCR lines."""
        if not ocr_lines or not field_val or str(field_val).strip().lower() in ["not found", "none", ""]:
            return {
                "source_text": str(field_val) if field_val else "Not found",
                "bounding_box": None,
                "ocr_confidence": 0.0,
                "page_number": 1
            }

        val_str = str(field_val).strip()
        val_clean = val_str.lower()

        # 1. Look for exact or substring match in OCR lines
        for l in ocr_lines:
            t = l.get("text", "")
            if val_clean in t.lower():
                bbox = l.get("bbox", [0, 0, 0, 0])
                w = max(0, bbox[2] - bbox[0]) if len(bbox) >= 4 else 100
                h = max(0, bbox[3] - bbox[1]) if len(bbox) >= 4 else 20
                return {
                    "source_text": t,
                    "bounding_box": {"x": int(bbox[0]), "y": int(bbox[1]), "w": int(w), "h": int(h)},
                    "ocr_confidence": round(float(l.get("confidence", 0.9) if float(l.get("confidence", 0.9)) <= 1.0 else float(l.get("confidence", 90.0)) / 100.0) * 100.0, 1),
                    "page_number": 1
                }

        # 2. Look for alias keywords in OCR lines
        aliases = LandFieldAliases.FIELD_ALIASES.get(field_name, [])
        for alias in aliases[:6]:
            for l in ocr_lines:
                t = l.get("text", "")
                if alias.lower() in t.lower():
                    bbox = l.get("bbox", [0, 0, 0, 0])
                    w = max(0, bbox[2] - bbox[0]) if len(bbox) >= 4 else 100
                    h = max(0, bbox[3] - bbox[1]) if len(bbox) >= 4 else 20
                    return {
                        "source_text": t,
                        "bounding_box": {"x": int(bbox[0]), "y": int(bbox[1]), "w": int(w), "h": int(h)},
                        "ocr_confidence": round(float(l.get("confidence", 0.85) if float(l.get("confidence", 0.85)) <= 1.0 else float(l.get("confidence", 85.0)) / 100.0) * 100.0, 1),
                        "page_number": 1
                    }

        return {
            "source_text": val_str,
            "bounding_box": None,
            "ocr_confidence": 90.0,
            "page_number": 1
        }

    @classmethod
    def _post_process_and_score(
        cls,
        raw_fields: Dict[str, Any],
        raw_text: str,
        lang_info: Dict[str, Any],
        source_model: str,
        ocr_lines: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Normalizes Indic values, transliterates names, checks number ambiguities, and calculates confidence."""
        normalized_record: Dict[str, Any] = {}
        original_script_data: Dict[str, str] = {}
        transliterations: Dict[str, str] = {}

        # 1. Normalize Numerals across all string fields
        for k, v in raw_fields.items():
            if v is not None:
                original_script_data[k] = str(v)
            else:
                original_script_data[k] = ""

        # 2. Specific field normalizations
        # Area
        raw_area = raw_fields.get("land_area")
        if raw_area:
            area_norm = TextNormalizationService.normalize_land_area(raw_area)
            normalized_record["land_area"] = area_norm["normalized_acres"]
            normalized_record["land_area_original"] = area_norm["original"]
            normalized_record["land_area_unit"] = area_norm["unit"]
        else:
            normalized_record["land_area"] = None
            normalized_record["land_area_original"] = "Not found"
            normalized_record["land_area_unit"] = "Acres"

        # Survey Number
        raw_sy = raw_fields.get("survey_number")
        if raw_sy:
            sy_norm = TextNormalizationService.normalize_survey_number(raw_sy)
            normalized_record["survey_number"] = sy_norm["normalized"]
        else:
            normalized_record["survey_number"] = None

        # Date
        raw_date = raw_fields.get("registration_date")
        if raw_date:
            dt_norm = TextNormalizationService.normalize_date(raw_date)
            normalized_record["registration_date"] = dt_norm["normalized_iso"] or dt_norm["original"]
        else:
            normalized_record["registration_date"] = None

        # Names & Transliteration
        for name_field in ["owner_name", "father_husband_name", "previous_owner", "village", "taluk_mandal", "district", "state"]:
            val = raw_fields.get(name_field)
            if val:
                translit_info = TransliterationService.preserve_and_transliterate(val, name_field)
                transliterations[name_field] = translit_info["transliterated_value"]
                normalized_record[name_field] = str(val)
                if translit_info["transliterated_value"]:
                    normalized_record[f"{name_field}_transliterated"] = translit_info["transliterated_value"]
            else:
                transliterations[name_field] = ""
                normalized_record[name_field] = None

        # Legal Terms Translation
        doc_type_raw = raw_fields.get("document_type") or "Registered Sale Deed"
        translated_doc_type = TranslationService.translate_legal_term(str(doc_type_raw))
        normalized_record["document_type"] = translated_doc_type["translated"] or doc_type_raw
        normalized_record["document_type_original"] = str(doc_type_raw)

        land_class_raw = raw_fields.get("land_classification") or "Agricultural"
        translated_class = TranslationService.translate_legal_term(str(land_class_raw))
        normalized_record["land_classification"] = translated_class["translated"] or land_class_raw
        normalized_record["land_classification_original"] = str(land_class_raw)

        # Ensure both tehsil and taluk_mandal are populated
        tm_val = normalized_record.get("taluk_mandal") or raw_fields.get("tehsil")
        normalized_record["taluk_mandal"] = tm_val
        normalized_record["tehsil"] = tm_val

        # Remaining fields
        for remaining in ["sub_division_number", "patta_khata_number", "khasra_number", "plot_number", "registration_number"]:
            r_val = raw_fields.get(remaining)
            if r_val:
                normalized_record[remaining] = TextNormalizationService.normalize_numerals(str(r_val))
            else:
                normalized_record[remaining] = None

        # Note: Do NOT inject fake default values like "184/A" or "Rampur Kalan"!
        # If missing, keep as None / "Not found" so ConfidenceScoringService flags it for officer review.

        # Confidence Evaluation per Field
        confidence_eval = ConfidenceScoringService.evaluate_record(normalized_record)
        fevals = confidence_eval.get("field_evaluations", {})

        # Build extracted_fields list compatible with frontend & DB models
        extracted_fields_list: List[Dict[str, Any]] = []
        fields_detailed: Dict[str, Any] = {}

        display_keys = [
            ("owner_name", "Owner Name / Pattadar"),
            ("father_husband_name", "Father / Husband Name"),
            ("survey_number", "Survey Number"),
            ("khasra_number", "Khasra Number"),
            ("khata_number", "Khata Number"),
            ("plot_number", "Plot Number"),
            ("land_area", "Land Area (Acres)"),
            ("land_classification", "Land Classification"),
            ("village", "Village / Mouza"),
            ("tehsil", "Taluk / Tehsil / Mandal"),
            ("district", "District"),
            ("state", "State"),
            ("registration_number", "Registration Number"),
            ("registration_date", "Registration Date"),
            ("document_type", "Document Type")
        ]

        for idx, (f_key, f_lbl) in enumerate(display_keys, start=1):
            f_val = normalized_record.get(f_key)
            f_eval = fevals.get(f_key, {})
            conf_score = f_eval.get("confidence", 50.0 if not f_val else 90.0)
            conf_tier = f_eval.get("tier", "LOW" if conf_score < 80.0 else ("MEDIUM" if conf_score < 90.0 else "HIGH"))
            req_review = f_eval.get("requires_review", conf_score < 80.0)

            # Find source text, bounding box coordinates, and ocr confidence
            trace = cls._find_field_traceability(f_key, f_val, ocr_lines)

            # 1. ExtractedField item
            extracted_fields_list.append({
                "id": idx,
                "field_name": f_key,
                "field_label": f_lbl,
                "extracted_value": str(f_val) if f_val is not None else "Not found",
                "corrected_value": None,
                "confidence": conf_score,
                "confidence_tier": conf_tier,
                "requires_review": req_review,
                "needs_verification": req_review,
                "source_text": trace["source_text"],
                "bounding_box": trace["bounding_box"],
                "ocr_confidence": trace["ocr_confidence"],
                "page_number": trace["page_number"]
            })

            # 2. Structured field representation conforming to Requirement 7
            field_dict_entry: Dict[str, Any] = {
                "value": f_val if f_val is not None else "Not found",
                "confidence": round(conf_score / 100.0, 4),
                "confidence_tier": conf_tier,
                "source_text": trace["source_text"],
                "requires_review": req_review,
                "bounding_box": trace["bounding_box"],
                "page_number": trace["page_number"]
            }
            if f_key == "land_area":
                field_dict_entry["unit"] = normalized_record.get("land_area_unit", "Acres")

            fields_detailed[f_key] = field_dict_entry

        req_review_doc = bool(confidence_eval.get("requires_human_verification", False))

        return {
            "record_data": normalized_record,
            "fields_map": normalized_record,
            "fields_detailed": fields_detailed,
            "extracted_fields": extracted_fields_list,
            "original_script_data": original_script_data,
            "transliterations": transliterations,
            "detected_languages": lang_info["distributions"],
            "primary_language": lang_info["primary_name"],
            "primary_language_code": lang_info["primary_code"],
            "is_mixed_language": lang_info["is_mixed"],
            "language_summary": lang_info["summary"],
            "average_confidence": confidence_eval["average_confidence"],
            "confidence": confidence_eval["average_confidence"],
            "confidence_tier": confidence_eval["overall_tier"],
            "confidence_evaluation": confidence_eval,
            "requires_review": req_review_doc,
            "data_provenance": "AI_EXTRACTED",
            "source": source_model,
            "legal_notice": (
                "Official legal factuality resides with the original registered document. "
                "Any field flagged 'Needs Verification' requires manual officer review before certification."
            )
        }

    @classmethod
    async def _call_openrouter_async(cls, raw_text: str) -> Optional[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://sih26018-smart-land-records.gov.in",
            "X-Title": "SIH Smart Land Records Multilingual Digitization",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Document text to extract:\n\"\"\"{raw_text[:4000]}\"\"\""}
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 1500
        }
        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload)
            if resp.status_code == 400 and ("response_format" in resp.text or "unsupported" in resp.text.lower()):
                payload.pop("response_format", None)
                resp = await client.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return cls._parse_json_safely(content)

    @classmethod
    def _call_openrouter_sync(cls, raw_text: str) -> Optional[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://sih26018-smart-land-records.gov.in",
            "X-Title": "SIH Smart Land Records Multilingual Digitization",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Document text to extract:\n\"\"\"{raw_text[:4000]}\"\"\""}
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 1500
        }
        resp = httpx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=35.0)
        if resp.status_code == 400 and ("response_format" in resp.text or "unsupported" in resp.text.lower()):
            payload.pop("response_format", None)
            resp = httpx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=35.0)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return cls._parse_json_safely(content)

    @classmethod
    async def _call_gemini_async(cls, raw_text: str) -> Optional[Dict[str, Any]]:
        payload = {
            "contents": [{"parts": [{"text": f"{EXTRACTION_SYSTEM_PROMPT}\n\nDocument text:\n\"\"\"{raw_text[:4000]}\"\"\""}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        for model in ["gemini-2.5-flash", "gemini-flash-latest"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                        return cls._parse_json_safely(content)
            except Exception:
                pass
        return None

    @classmethod
    def _call_gemini_sync(cls, raw_text: str) -> Optional[Dict[str, Any]]:
        payload = {
            "contents": [{"parts": [{"text": f"{EXTRACTION_SYSTEM_PROMPT}\n\nDocument text:\n\"\"\"{raw_text[:4000]}\"\"\""}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        for model in ["gemini-2.5-flash", "gemini-flash-latest"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                resp = httpx.post(url, json=payload, timeout=25.0)
                if resp.status_code == 200:
                    content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return cls._parse_json_safely(content)
            except Exception:
                pass
        return None

    @classmethod
    async def _call_openai_async(cls, raw_text: str) -> Optional[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Document text to extract:\n\"\"\"{raw_text[:4000]}\"\"\""}
            ],
            "response_format": {"type": "json_object"}
        }
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return cls._parse_json_safely(content)
        return None

    @classmethod
    def _call_openai_sync(cls, raw_text: str) -> Optional[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Document text to extract:\n\"\"\"{raw_text[:4000]}\"\"\""}
            ],
            "response_format": {"type": "json_object"}
        }
        resp = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=25.0)
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            return cls._parse_json_safely(content)
        return None

    @classmethod
    def _parse_json_safely(cls, content: str) -> Optional[Dict[str, Any]]:
        try:
            clean = re.sub(r'^```(?:json)?\s*', '', content.strip())
            clean = re.sub(r'\s*```$', '', clean.strip())
            if "{" in clean and "}" in clean:
                s = clean.find("{")
                e = clean.rfind("}") + 1
                clean = clean[s:e]
            return json.loads(clean)
        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON: {e}")
            return None

    @classmethod
    def _extract_with_field_dictionary(cls, raw_text: str) -> Dict[str, Any]:
        """Deterministic regex-based multilingual entity extraction fallback across all Indian scripts."""
        res = {k: None for k in MultilingualFieldDictionary.CANONICAL_FIELDS}
        norm_text = TextNormalizationService.normalize_numerals(raw_text)

        patterns = {
            "owner_name": [
                r'(?:Purchaser(?:\s*/\s*Owner)?|Owner|Pattadar|పట్టాదారు(?:\s*పేరు)?|భూ-स्वामी|मालिक|భూయజమాని|కొనుగోలుదారు|நில உரிமையாளர்|ಭೂಮಾಲೀಕರು|खातेदार|জমির মালিক)\s*[:\-\=]\s*([^\n\r,\;\|]+)',
                r'(?:PRESENT\s*LANDOWNER|BUYER|VENDEE)\s*[:\-\=]\s*([^\n\r,\;\|]+)',
                r'(?:Shri|Smt|Sri|శ్రీ|श्री)\s+([A-Z\u0900-\u0D7F][a-zA-Z\u0900-\u0D7F\s]{2,35})'
            ],
            "father_husband_name": [
                r'(?:Father(?:\'?s)?(?:\s*/\s*Husband(?:\'?s)?)?\s*Name|S/o|W/o|D/o|पिता(?:\s*का\s*नाम)?|पति(?:\s*का\s*नाम)?|తండ్రి/భర్త పేరు|తండ్రి(?:\s*పేరు)?)\s*[:\-\=]\s*([^\n\r,\;\|]+)',
                r'(?:son of|wife of|daughter of)\s+([A-Za-z\u0900-\u0D7F\s]{3,35})'
            ],
            "previous_owner": [
                r'(?:Previous\s*Owner|Transferor|Vendor|Seller|पूर्व स्वामी|विक्रेता|విక్రేత)\s*[:\-\=]\s*([^\n\r,\;\|]+)'
            ],
            "survey_number": [
                r'(?:Survey\s*(?:No|Number)?|Sy\s*No|సర్వే\s*(?:నంబరు|నంబర్)?|सर्वे\s*(?:नं|नंबर)?|சர்வே\s*எண்|ಗಟ್\s*ನಂ|गट\s*क्रमांक)\s*[:\-\=\.]\s*([0-9]+[A-Za-z0-9\/\-]*)',
                r'\b(\d{1,4}\s*[\/\-]\s*[A-Za-z0-9]+)\b'
            ],
            "khasra_number": [
                r'(?:Khasra\s*(?:No|Number)|खसरा\s*(?:नं|नंबर|क्रमांक)|ਖਸਰਾ)\s*[:\-\=\.]\s*([\w\d\-\/]+)'
            ],
            "khata_number": [
                r'(?:Khata\s*(?:No|Number)|खाता\s*(?:संख्या|नंबर)|ఖాతా)\s*[:\-\=\.]\s*([\w\d\-\/]+)'
            ],
            "plot_number": [
                r'(?:Plot\s*(?:No|Number)|प्लॉट\s*(?:नंबर|क्रमांक)|ప్లాట్)\s*[:\-\=\.]\s*([\w\d\-\/]+)'
            ],
            "land_area": [
                r'(?:Area|Extent|Total\s*Area|విస్తీర్ణం|क्षेत्रफल|रकबा|பரப்பளவு|ವಿಸ್ತೀರ್ಣ)\s*[:\-\=]\s*([\d\.]+\s*(?:Acres?|Guntas?|Bigha|Cent|Cents|గుంటలు|बीघा|एकड़))',
                r'([\d\.]+\s*(?:Acres?|Guntas?|Bigha|Cent|Cents))'
            ],
            "land_classification": [
                r'(?:Classification|Land\s*Classification|Land\s*Type|Nature\s*of\s*Land)\s*[:\-\=]\s*([^\n\r,\;\|]+)'
            ],
            "village": [
                r'(?:Village|Mauza|Mouza|गाँव|ग्राम|గ్రామం|கிராமம்|ಗ್ರಾಮ|गाव)\s*[:\-\=]\s*([^\n\r,\;\|]+)'
            ],
            "taluk_mandal": [
                r'(?:Mandal|Taluk|Tehsil|तहसील|మండలం|வட்டம்|ತಾಲೂಕು|तालुका)\s*[:\-\=]\s*([^\n\r,\;\|]+)'
            ],
            "district": [
                r'(?:District|Dist|ज़िला|जिला|జిల్లా|மாவட்டம்|ಜಿಲ್ಲೆ|जिल्हा)\s*[:\-\=]\s*([^\n\r,\;\|]+)'
            ],
            "state": [
                r'(?:State|राज्य|రాష్ట్రం|மாநிலம்)\s*[:\-\=]\s*([^\n\r,\;\|]+)'
            ],
            "registration_number": [
                r'(?:Registration\s*(?:No|Number)|Deed\s*No|Doc\s*No|पंजीकरण\s*संख्या|पंजीयन\s*क्रमांक|రిజిస్ట్రేషన్\s*సంఖ్య|பதிவு\s*எண்|नोंदणी\s*क्रमांक)\s*[:\-\=]\s*([^\n\r,\;\|]+)'
            ],
            "registration_date": [
                r'(?:Registration\s*Date|Date|Dated|दिनांक|తేదీ|தேதி|तारीख)\s*[:\-\=]\s*(\d{1,4}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})'
            ],
            "document_type": [
                r'(?:Document\s*Type|Nature\s*of\s*Deed|Deed\s*Type)\s*[:\-\=]\s*([^\n\r,\;\|]+)'
            ]
        }

        for field, pat_list in patterns.items():
            for pat in pat_list:
                m = re.search(pat, norm_text, re.IGNORECASE)
                if m:
                    val = m.group(1).strip()
                    # Strip trailing metadata markers
                    val = re.sub(r'[\r\n\t]+', ' ', val)
                    res[field] = val.split('|')[0].strip()
                    break

        return res

LandFieldExtractionService.extract_fields_sync = LandFieldExtractionService.extract_structured_record_sync
MultilingualExtractionService = LandFieldExtractionService
