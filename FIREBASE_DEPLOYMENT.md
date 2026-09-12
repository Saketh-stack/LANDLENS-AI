# Google Firebase Deployment Guide — SIH26018

This guide explains how to deploy the **Intelligent Land Record Digitization and Validation System** using **Google Firebase**.

---

## 🏗️ Architecture Overview

Full-stack applications (React + Python FastAPI) on Firebase are typically deployed using one of two architectures:

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Firebase Project                  │
│                                                             │
│   ┌──────────────────────────┐   ┌──────────────────────┐  │
│   │     Firebase Hosting     │   │   Google Cloud Run   │  │
│   │      (React 19 SPA)      │   │  (Python FastAPI)    │  │
│   │   https://<app>.web.app  │   │   Container Service  │  │
│   └────────────┬─────────────┘   └──────────▲───────────┘  │
│                │  /api/** rewrite           │              │
│                └────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

- **Frontend (React 19 + Vite):** Deployed to **Firebase Hosting** (Google's global edge CDN, automatic SSL certificate, fast caching).
- **Backend (Python FastAPI):** Deployed to **Google Cloud Run** (which lives inside the same Google Cloud / Firebase project) or any container host (Render / Railway / Fly.io).
- **Unified Domain Routing:** Firebase Hosting automatically routes `/api/**` to Cloud Run, meaning **no CORS issues** and a single clean domain.

---

## 📋 Prerequisites

1. **Google Account:** With access to the [Firebase Console](https://console.firebase.google.com/).
2. **Node.js & npm:** Already installed on your machine.
3. **Firebase CLI:** Install globally using:
   ```powershell
   npm install -g firebase-tools
   ```

---

## 🚀 Step 1: Create a Project in Firebase Console

1. Go to [https://console.firebase.google.com/](https://console.firebase.google.com/).
2. Click **"Add project"**.
3. Name your project (e.g., `sih26018-land-records`).
4. (Optional) Enable Google Analytics and click **Create project**.
5. Note your **Project ID** (e.g., `sih26018-land-records-12345`).

---

## 🔑 Step 2: Log in to Firebase CLI

Open PowerShell in the project root (`sih3.0`):

```powershell
firebase login
```
*This will open your default browser to authorize the Firebase CLI with your Google account.*

---

## 🔗 Step 3: Link Your Firebase Project

Run the following command to associate this directory with your Firebase project:

```powershell
firebase use --add
```
Select your newly created project from the list, or manually edit `.firebaserc`:
```json
{
  "projects": {
    "default": "<your-actual-firebase-project-id>"
  }
}
```

---

## 📦 Step 4: Build the React Frontend

Ensure the latest production bundle is compiled into `frontend/dist`:

```powershell
cd frontend
npm run build
cd ..
```

---

## 🌐 Step 5: Deploy Frontend to Firebase Hosting

From the root directory:

```powershell
firebase deploy --only hosting
```

When deployment finishes, Firebase CLI will output your live URL:
```
✔  Hosting URL: https://<your-project-id>.web.app
```

Your React Public & Officer Portals are now live on Google Firebase!

---

## ⚡ Step 6: Deploy the Python Backend (Cloud Run Integration)

Since Firebase Hosting serves static assets, the Python FastAPI backend can be deployed to **Google Cloud Run** under the same project.

### Method A: Deploy to Google Cloud Run (Recommended for Hackathons)

1. Install Google Cloud SDK ([gcloud](https://cloud.google.com/sdk/docs/install)).
2. Log in and set your project:
   ```powershell
   gcloud auth login
   gcloud config set project <your-firebase-project-id>
   ```
3. Deploy directly using the provided `backend/Dockerfile`:
   ```powershell
   gcloud run deploy sih26018-backend `
     --source . `
     --port 8080 `
     --region us-central1 `
     --allow-unauthenticated
   ```
4. Once deployed, update `firebase.json` to route `/api/**` to Cloud Run:
   ```json
   {
     "hosting": {
       "public": "frontend/dist",
       "rewrites": [
         {
           "source": "/api/**",
           "run": {
             "serviceId": "sih26018-backend",
             "region": "us-central1"
           }
         },
         {
           "source": "**",
           "destination": "/index.html"
         }
       ]
     }
   }
   ```
5. Re-deploy Firebase Hosting:
   ```powershell
   firebase deploy --only hosting
   ```
   Now `https://<your-project-id>.web.app/api/...` directly reaches your FastAPI backend!

---

### Method B: Deploy Backend to Render / Railway (Alternative Free Cloud Option)

If you prefer deploying the backend without configuring Google Cloud billing:

1. Push your code to GitHub.
2. In [Render](https://render.com) or [Railway](https://railway.app):
   - Create a new **Web Service**.
   - Select your GitHub repository.
   - Set Root Directory: `.`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
3. Copy your live backend URL (e.g. `https://sih26018-api.onrender.com`).
4. In `frontend/`, create `.env.production`:
   ```env
   VITE_API_URL=https://sih26018-api.onrender.com
   ```
5. Re-run `npm run build` and `firebase deploy --only hosting`.

---

## 🛠️ Configuration Files Reference

- **`firebase.json`:** Defines the public hosting directory (`frontend/dist`), Single-Page Application (SPA) rewrite rules, and optional Cloud Run integration.
- **`.firebaserc`:** Stores your Firebase project identifier.
- **`backend/Dockerfile`:** Standard container file compatible with Google Cloud Run.
