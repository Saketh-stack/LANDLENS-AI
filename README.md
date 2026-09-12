# SIH26018 — Intelligent Land Record Digitization and Validation System

**Ministry:** Ministry of Rural Development  
**Department:** Department of Land Resources (DoLR)  
**Theme:** Smart Automation  
**Hackathon:** Smart India Hackathon 2026 Prototype

---

## 🌟 Overview

The **Intelligent Land Record Digitization and Validation System** is an end-to-end full-stack web application developed to modernize and secure India's land governance. It processes both archival historical land registers (handwritten, scanned deeds, cadastral records in English, Hindi, Telugu, Tamil, Marathi) and newly registered properties (received from Sub-Registrar Offices via simulated APIs).

The system applies OCR, AI-driven information extraction, 14 automated business-rule checks, cross-database validation against cadastral ground truth, split-screen officer verification with human-in-the-loop AI model learning, and publishes verified records to a secure public citizen portal.

> **Prototype Service Target:**  
> *"Verified records can be made available for public viewing within 2–3 days after registration, subject to officer verification."*  
> *(Presented as a prototype service target, not an official government SLA).*

---

## 🚀 Key Features

1. **Role-Based Architecture & Portal Separation:**
   - **Public / Citizen Portal:** Search Record of Rights (RoR) by Owner, Survey No, Khasra, Khata, Village, District. Strictly read-only for verified/approved records. Citizens cannot alter official records.
   - **Government Officer Workspace:** Split-screen verification, historical document 8-stage stepper, confidence score inspector, cadastral reconciliation, approval/rejection.
   - **Administrator:** System audit logs, district progress, and validation telemetry.

2. **OCR & AI Extraction Engine:**
   - Multilingual support for Indian languages (English, Hindi, Telugu, Tamil, Marathi).
   - 18+ structured fields extracted with field-level confidence scores (High >80%, Medium 60-80%, Low <60%).
   - Bounding-box visual coordinates on deed canvases.

3. **14 Business Rules & Cross-Database Cadastral Engine:**
   - Validates missing fields, survey number syntax, area sanity.
   - Cross-references incoming deeds against the **Mock Cadastral Ground Truth Database** (e.g. flagging: *"Area mismatch: Land Record = 2.45 Acres, Cadastral DB = 2.40 Acres"*).
   - Duplicate detection on survey parcel collisions.

4. **Sub-Registrar Office (SRO) Integration Simulator:**
   - Mock Registration Department pushes new registered sale deeds via `POST /api/mock-registration/simulate`.
   - Real-time pipeline visualizer (Received → OCR → AI Extraction → Validation → Officer Review → Published).

5. **AI Learning & Continuous Feedback Loop:**
   - Captures officer corrections (e.g., changing 2.45 to 2.40 Acres).
   - Dynamically tracks model accuracy evolution (91.2% → 94.2%+).

6. **Cadastral GIS Map:**
   - Interactive Leaflet map displaying surveyed land parcels with closed polygonal boundaries, verification status badges, and parcel inspector.

7. **Hackathon Judge Demo Mode:**
   - Prominent toolbar with 1-click presets for all 7 evaluation scenarios.

---

## 🛠️ Tech Stack

- **Backend:** Python FastAPI, SQLAlchemy, SQLite (PostgreSQL ready), Pydantic.
- **Frontend:** React 19 (Vite), Tailwind CSS, Lucide Icons, Recharts, Leaflet, React-Leaflet, Axios.
- **Security:** JWT Authentication, hashed credentials, role-based middleware guards.

---

## 🏃 Running Locally

### 1. Backend Setup
```bash
# From the project root:
cd backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
Backend API will be accessible at: `http://127.0.0.1:8000`  
Interactive Swagger Docs at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
Frontend Portal will be accessible at: `http://127.0.0.1:5173`

---

## 🔑 Demo Credentials

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Government Officer** | `officer` or `officer@dolr.gov.in` | `officer123` | Senior Revenue Officer / Tahsildar |
| **Administrator** | `admin` or `admin@dolr.gov.in` | `admin123` | National Portal Administrator |
| **Public Citizen** | `citizen` or `citizen@india.gov.in` | `citizen123` | Public Viewer |

---

## 🎬 Step-by-Step Judge Demonstration Flow

1. **Open Public Portal (`http://127.0.0.1:5173/`)**:
   - Search for landowner `"Ravi Kumar"` or survey number `"123/4A"`.
   - Click **"View Details"** to open the certified Record of Rights (RoR) modal. Notice only approved records are visible.
2. **Log in as Government Officer**:
   - Click **"Officer Login"** in the top right.
   - Use the quick 1-click preset button for `officer / officer123`.
3. **Trigger New Registration Simulation**:
   - Navigate to **"New Registrations"**.
   - Click **"Simulate New Registration"**.
   - Watch the live 7-stage automated pipeline stream:
     - Document Received → OCR Completed → AI Extracted → Validation Completed → Area Mismatch Alert (2.45 vs 2.40 Acres).
4. **Split-Screen Human Verification**:
   - Click **"Open Split-Screen Officer Verification"**.
   - **Left Pane:** View the original deed canvas with bounding box overlays.
   - **Right Pane:** View extracted fields with confidence badges and the Cadastral DB warning.
   - Click **"Sync with Cadastral DB (2.40 Ac)"** to correct the land area.
   - Click **"Approve & Publish to Public Portal"**.
5. **AI Model Learning Feedback**:
   - Open **"AI Learning Metrics"** in the navbar to observe the logged correction and accuracy boost.
6. **Public Verification**:
   - Open an incognito tab or click Log Out.
   - Search for the newly approved record on the Public Portal to confirm immediate public availability.
7. **Cadastral GIS Map**:
   - Open the **"Cadastral GIS Map"** tab to view the geo-referenced survey parcel polygons and inspect boundaries.
