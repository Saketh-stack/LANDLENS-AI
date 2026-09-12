from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class ValidationRuleResultOut(BaseModel):
    rule_id: str
    rule_name: str
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ValidationSummaryOut(BaseModel):
    results: List[ValidationRuleResultOut]
    has_errors: bool
    has_warnings: bool
    overall_status: str
    passed_rules_count: int
    total_rules_count: int
