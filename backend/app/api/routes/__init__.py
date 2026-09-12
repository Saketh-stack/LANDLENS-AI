from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.users import router as users_router
from backend.app.api.routes.land_records import router as land_records_router
from backend.app.api.routes.documents import router as documents_router
from backend.app.api.routes.registrations import router as registrations_router
from backend.app.api.routes.validation import router as validation_router
from backend.app.api.routes.verification import router as verification_router
from backend.app.api.routes.dashboard import router as dashboard_router
from backend.app.api.routes.search import router as search_router
from backend.app.api.routes.gis import router as gis_router
from backend.app.api.routes.audit import router as audit_router
from backend.app.api.routes.admin import router as admin_router
from backend.app.api.routes.mock_registration import router as mock_registration_router
from backend.app.api.routes.public import router as public_router
from backend.app.api.routes.compat import officer_compat_router, demo_compat_router

__all__ = [
    "auth_router",
    "users_router",
    "land_records_router",
    "documents_router",
    "registrations_router",
    "validation_router",
    "verification_router",
    "dashboard_router",
    "search_router",
    "gis_router",
    "audit_router",
    "admin_router",
    "mock_registration_router",
    "public_router",
    "officer_compat_router",
    "demo_compat_router"
]
