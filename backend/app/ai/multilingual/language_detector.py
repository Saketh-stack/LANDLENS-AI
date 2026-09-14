"""
LanguageDetectionService: High-precision Unicode script & language detector.
Detects both single-script and mixed-language Indian documents (e.g. Telugu + English,
Hindi + English, Tamil + English) with percentage distributions.
"""
import re
from typing import Dict, Any, List
from backend.app.ai.multilingual.languages import LanguageConfiguration

class LanguageDetectionService:
    """
    Analyzes raw text codepoints against Indian language Unicode blocks.
    Identifies primary language, secondary languages, and mixed-language ratio.
    """

    @classmethod
    def detect_languages(cls, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "primary_code": "en",
                "primary_name": "English",
                "is_mixed": False,
                "summary": "English",
                "distributions": [{"code": "en", "name": "English", "percentage": 100.0}],
                "scripts": ["Latin"]
            }

        # Count characters belonging to each script
        all_langs = LanguageConfiguration.get_all_languages()
        script_counts: Dict[str, int] = {code: 0 for code in all_langs}
        total_matched = 0

        for ch in text:
            cp = ord(ch)
            # Skip spaces, control characters, common punctuation
            if ch.isspace() or ch in ',.:;-_()[]{}<>"\'/\\|!@#$%^&*+=?~`':
                continue

            matched = False
            for code, meta in all_langs.items():
                for start, end in meta.unicode_ranges:
                    if start <= cp <= end:
                        script_counts[code] += 1
                        total_matched += 1
                        matched = True
                        break
                if matched:
                    break

        if total_matched == 0:
            return {
                "primary_code": "en",
                "primary_name": "English",
                "is_mixed": False,
                "summary": "English",
                "distributions": [{"code": "en", "name": "English", "percentage": 100.0}],
                "scripts": ["Latin"]
            }

        # Calculate percentages
        dists = []
        for code, count in script_counts.items():
            if count > 0:
                pct = round((count / total_matched) * 100, 1)
                if pct >= 3.0:  # Threshold to filter noise
                    meta = all_langs[code]
                    dists.append({
                        "code": code,
                        "name": meta.name,
                        "native_name": meta.native_name,
                        "script": meta.script,
                        "percentage": pct,
                        "count": count
                    })

        # Sort descending by percentage
        dists.sort(key=lambda x: x["percentage"], reverse=True)

        if not dists:
            dists = [{"code": "en", "name": "English", "native_name": "English", "script": "Latin", "percentage": 100.0, "count": total_matched}]

        primary = dists[0]
        is_mixed = len(dists) > 1 and dists[1]["percentage"] >= 10.0

        if is_mixed:
            summary = f"{primary['name']} + {dists[1]['name']} (Mixed)"
        else:
            summary = primary["name"]

        # If Devanagari script is detected, distinguish Marathi vs Hindi using vocabulary hints
        if primary["code"] in ["hi", "mr"] and len(dists) > 0:
            cls._disambiguate_devanagari(text, primary, dists)

        # Distinguish Bengali vs Assamese
        if primary["code"] in ["bn", "as"]:
            cls._disambiguate_bengali_assamese(text, primary, dists)

        return {
            "primary_code": primary["code"],
            "primary_name": primary["name"],
            "primary_language": primary["name"],
            "primary_script": primary.get("script", "Unknown"),
            "is_mixed": is_mixed,
            "is_multilingual": is_mixed or primary["code"] != "en",
            "summary": summary,
            "distributions": dists,
            "scripts": list({d["script"] for d in dists if "script" in d})
        }

    @classmethod
    def _disambiguate_devanagari(cls, text: str, primary: Dict[str, Any], dists: List[Dict[str, Any]]):
        marathi_markers = ["खरेदीखत", "७/१२", "उतारा", "गट क्रमांक", "खातेदार", "गुंठा", "तालुका", "आहे", "जमीन", "गावठाण"]
        hindi_markers = ["बैनामा", "विक्रय पत्र", "खसरा", "खतौनी", "रकबा", "बीघा", "तहसीलदार", "ग्राम", "श्रीमती", "निवासी"]

        m_score = sum(1 for w in marathi_markers if w in text)
        h_score = sum(1 for w in hindi_markers if w in text)

        if m_score > h_score and m_score >= 1:
            primary["code"] = "mr"
            primary["name"] = "Marathi"
        elif h_score > m_score:
            primary["code"] = "hi"
            primary["name"] = "Hindi"

    @classmethod
    def _disambiguate_bengali_assamese(cls, text: str, primary: Dict[str, Any], dists: List[Dict[str, Any]]):
        # Assamese unique characters: ৰ (0x09F0), ৱ (0x09F1)
        if 'ৰ' in text or 'ৱ' in text:
            primary["code"] = "as"
            primary["name"] = "Assamese"
        elif "মৌজা" in text and ("খতিয়ান" in text or "দলিল" in text):
            primary["code"] = "bn"
            primary["name"] = "Bengali"
