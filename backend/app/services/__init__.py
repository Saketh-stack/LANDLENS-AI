from backend.app.services.auth_service import AuthService
from backend.app.services.land_record_service import LandRecordService
from backend.app.services.document_service import DocumentService
from backend.app.services.registration_service import RegistrationService
from backend.app.services.validation_service import ValidationService
from backend.app.services.verification_service import VerificationService
from backend.app.services.audit_service import AuditService
from backend.app.services.duplicate_service import DuplicateService
from backend.app.services.search_service import SearchService
from backend.app.services.dashboard_service import DashboardService

__all__ = [
    "AuthService",
    "LandRecordService",
    "DocumentService",
    "RegistrationService",
    "ValidationService",
    "VerificationService",
    "AuditService",
    "DuplicateService",
    "SearchService",
    "DashboardService"
]
