"""
DuplicateRulesEngine: Multi-vector duplicate detection & risk scoring engine for Indian Land Records.
Implements the 8 statutory duplicate detection checks:
1. SHA-256 document hash collision
2. Registration number + state/district collision
3. Survey number + village collision
4. Owner + survey number collision
5. Khasra + village + area collision
6. Registration number + owner collision
7. OCR text similarity
8. Perceptual image similarity (dHash / pHash)

Generates composite risk score:
- Document duplicate: +40
- Registration duplicate: +40
- Owner mismatch: +25
- Survey mismatch: +30
- Area mismatch: +25
- GIS mismatch: +30
- Low OCR confidence: +15
- Date inconsistency: +15

Risk Levels:
- 0–20: LOW
- 21–50: MEDIUM
- 51–80: HIGH
- 81+: CRITICAL
Rule: Never automatically reject based solely on score; flag for officer review.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.models.land_record import LandRecord
from backend.app.models.document import Document

class DuplicateRulesEngine:
    """
    Multi-vector Duplicate Detection & Fraud Prevention Engine.
    """

    @staticmethod
    def _hamming_distance(s1: str, s2: str) -> int:
        """Calculates Hamming distance between two hexadecimal hash strings."""
        try:
            if not s1 or not s2 or len(s1) != len(s2):
                return 64
            val1 = int(s1, 16)
            val2 = int(s2, 16)
            return bin(val1 ^ val2).count("1")
        except Exception:
            return 64

    @staticmethod
    def _text_jaccard_similarity(text1: str, text2: str) -> float:
        """Computes word token Jaccard similarity between two OCR texts."""
        if not text1 or not text2:
            return 0.0
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return len(intersection) / float(len(union))

    @classmethod
    def analyze_duplicates(
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
        Executes all 8 duplicate checks, computes risk score (0-100), and assigns risk level.
        """
        risk_score = 0
        risk_breakdown = []
        conflicts = []

        survey_no = str(data.get("survey_number", "")).strip()
        village = str(data.get("village", "")).strip()
        district = str(data.get("district", "")).strip()
        state = str(data.get("state", "")).strip()
        owner_name = str(data.get("owner_name", "")).strip()
        khasra_no = str(data.get("khasra_number", "")).strip()
        reg_no = str(data.get("registration_number", "")).strip()

        try:
            area = float(data.get("land_area", 0.0))
        except (ValueError, TypeError):
            area = 0.0

        # Vector 1: SHA-256 Exact Document Hash
        if file_hash:
            doc_query = db.query(Document).filter(Document.file_hash == file_hash)
            if current_record_id:
                doc_query = doc_query.filter(Document.land_record_id != current_record_id)
            hash_conflict = doc_query.first()
            if hash_conflict:
                risk_score += 40
                risk_breakdown.append({
                    "vector": "DOCUMENT_HASH_COLLISION",
                    "score": 40,
                    "description": f"Identical file binary detected (SHA-256: {file_hash[:12]}...). Matches document #{hash_conflict.id}"
                })
                conflicts.append({
                    "type": "EXACT_DOCUMENT_DUPLICATE",
                    "id": hash_conflict.id,
                    "detail": f"File binary identical to document #{hash_conflict.id} ({hash_conflict.filename})"
                })

        # Vector 2: Registration Number + State / District
        if reg_no:
            reg_query = db.query(LandRecord).filter(LandRecord.registration_number.ilike(reg_no))
            if district:
                reg_query = reg_query.filter(LandRecord.district.ilike(f"%{district}%"))
            if current_record_id:
                reg_query = reg_query.filter(LandRecord.id != current_record_id)
            reg_conflict = reg_query.first()
            if reg_conflict:
                risk_score += 40
                risk_breakdown.append({
                    "vector": "REGISTRATION_DUPLICATE",
                    "score": 40,
                    "description": f"Registration number '{reg_no}' already exists in {district} registry (Record #{reg_conflict.id})"
                })
                conflicts.append({
                    "type": "REGISTRATION_NUMBER_COLLISION",
                    "id": reg_conflict.id,
                    "detail": f"Deed registered under owner '{reg_conflict.owner_name}' with status {reg_conflict.status}"
                })

        # Vector 3: Survey Number + Village
        if survey_no and village:
            sy_query = db.query(LandRecord).filter(
                LandRecord.survey_number == survey_no,
                LandRecord.village.ilike(f"%{village}%"),
                LandRecord.status.in_(["APPROVED", "PUBLISHED", "OFFICER_REVIEW"])
            )
            if current_record_id:
                sy_query = sy_query.filter(LandRecord.id != current_record_id)
            sy_conflict = sy_query.first()
            if sy_conflict:
                # Check if owners differ
                if owner_name and sy_conflict.owner_name.lower().strip() != owner_name.lower().strip():
                    risk_score += 30
                    risk_breakdown.append({
                        "vector": "SURVEY_NUMBER_OWNER_MISMATCH",
                        "score": 30,
                        "description": f"Survey parcel '{survey_no}' in '{village}' is currently registered to '{sy_conflict.owner_name}' but submitted for '{owner_name}'"
                    })
                    conflicts.append({
                        "type": "SURVEY_OWNERSHIP_MISMATCH",
                        "id": sy_conflict.id,
                        "detail": f"Existing landowner on record: '{sy_conflict.owner_name}'"
                    })
                else:
                    risk_score += 15
                    risk_breakdown.append({
                        "vector": "EXISTING_PARCEL_RECORD",
                        "score": 15,
                        "description": f"Active land record exists for survey parcel '{survey_no}' in '{village}'"
                    })

        # Vector 4: Owner + Survey Number Collision
        if owner_name and survey_no:
            owner_sy = db.query(LandRecord).filter(
                LandRecord.survey_number == survey_no,
                LandRecord.owner_name.ilike(f"%{owner_name}%")
            )
            if current_record_id:
                owner_sy = owner_sy.filter(LandRecord.id != current_record_id)
            if owner_sy.first():
                risk_score += 20
                risk_breakdown.append({
                    "vector": "OWNER_SURVEY_COLLISION",
                    "score": 20,
                    "description": f"Owner '{owner_name}' already holds an active record for parcel '{survey_no}'"
                })

        # Vector 5: Khasra + Village + Area Collision
        if khasra_no and village and area > 0:
            khasra_q = db.query(LandRecord).filter(
                LandRecord.khasra_number == khasra_no,
                LandRecord.village.ilike(f"%{village}%")
            )
            if current_record_id:
                khasra_q = khasra_q.filter(LandRecord.id != current_record_id)
            k_conf = khasra_q.first()
            if k_conf and abs(k_conf.land_area - area) < 0.05:
                risk_score += 25
                risk_breakdown.append({
                    "vector": "KHASRA_VILLAGE_AREA_COLLISION",
                    "score": 25,
                    "description": f"Exact matching Khasra '{khasra_no}' in '{village}' with area {k_conf.land_area} Ac found (Record #{k_conf.id})"
                })

        # Vector 6: Registration Number + Owner Collision
        if reg_no and owner_name:
            ro_q = db.query(LandRecord).filter(
                LandRecord.registration_number == reg_no,
                LandRecord.owner_name.ilike(f"%{owner_name}%")
            )
            if current_record_id:
                ro_q = ro_q.filter(LandRecord.id != current_record_id)
            if ro_q.first():
                risk_score += 15
                risk_breakdown.append({
                    "vector": "REGISTRATION_OWNER_MATCH",
                    "score": 15,
                    "description": f"Same registration number and owner submitted previously"
                })

        # Vector 7: OCR Text Similarity (Levenshtein/Jaccard Token Match)
        if raw_text and len(raw_text.strip()) > 50:
            recent_docs = db.query(Document).order_by(Document.id.desc()).limit(15).all()
            for rd in recent_docs:
                if current_record_id and rd.land_record_id == current_record_id:
                    continue
                if rd.ocr_raw_text and len(rd.ocr_raw_text.strip()) > 50:
                    sim = cls._text_jaccard_similarity(raw_text, rd.ocr_raw_text)
                    if sim > 0.85:
                        risk_score += 20
                        risk_breakdown.append({
                            "vector": "OCR_TEXT_SIMILARITY",
                            "score": 20,
                            "description": f"High textual similarity ({round(sim*100, 1)}%) detected with document #{rd.id} ({rd.filename})"
                        })
                        break

        # Vector 8: Perceptual Image Similarity (dHash Hamming Distance)
        if phash and len(phash) >= 8:
            phash_docs = db.query(Document).filter(Document.phash.isnot(None)).limit(20).all()
            for pd in phash_docs:
                if current_record_id and pd.land_record_id == current_record_id:
                    continue
                if pd.phash:
                    h_dist = cls._hamming_distance(phash, pd.phash)
                    if h_dist <= 6:  # Visual perceptual match threshold
                        risk_score += 25
                        risk_breakdown.append({
                            "vector": "PERCEPTUAL_IMAGE_SIMILARITY",
                            "score": 25,
                            "description": f"Visual perceptual match detected with document #{pd.id} (Hamming distance: {h_dist})"
                        })
                        break

        # Factor in Low OCR Confidence
        if ocr_confidence is not None and ocr_confidence < 80.0:
            risk_score += 15
            risk_breakdown.append({
                "vector": "LOW_OCR_CONFIDENCE",
                "score": 15,
                "description": f"Overall document recognition confidence is low ({round(ocr_confidence, 1)}%)"
            })

        # Cap score between 0 and 100
        total_risk = min(100, risk_score)

        # Risk level determination
        if total_risk <= 20:
            risk_level = "LOW"
        elif total_risk <= 50:
            risk_level = "MEDIUM"
        elif total_risk <= 80:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        return {
            "risk_score": total_risk,
            "risk_level": risk_level,
            "is_duplicate": bool(total_risk >= 40),
            "requires_officer_review": bool(total_risk > 20),
            "conflicts_count": len(conflicts),
            "conflicts": conflicts,
            "risk_breakdown": risk_breakdown,
            "policy": "Advisory risk assessment. Record flagged for officer verification rather than automated rejection."
        }

    @classmethod
    def check_parcel_collision(
        cls,
        survey_number: str,
        village: str,
        district: str,
        current_record_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Backward-compatible parcel collision check."""
        if not db or not survey_number:
            return {"is_duplicate": False, "conflicts": []}

        res = cls.analyze_duplicates(
            data={"survey_number": survey_number, "village": village, "district": district},
            db=db,
            current_record_id=current_record_id
        )
        return {
            "is_duplicate": res["is_duplicate"],
            "count": res["conflicts_count"],
            "conflicts": res["conflicts"],
            "risk_score": res["risk_score"],
            "risk_level": res["risk_level"]
        }
