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
    demo_compat_router
)

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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
