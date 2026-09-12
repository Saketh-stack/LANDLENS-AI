from typing import Dict, Any

class MockAIService:
    SAMPLE_RECORDS = [
        {
            "owner_name": "Ravi Kumar",
            "father_husband_name": "Anand Kumar",
            "survey_number": "123/4A",
            "khasra_number": "KHA-7796",
            "khata_number": "KH-27159",
            "plot_number": "PLOT-63",
            "village": "Rampur Kalan",
            "tehsil": "Huzur",
            "district": "Bhopal",
            "state": "Madhya Pradesh",
            "land_area": 2.45,
            "land_classification": "Agricultural",
            "registration_number": "REG2026/00735",
            "registration_date": "11-09-2026",
            "document_type": "Sale Deed"
        }
    ]

    @classmethod
    def get_deterministic_extraction(cls, text_seed: str = "") -> Dict[str, Any]:
        rec = cls.SAMPLE_RECORDS[0].copy()
        boxes = {
            "owner_name": {"x": 180, "y": 220, "w": 280, "h": 40, "page": 1},
            "father_husband_name": {"x": 180, "y": 270, "w": 260, "h": 35, "page": 1},
            "survey_number": {"x": 480, "y": 220, "w": 160, "h": 40, "page": 1},
            "khasra_number": {"x": 480, "y": 270, "w": 160, "h": 35, "page": 1},
            "village": {"x": 180, "y": 340, "w": 220, "h": 35, "page": 1},
            "tehsil": {"x": 420, "y": 340, "w": 180, "h": 35, "page": 1},
            "district": {"x": 620, "y": 340, "w": 160, "h": 35, "page": 1},
            "land_area": {"x": 180, "y": 410, "w": 200, "h": 40, "page": 1},
            "registration_number": {"x": 520, "y": 80, "w": 240, "h": 40, "page": 1},
            "registration_date": {"x": 520, "y": 130, "w": 200, "h": 35, "page": 1}
        }
        return {
            "record_data": rec,
            "bounding_boxes": boxes,
            "average_confidence": 93.8,
            "extracted_language": "English / Hindi",
            "source": "Deterministic Mock AI Engine (DoLR Tested)"
        }
