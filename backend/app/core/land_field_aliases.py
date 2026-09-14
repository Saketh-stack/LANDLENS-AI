"""
LandFieldAliases: Central, configurable land record field terminology registry
covering state-specific nomenclature across India (Telangana, MP, UP, Maharashtra,
Tamil Nadu, Karnataka, Andhra Pradesh, West Bengal, Punjab, etc.).
"""
from typing import Dict, List, Any, Optional

class LandFieldAliases:
    """
    Configurable alias registry for land-record fields across Indian States.
    Maps localized and regional keywords to canonical land record entities.
    """

    CANONICAL_FIELDS = [
        "owner_name",
        "father_husband_name",
        "survey_number",
        "khasra_number",
        "khata_number",
        "khatauni_number",
        "plot_number",
        "dag_number",
        "patta_number",
        "sub_division_number",
        "land_area",
        "area_unit",
        "village",
        "tehsil",
        "taluk",
        "mandal",
        "district",
        "state",
        "registration_number",
        "registration_date",
        "mutation_number",
        "mutation_date",
        "previous_owner",
        "current_owner",
        "land_classification",
        "ownership_type",
        "document_number",
        "parcel_number"
    ]

    # Aliases mapping canonical field -> list of variants across English & regional terms
    FIELD_ALIASES: Dict[str, List[str]] = {
        "owner_name": [
            "owner name", "owner", "purchaser", "vendee", "pattadar", "landowner", "present owner",
            "khatedar", "buyer", "transferee", "holder", "भू-स्वामी", "मालिक", "खातेदार", "భూయజమాని",
            "కొనుగోలుదారు", "பட்டாதாரர்", "நில உரிமையாளர்", "ಭೂಮಾಲೀಕರು", "জমির মালিক", "ਜ਼ਮੀਨ ਮਾਲਕ", "مالک زمین"
        ],
        "father_husband_name": [
            "father name", "husband name", "parent name", "guardian", "s/o", "w/o", "d/o", "c/o",
            "father/husband", "पिता का नाम", "पति का नाम", "తండ్రి/భర్త పేరు", "தந்தை/கணவர் பெயர்", "ತಂದೆ/ಗಂಡನ ಹೆಸರು"
        ],
        "survey_number": [
            "survey_no", "survey number", "survey", "sy.no", "sy no", "s.no", "s no", "survey/khasra",
            "gut no", "gut number", "सर्वे नंबर", "सर्वे संख्या", "సర్వే నంబరు", "సర్వే నెం", "சர்வே எண்",
            "ಸರ್ವೆ ನಂಬರ್", "गट क्रमांक"
        ],
        "khasra_number": [
            "khasra", "khasra no", "khasra number", "khasra_no", "खसरा", "खसरा नं", "खसरा क्रमांक",
            "ਖਸਰਾ ਨੰਬਰ", "خسرہ نمبر"
        ],
        "khata_number": [
            "khata", "khata no", "khata number", "khatauni", "khatauni no", "khewat", "khewat no",
            "खाता संख्या", "खाता नंबर", "खतौनी", "ఖాతా నంబరు", "ಖಾತಾ ಸಂಖ್ಯೆ", "খতিয়ান নম্বর"
        ],
        "khatauni_number": [
            "khatauni", "khatauni no", "khatauni number", "प्रारूप खतौनी", "अधिकार अभिलेख", "ror-1b", "jamabandi"
        ],
        "plot_number": [
            "plot_no", "plot number", "plot", "site no", "site number", "પ્લોટ નંબર", "ప్లాట్ నెం",
            "ப்ளாட் எண்", "प्लॉट क्रमांक"
        ],
        "dag_number": [
            "dag no", "dag number", "dag", "দাগ নম্বর", "দাগ নং"
        ],
        "patta_number": [
            "patta", "patta no", "patta number", "passbook no", "pattadar passbook", "पट्टा", "పట్టా నెం", "பட்டா எண்"
        ],
        "sub_division_number": [
            "sub_division", "sub division", "sub-division", "hissa", "hissa no", "sub no", "पोट हिस्सा",
            "ఉప విభాగం"
        ],
        "land_area": [
            "area", "extent", "land area", "total area", "total extent", "rakba", "रकबा", "क्षेत्रफल",
            "విస్తీర్ణం", "பரப்பளவு", "ವಿಸ್ತೀರ್ಣ", "বিঘা", "रकबा (क्षेत्रफल)"
        ],
        "area_unit": [
            "acres", "acre", "guntas", "guntha", "bigha", "biswa", "cents", "cent", "ground",
            "hectare", "hectares", "sq yards", "sq ft", "kanal", "marla", "एकड़", "गुंठा", "बीघा", "గుంటలు"
        ],
        "village": [
            "village", "mauza", "mouza", "gram", "gaon", "गाँव", "ग्राम", "గ్రామం", "கிராமம்", "ಗ್ರಾಮ", "মৌজা", "ਪਿੰਡ", "موضع"
        ],
        "tehsil": [
            "tehsil", "tahsil", "taluk", "taluka", "mandal", "revenue circle", "block", "तहसील", "तालुका", "మండలం", "வட்டம்", "ತಾಲೂಕು", "তাহসিল", "تحصیل"
        ],
        "taluk": [
            "taluk", "taluka", "तालुका", "வட்டம்", "ತಾಲೂಕು"
        ],
        "mandal": [
            "mandal", "revenue mandal", "మండలం"
        ],
        "district": [
            "district", "dist", "ज़िला", "जिला", "జిల్లా", "மாவட்டம்", "ಜಿಲ್ಲೆ", "জেলা", "ਜ਼ਿਲ੍ਹਾ", "ضلع"
        ],
        "state": [
            "state", "state/ut", "province", "राज्य", "రాష్ట్రం", "மாநிலம்", "ರಾಜ್ಯ", "রাজ্য", "ਸੂਬਾ"
        ],
        "registration_number": [
            "registration_no", "registration number", "reg no", "reg.no", "deed no", "deed number",
            "document no", "doc no", "पंजीयन क्रमांक", "पंजीकरण संख्या", "రిజిస్ట్రేషన్ నంబర్", "பதிவு எண்", "नोंदणी क्रमांक"
        ],
        "registration_date": [
            "registration date", "reg date", "date of registration", "deed date", "date of execution",
            "पंजीयन दिनांक", "తేదీ", "தேதி", "तारीख", "दिनांक"
        ],
        "mutation_number": [
            "mutation_no", "mutation number", "namantaran", "dakhil kharij no", "नामांतरण क्रमांक", "దాఖిల్ ఖారీజ్", "பட்டா மாறுதல் எண்"
        ],
        "mutation_date": [
            "mutation date", "order date", "sanction date", "नामांतरण दिनांक", "ఉత్తర్వు తేదీ"
        ],
        "previous_owner": [
            "previous owner", "seller", "vendor", "transferor", "former owner", "पूर्व स्वामी", "विक्रेता",
            "విక్రేత", "முந்தைய உரிமையாளர்", "விற்பனையாளர்"
        ],
        "current_owner": [
            "current owner", "present owner", "purchaser", "वर्तमान स्वामी", "ప్రస్తుత యజమాని"
        ],
        "land_classification": [
            "land classification", "classification", "land type", "nature of land", "kisam", "भूमि प्रकार",
            "భూమి రకం", "நில வகை", "जमीन प्रकार", "কৃষি জমি"
        ],
        "ownership_type": [
            "ownership type", "tenure", "holding type", "individual", "joint", "स्वामित्व प्रकार", "యాజమాన్య రకం"
        ],
        "document_number": [
            "document number", "doc number", "doc no", "order number", "दस्तावेज़ संख्या"
        ],
        "parcel_number": [
            "parcel number", "parcel id", "gis id", "भूखंड संख्या"
        ]
    }

    @classmethod
    def match_canonical_field(cls, candidate_label: str) -> Optional[str]:
        """Matches an arbitrary document text label to its canonical field key."""
        if not candidate_label:
            return None
        c_clean = candidate_label.lower().strip().replace(":", "").replace("-", " ").replace(".", "")

        for canonical, aliases in cls.FIELD_ALIASES.items():
            for alias in aliases:
                alias_clean = alias.lower().replace(":", "").replace("-", " ").replace(".", "")
                if alias_clean == c_clean or alias_clean in c_clean:
                    return canonical
        return None
