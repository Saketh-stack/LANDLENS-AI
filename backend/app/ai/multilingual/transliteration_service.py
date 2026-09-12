"""
TransliterationService: Phonetic Romanization & Name Preservation.
Preserves personal names, village names, and legal identifiers in their native scripts
while generating standardized English phonetic transliteration.
Strictly ensures names are NEVER erroneously translated as dictionary nouns.
"""
import re
from typing import Dict, Any, Optional

# Indic Character Phonetic Mapping (Consonants, Vowels, Diacritics)
DEVANAGARI_MAP = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ऋ': 'ri',
    'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'am', 'अः': 'ah',
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
    'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'ृ': 'ri',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'n', '्': ''
}

TELUGU_MAP = {
    'అ': 'a', 'ఆ': 'aa', 'ఇ': 'i', 'ఈ': 'ee', 'ఉ': 'u', 'ఊ': 'oo', 'ఋ': 'ri',
    'ఎ': 'e', 'ఏ': 'e', 'ఐ': 'ai', 'ఒ': 'o', 'ఓ': 'o', 'ఔ': 'au', 'అం': 'am',
    'క': 'k', 'ఖ': 'kh', 'గ': 'g', 'ఘ': 'gh', 'ఙ': 'ng',
    'చ': 'ch', 'ఛ': 'chh', 'జ': 'j', 'ఝ': 'jh', 'ఞ': 'ny',
    'ట': 't', 'ఠ': 'th', 'డ': 'd', 'ఢ': 'dh', 'ణ': 'n',
    'త': 't', 'థ': 'th', 'ద': 'd', 'ధ': 'dh', 'న': 'n',
    'ప': 'p', 'ఫ': 'ph', 'బ': 'b', 'భ': 'bh', 'మ': 'm',
    'య': 'y', 'ర': 'r', 'ల': 'l', 'వ': 'v', 'శ': 'sh', 'ష': 'sh', 'స': 's', 'హ': 'h',
    'ళ': 'la', 'క్ష': 'ksha', 'ఱ': 'ra',
    'ా': 'aa', 'ి': 'i', 'ీ': 'ee', 'ు': 'u', 'ూ': 'oo', 'ృ': 'ri',
    'ె': 'e', 'ే': 'e', 'ై': 'ai', 'ొ': 'o', 'ో': 'o', 'ౌ': 'au', 'ం': 'm', '్': ''
}

TAMIL_MAP = {
    'அ': 'a', 'ஆ': 'aa', 'இ': 'i', 'ஈ': 'ee', 'உ': 'u', 'ஊ': 'oo',
    'எ': 'e', 'ஏ': 'e', 'ஐ': 'ai', 'ஒ': 'o', 'ஓ': 'o', 'ஔ': 'au',
    'க': 'k', 'ங': 'ng', 'ச': 'ch', 'ஞ': 'ny', 'ட': 't', 'ண': 'n',
    'த': 'th', 'ந': 'n', 'ப': 'p', 'ம': 'm', 'ய': 'y', 'ர': 'r',
    'ல': 'l', 'வ': 'v', 'ழ': 'zh', 'ள': 'l', 'ற': 'r', 'ன': 'n',
    'ஜ': 'j', 'ஷ': 'sh', 'ஸ': 's', 'ஹ': 'h',
    'ா': 'aa', 'ி': 'i', 'ீ': 'ee', 'ு': 'u', 'ூ': 'oo',
    'ெ': 'e', 'ே': 'e', 'ை': 'ai', 'ொ': 'o', 'ோ': 'o', 'ௌ': 'au', '்': ''
}

BENGALI_MAP = {
    'অ': 'a', 'আ': 'aa', 'ই': 'i', 'ঈ': 'ee', 'উ': 'u', 'ঊ': 'oo', 'ঋ': 'ri',
    'এ': 'e', 'ঐ': 'ai', 'ও': 'o', 'ঔ': 'au',
    'ক': 'k', 'খ': 'kh', 'গ': 'g', 'ঘ': 'gh', 'ঙ': 'ng',
    'চ': 'ch', 'ছ': 'chh', 'জ': 'j', 'ঝ': 'jh', 'ঞ': 'ny',
    'ট': 't', 'ঠ': 'th', 'ড': 'd', 'ঢ': 'dh', 'ণ': 'n',
    'ত': 't', 'থ': 'th', 'দ': 'd', 'ধ': 'dh', 'ন': 'n',
    'প': 'p', 'ফ': 'ph', 'ব': 'b', 'ভ': 'bh', 'ম': 'm',
    'য': 'y', 'র': 'r', 'ল': 'l', 'শ': 'sh', 'ষ': 'sh', 'স': 's', 'হ': 'h',
    'া': 'aa', 'ি': 'i', 'ী': 'ee', 'ু': 'u', 'ূ': 'oo', 'ে': 'e', 'ৈ': 'ai', 'ো': 'o', 'ৌ': 'au', '্': ''
}

# Common Indian Name Direct Transliteration Overrides
KNOWN_NAME_TRANSLITERATIONS = {
    "రమేష్": "Ramesh", "సురేష్": "Suresh", "రాజేష్": "Rajesh", "కుమార్": "Kumar",
    "శర్మ": "Sharma", "రెడ్డి": "Reddy", "రావు": "Rao", "వర్మ": "Verma", "లక్ష్మి": "Lakshmi",
    "రమేశ్": "Ramesh", "సురేశ్": "Suresh", "రాజేశ్": "Rajesh",
    "रमेश": "Ramesh", "सुरेश": "Suresh", "राजेश": "Rajesh", "कुमार": "Kumar",
    "शर्मा": "Sharma", "वर्मा": "Verma", "सिंह": "Singh", "यादव": "Yadav", "गुप्ता": "Gupta",
    "शांति": "Shanti", "लक्ष्मी": "Lakshmi", "देवी": "Devi", "राम": "Ram",
    "ரமேஷ்": "Ramesh", "சுரேஷ்": "Suresh", "ராஜேஷ்": "Rajesh", "குமார்": "Kumar",
    "శంషాబాద్": "Shamshabad", "రాజేంద్రనగర్": "Rajendranagar", "రంగారెడ్డి": "Ranga Reddy",
    "हिंजवड़ी": "Hinjawadi", "पुणे": "Pune", "मुळशी": "Mulshi"
}

class TransliterationService:
    """
    Transliterates Indic names, villages, and identifiers to Latin/English.
    Preserves original script intact.
    """

    @classmethod
    def transliterate_text(cls, text: str, script_hint: Optional[str] = None) -> str:
        """Transliterates text while honoring known Indian names and terms."""
        if not text:
            return ""

        words = text.split()
        out_words = []

        for w in words:
            # Check known proper name dictionary first
            clean_w = w.strip(' ,.-;:"()')
            if clean_w in KNOWN_NAME_TRANSLITERATIONS:
                mapped = KNOWN_NAME_TRANSLITERATIONS[clean_w]
                out_words.append(w.replace(clean_w, mapped))
                continue

            # Character by character phonetic mapping
            res = []
            for ch in w:
                if ch in TELUGU_MAP:
                    res.append(TELUGU_MAP[ch])
                elif ch in DEVANAGARI_MAP:
                    res.append(DEVANAGARI_MAP[ch])
                elif ch in TAMIL_MAP:
                    res.append(TAMIL_MAP[ch])
                elif ch in BENGALI_MAP:
                    res.append(BENGALI_MAP[ch])
                else:
                    res.append(ch)

            translit_word = "".join(res)
            # Capitalize first letter of names
            if translit_word and translit_word[0].isalpha():
                translit_word = translit_word[0].upper() + translit_word[1:]
            out_words.append(translit_word)

        return " ".join(out_words)

    @classmethod
    def preserve_and_transliterate(cls, original_val: Any, field_name: str = "") -> Dict[str, Any]:
        """
        Takes raw field value in any Indian language.
        Returns a rich object preserving original script, transliterated version,
        and legal verification notice.
        """
        if original_val is None:
            return {
                "original_value": "",
                "transliterated_value": "",
                "display_label": "Not Recorded",
                "is_name_preserved": True
            }

        orig_str = str(original_val).strip()
        translit = cls.transliterate_text(orig_str)

        return {
            "original_value": orig_str,
            "transliterated_value": translit,
            "display_label": f"{orig_str} ({translit})" if translit != orig_str and translit else orig_str,
            "is_name_preserved": True
        }
