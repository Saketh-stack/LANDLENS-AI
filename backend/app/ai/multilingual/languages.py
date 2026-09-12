"""
LanguageConfiguration: Central, extensible Indian language registry.
Defines metadata, Unicode ranges, native scripts, numeral mappings,
and regional measurement units for all 13 supported Indian languages.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

@dataclass
class LanguageMeta:
    code: str
    name: str
    native_name: str
    script: str
    unicode_ranges: List[tuple[int, int]]  # (start_codepoint, end_codepoint)
    numeral_map: Dict[str, str] = field(default_factory=dict)  # Native digit -> '0'-'9'
    locale_code: str = "en-IN"
    common_land_terms: List[str] = field(default_factory=list)

class LanguageConfiguration:
    """
    Extensible Indian Language Registry.
    Supports English + 12 Scheduled Indian Languages.
    New languages can be dynamically registered without altering system core.
    """
    _LANGUAGES: Dict[str, LanguageMeta] = {}

    @classmethod
    def register_language(cls, meta: LanguageMeta):
        cls._LANGUAGES[meta.code] = meta

    @classmethod
    def get_language(cls, code: str) -> Optional[LanguageMeta]:
        return cls._LANGUAGES.get(code)

    @classmethod
    def get_all_languages(cls) -> Dict[str, LanguageMeta]:
        return cls._LANGUAGES

    @classmethod
    def get_supported_codes(cls) -> List[str]:
        return list(cls._LANGUAGES.keys())

# --- Register 13 Major Indian Languages ---

# 1. English
LanguageConfiguration.register_language(LanguageMeta(
    code="en",
    name="English",
    native_name="English",
    script="Latin",
    unicode_ranges=[(0x0041, 0x005A), (0x0061, 0x007A)],
    numeral_map={},
    locale_code="en-IN",
    common_land_terms=["Sale Deed", "Survey Number", "Plot", "Patta", "Owner", "Acre", "Boundary"]
))

# 2. Hindi
LanguageConfiguration.register_language(LanguageMeta(
    code="hi",
    name="Hindi",
    native_name="हिन्दी",
    script="Devanagari",
    unicode_ranges=[(0x0900, 0x097F)],
    numeral_map={'०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'},
    locale_code="hi-IN",
    common_land_terms=["बैनामा", "विक्रय पत्र", "खसरा", "खतौनी", "सर्वे संख्या", "भू-स्वामी", "रकबा", "बीघा", "बिस्वा", "तहसील", "गाँव"]
))

# 3. Telugu
LanguageConfiguration.register_language(LanguageMeta(
    code="te",
    name="Telugu",
    native_name="తెలుగు",
    script="Telugu",
    unicode_ranges=[(0x0C00, 0x0C7F)],
    numeral_map={'౦': '0', '౧': '1', '౨': '2', '౩': '3', '౪': '4', '౫': '5', '౬': '6', '౭': '7', '౮': '8', '౯': '9'},
    locale_code="te-IN",
    common_land_terms=["క్రయవిక్రయ పత్రము", "సర్వే నంబరు", "పట్టాదారు పాస్ పుస్తకం", "ఖాతా నంబరు", "భూయజమాని", "విస్తీర్ణం", "గుంటలు", "మండలం", "గ్రామం"]
))

# 4. Tamil
LanguageConfiguration.register_language(LanguageMeta(
    code="ta",
    name="Tamil",
    native_name="தமிழ்",
    script="Tamil",
    unicode_ranges=[(0x0B80, 0x0BFF)],
    numeral_map={'௦': '0', '௧': '1', '௨': '2', '௩': '3', '௪': '4', '௫': '5', '௬': '6', '௭': '7', '௮': '8', '௯': '9'},
    locale_code="ta-IN",
    common_land_terms=["கிரய பத்திரம்", "சர்வே எண்", "பட்டா எண்", "சிட்டா", "நில உரிமையாளர்", "சென்ட்", "கிரவுண்ட்", "வட்டம்", "கிராமம்"]
))

# 5. Kannada
LanguageConfiguration.register_language(LanguageMeta(
    code="kn",
    name="Kannada",
    native_name="ಕನ್ನಡ",
    script="Kannada",
    unicode_ranges=[(0x0C80, 0x0CFF)],
    numeral_map={'೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4', '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9'},
    locale_code="kn-IN",
    common_land_terms=["ಕ್ರಯ ಪತ್ರ", "ಸರ್ವೆ ನಂಬರ್", "ಖಾತಾ ಸಂಖ್ಯೆ", "ಪಹಣಿ", "ಭೂಮಾಲೀಕರು", "ಗುಂಟೆ", "ತಾಲೂಕು", "ಗ್ರಾಮ"]
))

# 6. Malayalam
LanguageConfiguration.register_language(LanguageMeta(
    code="ml",
    name="Malayalam",
    native_name="മലയാളം",
    script="Malayalam",
    unicode_ranges=[(0x0D00, 0x0D7F)],
    numeral_map={'൦': '0', '൧': '1', '൨': '2', '൩': '3', '൪': '4', '൫': '5', '൬': '6', '൭': '7', '൮': '8', '൯': '9'},
    locale_code="ml-IN",
    common_land_terms=["തീറാധാരം", "സർവേ നമ്പർ", "തണ്ടപ്പേര്", "പട്ടയം", "ഭൂവുടമ", "സെന്റ്", "ഏക്കർ", "താലൂക്ക്", "വില്ലേജ്"]
))

# 7. Marathi
LanguageConfiguration.register_language(LanguageMeta(
    code="mr",
    name="Marathi",
    native_name="मराठी",
    script="Devanagari",
    unicode_ranges=[(0x0900, 0x097F)],
    numeral_map={'०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'},
    locale_code="mr-IN",
    common_land_terms=["खरेदीखत", "७/१२ उतारा", "गट क्रमांक", "सर्व्हे नंबर", "खातेदार", "गुंठा", "तालुका", "गाव"]
))

# 8. Gujarati
LanguageConfiguration.register_language(LanguageMeta(
    code="gu",
    name="Gujarati",
    native_name="ગુજરાતી",
    script="Gujarati",
    unicode_ranges=[(0x0A80, 0x0AFF)],
    numeral_map={'૦': '0', '૧': '1', '૨': '2', '૩': '3', '૪': '4', '૫': '5', '૬': '6', '૭': '7', '૮': '8', '૯': '9'},
    locale_code="gu-IN",
    common_land_terms=["વેચાણ દસ્તાવેજ", "૭/૧૨ નો ઉતારો", "સર્વે નંબર", "ખાતા નંબર", "જમીન માલિક", "વીઘા", "તાલુકો", "ગામ"]
))

# 9. Bengali
LanguageConfiguration.register_language(LanguageMeta(
    code="bn",
    name="Bengali",
    native_name="বাংলা",
    script="Bengali",
    unicode_ranges=[(0x0980, 0x09FF)],
    numeral_map={'০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5', '⑥': '6', '৭': '7', '৮': '8', '৯': '9'},
    locale_code="bn-IN",
    common_land_terms=["বিক্রয় দলিল", "খতিয়ান নম্বর", "দাগ নম্বর", "মৌজা", "জমির মালিক", "বিঘা", "কাঠা", "থানা", "জেলা"]
))

# 10. Punjabi
LanguageConfiguration.register_language(LanguageMeta(
    code="pa",
    name="Punjabi",
    native_name="ਪੰਜਾਬੀ",
    script="Gurmukhi",
    unicode_ranges=[(0x0A00, 0x0A7F)],
    numeral_map={'੦': '0', '੧': '1', '੨': '2', '੩': '3', '੪': '4', '੫': '5', '੬': '6', '੭': '7', '੮': '8', '੯': '9'},
    locale_code="pa-IN",
    common_land_terms=["ਬੈਨਾਮਾ", "ਜਮ੍ਹਾਂਬੰਦੀ", "ਖਸਰਾ ਨੰਬਰ", "ਖੇਵਟ ਨੰਬਰ", "ਜ਼ਮੀਨ ਮਾਲਕ", "ਕਨਾਲ", "ਮਰਲਾ", "ਤਹਿਸੀਲ", "ਪਿੰਡ"]
))

# 11. Odia
LanguageConfiguration.register_language(LanguageMeta(
    code="or",
    name="Odia",
    native_name="ଓଡ଼ିଆ",
    script="Odia",
    unicode_ranges=[(0x0B00, 0x0B7F)],
    numeral_map={'୦': '0', '୧': '1', '୨': '2', '୩': '3', '୪': '4', '୫': '5', '୬': '6', '୭': '7', '୮': '8', '୯': '9'},
    locale_code="or-IN",
    common_land_terms=["ବିକ୍ରୟ ଦଲିଲ", "ପଟ୍ଟା", "ଖତିଆନ ନମ୍ବର", "ପ୍ଲଟ ନମ୍ବର", "ଜମି ମାଲିକ", "ଗୁଣ୍ଠ", "ମାଣ", "ତହସିଲ", "ଗ୍ରାମ"]
))

# 12. Assamese
LanguageConfiguration.register_language(LanguageMeta(
    code="as",
    name="Assamese",
    native_name="অসমীয়া",
    script="Bengali-Assamese",
    unicode_ranges=[(0x0980, 0x09FF)],
    numeral_map={'০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'},
    locale_code="as-IN",
    common_land_terms=["বিক্ৰী দলিল", "পট্টা নম্বৰ", "দাগ নম্বৰ", "মৌজা", "মাটিৰ গৰাকী", "বিঘা", "কঠা", "ৰাজহ চক্ৰ", "গাঁও"]
))

# 13. Urdu
LanguageConfiguration.register_language(LanguageMeta(
    code="ur",
    name="Urdu",
    native_name="اردو",
    script="Perso-Arabic",
    unicode_ranges=[(0x0600, 0x06FF), (0x0750, 0x077F), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)],
    numeral_map={'۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'},
    locale_code="ur-IN",
    common_land_terms=["بیع نامہ", "خسرہ نمبر", "کھتونی", "خاتہ", "مالک زمین", "موضع", "تحصیل", "ضلع"]
))

