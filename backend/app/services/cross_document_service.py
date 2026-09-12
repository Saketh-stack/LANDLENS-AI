"""
CrossDocumentService: Cross-document verification and discrepancy detection for Indian land records.
Compares information across the 4 core documents:
- Registered Sale Deed
- Khasra / Khatauni Register
- Cadastral Boundary Map
- Mutation Sanction Order

Generates a comparison matrix:
Field | Sale Deed | Khasra/Khatauni | Cadastral Map | Mutation Order | Status

Flags:
- Matching information
- Possible mismatches (e.g. area delta)
- Missing information ("Not found")
- Conflicting information (different owners)
- Possible OCR errors (fuzzy typos)

Status levels:
- GREEN: Information appears consistent
- YELLOW: Possible mismatch or insufficient information; officer review required
- RED: Significant inconsistency detected; detailed officer verification required
"""
import re
from typing import Dict, Any, List, Optional
from difflib import SequenceMatcher
from backend.app.core.logging import logger

class CrossDocumentService:
    """
    Verification Engine comparing multiple uploaded documents for the same land parcel.
    """

    COMPARISON_FIELDS = [
        ("survey_number", "Survey / Khasra Number"),
        ("khata_number", "Khata / Account Number"),
        ("owner_name", "Owner Name / Transferee"),
        ("previous_owner", "Previous Owner / Vendor"),
        ("new_owner", "New Owner / Purchaser"),
        ("land_area", "Land Area / Extent"),
        ("village", "Village / Mouza"),
        ("mandal_tehsil_taluk", "Mandal / Tehsil / Taluk"),
        ("district", "District"),
        ("state", "State"),
        ("boundary_north", "North Boundary"),
        ("boundary_south", "South Boundary"),
        ("boundary_east", "East Boundary"),
        ("boundary_west", "West Boundary"),
        ("mutation_info", "Mutation / Order Reference")
    ]

    @classmethod
    def compare_documents(cls, documents_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes a list of extracted documents, each having:
        - document_type: str
        - filename: str
        - fields_map: dict of field -> value
        """
        # Bucket by type
        by_type = {
            "sale_deed": None,
            "khasra": None,
            "cadastral": None,
            "mutation": None
        }

        for d in documents_data:
            dt = d.get("document_type", "").lower()
            f_map = d.get("fields_map", {})
            if "sale" in dt:
                by_type["sale_deed"] = f_map
            elif "khasra" in dt or "khatauni" in dt:
                by_type["khasra"] = f_map
            elif "cadastral" in dt or "map" in dt:
                by_type["cadastral"] = f_map
            elif "mutation" in dt:
                by_type["mutation"] = f_map

        matrix = []
        has_red = False
        has_yellow = False
        match_count = 0
        mismatch_count = 0
        missing_count = 0

        for field_key, field_label in cls.COMPARISON_FIELDS:
            sd_val = cls._get_field_val(by_type["sale_deed"], field_key, "sale_deed")
            kh_val = cls._get_field_val(by_type["khasra"], field_key, "khasra")
            cad_val = cls._get_field_val(by_type["cadastral"], field_key, "cadastral")
            mut_val = cls._get_field_val(by_type["mutation"], field_key, "mutation")

            row_status, notes = cls._evaluate_field_status(field_key, sd_val, kh_val, cad_val, mut_val)

            if row_status == "RED":
                has_red = True
                mismatch_count += 1
            elif row_status == "YELLOW":
                has_yellow = True
                if "Not found" in [sd_val, kh_val, cad_val, mut_val]:
                    missing_count += 1
                else:
                    mismatch_count += 1
            elif row_status == "GREEN":
                match_count += 1

            matrix.append({
                "field_key": field_key,
                "field_label": field_label,
                "sale_deed": sd_val,
                "khasra_khatauni": kh_val,
                "cadastral_map": cad_val,
                "mutation_order": mut_val,
                "status": row_status,
                "notes": notes
            })

        # Overall Status
        if has_red:
            overall_status = "RED"
            status_desc = "Significant inconsistency detected; detailed officer verification required."
        elif has_yellow or (len([d for d in documents_data if d]) < 2):
            overall_status = "YELLOW"
            status_desc = "Possible mismatch or insufficient information; officer review required."
        else:
            overall_status = "GREEN"
            status_desc = "Information appears consistent across uploaded documents."

        return {
            "comparison_matrix": matrix,
            "overall_status": overall_status,
            "status_description": status_desc,
            "documents_analyzed_count": len(documents_data),
            "match_count": match_count,
            "mismatch_count": mismatch_count,
            "missing_count": missing_count,
            "legal_notice": (
                "AI assists in document classification, OCR, information extraction and inconsistency detection. "
                "AI does not make the final legal ownership decision. "
                "Final verification must be performed by an authorized government officer."
            )
        }

    @classmethod
    def _get_field_val(cls, f_map: Optional[Dict[str, Any]], field_key: str, doc_category: str) -> str:
        if not f_map:
            return "Document not uploaded"

        # Alias mappings
        aliases = [field_key]
        if field_key == "survey_number":
            aliases += ["khasra_number", "parcel_numbers"]
        elif field_key == "owner_name":
            aliases += ["buyer_name", "new_owner_name", "applicant_name"]
        elif field_key == "previous_owner":
            aliases += ["seller_name", "previous_owner_name"]
        elif field_key == "new_owner":
            aliases += ["buyer_name", "new_owner_name"]
        elif field_key == "boundary_north":
            aliases += ["north_boundary", "north_direction"]
        elif field_key == "boundary_south":
            aliases += ["south_boundary"]
        elif field_key == "boundary_east":
            aliases += ["east_boundary"]
        elif field_key == "boundary_west":
            aliases += ["west_boundary"]
        elif field_key == "mutation_info":
            aliases += ["mutation_number", "order_number", "mutation_information"]

        for a in aliases:
            if a in f_map and f_map[a] and str(f_map[a]).strip().lower() not in ["none", "null", "n/a", "not found"]:
                return str(f_map[a]).strip()

        return "Not found"

    @classmethod
    def _evaluate_field_status(cls, field_key: str, v1: str, v2: str, v3: str, v4: str) -> tuple[str, str]:
        vals = [v for v in [v1, v2, v3, v4] if v not in ["Document not uploaded", "Not found"]]
        if not vals:
            return "YELLOW", "Information missing across uploaded records"

        if len(vals) == 1:
            return "YELLOW", "Only 1 document provides this field; unable to cross-validate"

        # Check for Land Area mismatch
        if field_key == "land_area":
            num_vals = []
            for v in vals:
                m = re.search(r'([\d\.]+)', v)
                if m:
                    num_vals.append(float(m.group(1)))
            if num_vals:
                diff = max(num_vals) - min(num_vals)
                if diff > 0.05:
                    return "RED", f"Area conflict detected: delta {diff:.2f} units between uploaded documents"
                elif diff > 0.001:
                    return "YELLOW", f"Minor area discrepancy: delta {diff:.2f} units"
                else:
                    return "GREEN", "Land area perfectly matches across records"

        # Check exact string match
        cleaned = [cls._clean_str(v) for v in vals]
        if len(set(cleaned)) == 1:
            return "GREEN", "Values match across documents"

        # Fuzzy check for OCR typographical differences
        sims = []
        for i in range(len(cleaned)):
            for j in range(i + 1, len(cleaned)):
                sims.append(SequenceMatcher(None, cleaned[i], cleaned[j]).ratio())

        min_sim = min(sims) if sims else 1.0
        if min_sim >= 0.82:
            return "YELLOW", "Possible minor OCR typographical discrepancy"

        # If critical fields like owner or survey differ substantially: RED
        if field_key in ["survey_number", "owner_name", "new_owner"]:
            return "RED", "Substantial conflict in legal identifier/party name"

        return "YELLOW", "Discrepancy detected across records; requires officer clarification"

    @classmethod
    def _clean_str(cls, s: str) -> str:
        s = s.lower().strip()
        s = re.sub(r'[^\w\s]', '', s)
        s = re.sub(r'\s+', ' ', s)
        return s
