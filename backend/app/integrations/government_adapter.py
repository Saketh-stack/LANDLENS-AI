from typing import Dict, Any, Optional

class GovernmentStateAdapter:
    """
    Pan-India State Revenue Terminology & Rules Adapter.
    Translates state-specific administrative naming conventions:
    - MP/UP: Khasra, Khatauni, Tehsil, Bigha/Acres
    - AP/Telangana: Survey No, Passbook/Pattadar, Mandal, Guntha/Acres
    - Maharashtra: 7/12 (Saat-Baara), Gut No, Taluka, Guntha
    - Tamil Nadu: Patta/Chitta, Survey No, Taluk, Cents/Acres
    - Karnataka: RTC (Pahani), Survey/Hissa, Hobli/Taluka, Guntas
    """
    STATE_PROFILES: Dict[str, Dict[str, str]] = {
        "Andhra Pradesh": {
            "survey_label": "Survey Number",
            "ror_label": "1-B Record of Rights / Pattadar Passbook",
            "admin_unit": "Mandal",
            "area_unit": "Acres / Cents",
            "language": "Telugu / English"
        },
        "Telangana": {
            "survey_label": "Survey Number",
            "ror_label": "Dharani Pattadar Passbook",
            "admin_unit": "Mandal",
            "area_unit": "Acres / Guntas",
            "language": "Telugu / English"
        },
        "Madhya Pradesh": {
            "survey_label": "Khasra Number",
            "ror_label": "Khasra Khatauni (Bhu-Abhilekh)",
            "admin_unit": "Tehsil",
            "area_unit": "Acres / Hectares",
            "language": "Hindi"
        },
        "Uttar Pradesh": {
            "survey_label": "Khasra / Gata Number",
            "ror_label": "Khatauni (Bhulekh)",
            "admin_unit": "Tehsil",
            "area_unit": "Hectares / Bigha",
            "language": "Hindi"
        },
        "Maharashtra": {
            "survey_label": "Survey No / Gut No",
            "ror_label": "7/12 Extract (Mahabhulekh)",
            "admin_unit": "Taluka",
            "area_unit": "Hectares / Guntha",
            "language": "Marathi / English"
        },
        "Tamil Nadu": {
            "survey_label": "Survey Number / Sub-Division",
            "ror_label": "Patta / Chitta (AnyROR)",
            "admin_unit": "Taluk",
            "area_unit": "Acres / Cents",
            "language": "Tamil / English"
        },
        "Karnataka": {
            "survey_label": "Survey No / Hissa",
            "ror_label": "RTC / Pahani (Bhoomi)",
            "admin_unit": "Taluk / Hobli",
            "area_unit": "Acres / Guntas",
            "language": "Kannada / English"
        },
        "West Bengal": {
            "survey_label": "Dag Number",
            "ror_label": "Banglarbhumi Khatian",
            "admin_unit": "Block",
            "area_unit": "Acres / Decimals",
            "language": "Bengali / English"
        },
        "Gujarat": {
            "survey_label": "Survey Number",
            "ror_label": "AnyRoR 7/12 & 8A",
            "admin_unit": "Taluka",
            "area_unit": "Hectares / Guntha",
            "language": "Gujarati / English"
        },
        "Kerala": {
            "survey_label": "Resurvey Number / Tandaper",
            "ror_label": "e-Rekhakal RoR",
            "admin_unit": "Taluk",
            "area_unit": "Hectares / Ares",
            "language": "Malayalam / English"
        }
    }

    @classmethod
    def get_state_profile(cls, state_name: str) -> Dict[str, str]:
        return cls.STATE_PROFILES.get(state_name, {
            "survey_label": "Survey Number",
            "ror_label": "Record of Rights (RoR)",
            "admin_unit": "Tehsil / Taluka",
            "area_unit": "Acres",
            "language": "English / Regional"
        })
