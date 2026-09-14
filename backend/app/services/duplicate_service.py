from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.validation.duplicate_rules import DuplicateRulesEngine

class DuplicateService:
    @staticmethod
    def check_duplicate(
        survey_number: str,
        village: str,
        district: str,
        record_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Backward compatible check for parcel collisions."""
        return DuplicateRulesEngine.check_parcel_collision(
            survey_number=survey_number,
            village=village,
            district=district,
            current_record_id=record_id,
            db=db
        )

    @classmethod
    def analyze_record_duplicates(
        cls,
        data: Dict[str, Any],
        db: Session,
        current_record_id: Optional[int] = None,
        file_hash: Optional[str] = None,
        phash: Optional[str] = None,
        raw_text: Optional[str] = None,
        ocr_confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes all 8 statutory duplicate detection checks:
        1. SHA-256 exact document hash
        2. Registration number + state/district
        3. Survey number + village
        4. Owner + survey number
        5. Khasra + village + area
        6. Registration number + owner
        7. OCR text Jaccard similarity
        8. Perceptual image similarity (dHash / pHash)

        Returns composite risk score (0-100), risk breakdown, and risk level.
        Never automatically rejects; flags for officer review.
        """
        return DuplicateRulesEngine.analyze_duplicates(
            data=data,
            db=db,
            current_record_id=current_record_id,
            file_hash=file_hash,
            phash=phash,
            raw_text=raw_text,
            ocr_confidence=ocr_confidence
        )
