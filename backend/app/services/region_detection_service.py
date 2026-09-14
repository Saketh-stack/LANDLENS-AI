"""
RegionDetectionService: Spatial and semantic layout region segmentation
for Indian land documents (Sale Deeds, Khasra-Khatauni, Cadastral Maps, Mutation Orders).
Associates OCR coordinates with functional document regions to improve extraction accuracy.
"""
from typing import Dict, Any, List, Optional

class RegionDetectionService:
    """
    Analyzes spatial coordinates and legal keyword anchors to segment documents into:
    - registration_section
    - parties_section (owner/buyer/seller)
    - parcel_survey_section
    - area_section
    - location_section
    - mutation_section
    - boundary_section
    - tables
    """

    REGION_KEYWORDS = {
        "registration_section": [
            "registration", "reg no", "deed no", "book no", "volume", "page", "stamp", "duty",
            "sub-registrar", "sub registrar", "consideration", "पंजीयन", "पंजीकरण", "రిజిస్ట్రేషన్", "பதிவு"
        ],
        "parties_section": [
            "owner", "purchaser", "buyer", "vendee", "vendor", "seller", "pattadar", "father",
            "husband", "s/o", "w/o", "d/o", "shri", "smt", "holder", "भू-स्वामी", "मालिक", "खातेदार", "భూయజమాని"
        ],
        "parcel_survey_section": [
            "survey", "sy.no", "sy no", "s.no", "khasra", "khata", "plot", "dag", "gut", "hissa",
            "सर्वे", "खसरा", "खाता", "సర్వే", "ఖాతా"
        ],
        "area_section": [
            "area", "extent", "acres", "guntas", "cents", "bigha", "biswa", "hectare", "rakba",
            "रकबा", "क्षेत्रफल", "విస్తీర్ణం", "பரப்பளவு"
        ],
        "location_section": [
            "village", "mauza", "mouza", "gram", "tehsil", "taluk", "mandal", "district", "state",
            "गाँव", "ग्राम", "तहसील", "ज़िला", "మండలం", "గ్రామం"
        ],
        "mutation_section": [
            "mutation", "sanction", "dakhil kharij", "namantaran", "virasat", "tahsildar order",
            "case no", "नामांतरण", "दाखिल खारिज", "వారసత్వ"
        ],
        "boundary_section": [
            "boundary", "boundaries", "north", "south", "east", "west", "schedule of property",
            "चौहद्दी", "సరిహద్దులు", "எல்லைகள்"
        ]
    }

    @classmethod
    def detect_regions(cls, ocr_lines: List[Dict[str, Any]], image_w: int = 1000, image_h: int = 1400) -> Dict[str, Any]:
        """
        Segments OCR lines into layout regions based on text semantics and vertical coordinates.
        """
        regions: Dict[str, List[Dict[str, Any]]] = {
            "registration_section": [],
            "parties_section": [],
            "parcel_survey_section": [],
            "area_section": [],
            "location_section": [],
            "mutation_section": [],
            "boundary_section": [],
            "tables": []
        }

        if not ocr_lines:
            return {k: {"lines": [], "text": "", "line_count": 0} for k in regions}

        # Detect table columns: lines that share close Y-ranges but distinct X columns
        table_candidates = cls._detect_tabular_structures(ocr_lines)

        for line in ocr_lines:
            t = line.get("text", "").lower()
            assigned = False

            # Check keyword associations
            for reg_name, keywords in cls.REGION_KEYWORDS.items():
                if any(k in t for k in keywords):
                    regions[reg_name].append(line)
                    assigned = True
                    break

            if not assigned:
                # Vertical spatial heuristic fallback
                bbox = line.get("bbox", [0, 0, 0, 0])
                y_mid = (bbox[1] + bbox[3]) / 2.0 if len(bbox) >= 4 else 0
                rel_y = y_mid / max(float(image_h), 1.0)

                if rel_y < 0.22:
                    regions["registration_section"].append(line)
                elif rel_y < 0.45:
                    regions["parties_section"].append(line)
                elif rel_y < 0.65:
                    regions["parcel_survey_section"].append(line)
                elif rel_y < 0.85:
                    regions["location_section"].append(line)
                else:
                    regions["boundary_section"].append(line)

        # Build structured output
        summary: Dict[str, Any] = {}
        for reg_name, lines in regions.items():
            if reg_name == "tables":
                summary["tables"] = table_candidates
            else:
                summary[reg_name] = {
                    "line_count": len(lines),
                    "text": "\n".join([l.get("text", "") for l in lines]),
                    "lines": lines
                }

        return summary

    @classmethod
    def _detect_tabular_structures(cls, ocr_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detects horizontally aligned columns resembling land revenue registers / tables."""
        tables = []
        rows: Dict[int, List[Dict[str, Any]]] = {}

        for l in ocr_lines:
            bbox = l.get("bbox", [0, 0, 0, 0])
            if len(bbox) >= 4:
                # Quantize Y to 20px buckets
                y_bucket = int(bbox[1] // 20) * 20
                rows.setdefault(y_bucket, []).append(l)

        # Rows with 3 or more horizontally separated items form a table structure
        table_rows = []
        for y, items in sorted(rows.items()):
            if len(items) >= 3:
                sorted_items = sorted(items, key=lambda x: x.get("bbox", [0])[0])
                table_rows.append({
                    "y": y,
                    "cells": [item.get("text", "") for item in sorted_items]
                })

        if len(table_rows) >= 2:
            tables.append({
                "detected": True,
                "row_count": len(table_rows),
                "rows": table_rows[:15]
            })

        return tables
