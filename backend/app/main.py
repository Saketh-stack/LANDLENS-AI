import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.core.logging import logger
from backend.app.api.routes import (
    auth_router,
    users_router,
    land_records_router,
    documents_router,
    registrations_router,
    validation_router,
    verification_router,
    dashboard_router,
    search_router,
    gis_router,
    audit_router,
    admin_router,
    mock_registration_router,
    public_router,
    officer_compat_router,
    demo_compat_router,
    multilingual_router
)

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Auto-create all SQLAlchemy database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "SIH26018 — Intelligent Land Record Digitization and Validation System\n\n"
        "Ministry of Rural Development — Department of Land Resources (DoLR)\n\n"
        "Features:\n"
        "- Pan-India Multi-Lingual Land Records Digitization (English, Hindi, Telugu, Tamil, Marathi)\n"
        "- 14 Automated Business Rules & Cadastral Ground Truth Cross-Validation\n"
        "- Sub-Registrar Office (SRO) Simulated Ingestion Pipeline\n"
        "- Role-Based Access Control (Citizen, Officer, Admin)\n"
        "- GIS & Google Maps Cadastral Visualization\n"
        "- Continuous Human-in-the-Loop AI Feedback Loop"
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Explicit CORS configuration
allowed_origins = [
    "https://landlens-ai-56a07.web.app",
    "https://landlens-ai-56a07.firebaseapp.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]
custom_origins = os.getenv("ALLOWED_ORIGINS", "")
if custom_origins:
    allowed_origins.extend([o.strip() for o in custom_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if os.getenv("STRICT_CORS") == "true" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Strict JSON error handlers to prevent HTML error responses
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "error": "Validation Error", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def custom_generic_exception_handler(request, exc):
    logger.error(f"Unhandled Server Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "error": "Internal Server Error", "detail": str(exc)}
    )

# Required Health Endpoint for Cloud Run / Monitoring
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "LANDLENS-AI backend"
    }

# Mount uploads static folder
upload_dir = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Include Modular API Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(land_records_router)
app.include_router(documents_router)
app.include_router(registrations_router)
app.include_router(validation_router)
app.include_router(verification_router)
app.include_router(dashboard_router)
app.include_router(search_router)
app.include_router(gis_router)
app.include_router(audit_router)
app.include_router(admin_router)
app.include_router(mock_registration_router)
app.include_router(public_router)

# Compatibility Routers for existing Frontend UI
app.include_router(officer_compat_router)
app.include_router(demo_compat_router)
app.include_router(multilingual_router)

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "sih_code": "SIH26018",
        "ministry": settings.MINISTRY,
        "department": settings.DEPARTMENT,
        "status": "OPERATIONAL",
        "demo_mode": settings.DEMO_MODE,
        "mock_mode": settings.MOCK_MODE,
        "proposed_service_target": "Verified registration records available for public viewing within 2-3 days."
    }
