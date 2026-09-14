from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.models.land_record import LandRecord
from backend.app.ai.multilingual.normalizer import TextNormalizationService
from backend.app.ai.multilingual.transliteration_service import TransliterationService

class SearchService:
    @staticmethod
    def search_all_records(
        query_str: str,
        db: Session,
        include_internal: bool = False
    ) -> List[LandRecord]:
        if not query_str or not query_str.strip():
            return []

        raw_q = query_str.strip()
        # 1. Convert Indic numerals if any
        num_norm_q = TextNormalizationService.normalize_numerals(raw_q)
        # 2. Phonetic transliteration for Indian scripts to English
        translit_q = TransliterationService.transliterate_text(raw_q)

        search_terms = list({raw_q, num_norm_q, translit_q} - {"", None})

        q = db.query(LandRecord)
        if not include_internal:
            q = q.filter(LandRecord.is_public == True, LandRecord.status.in_(["APPROVED", "PUBLISHED", "USER_VERIFIED"]))

        conditions = []
        for term in search_terms:
            kw = f"%{term}%"
            conditions.extend([
                LandRecord.owner_name.ilike(kw),
                LandRecord.survey_number.ilike(kw),
                LandRecord.khasra_number.ilike(kw),
                LandRecord.khata_number.ilike(kw),
                LandRecord.registration_number.ilike(kw),
                LandRecord.village.ilike(kw),
                LandRecord.district.ilike(kw),
                LandRecord.state.ilike(kw)
            ])

        q = q.filter(or_(*conditions))
        return q.all()
