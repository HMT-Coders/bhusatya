# BhuSatya (भू-सत्य) — Full Hackathon MVP

**MU ANANT 1.0 · Problem Statement MU-PS-004**  
AI-assisted, evidence-first land-document screening prototype.

> **Important:** This is a hackathon demonstration, not legal certification, proof of ownership, or a substitute for verification by the competent authority. Registry data included here is synthetic demo data only.

## What is included
- React + TypeScript + Vite frontend
- Python + Flask backend
- PostgreSQL schema and synthetic seed data
- Upload and file validation (PDF/JPG/PNG)
- SHA-256 document hash
- OCR adapter using Tesseract when installed
- Deterministic cross-field checks and synthetic registry matching
- Seven-category explainable risk engine with missing-check handling
- Evidence-oriented result report
- Hindi-first interface with a language selector for 12 Indian languages (Hindi, English, Marathi, Gujarati, Punjabi, Bengali, Tamil, Telugu, Kannada, Malayalam, Odia and Urdu)
- MP Bhulekh WebGIS 2.0 reference link and land-record hierarchy cues; no live government integration is claimed
- Three benchmark scenarios for the demo
- Phase-by-phase implementation and presentation guide

## Run locally

### Requirements
- Node.js 20+ and npm
- Python 3.11+
- Optional: Tesseract OCR installed on the machine (install both `eng` and `hin` language packs for Hindi/English scans; if `hin` is missing, image OCR falls back to English)
- PostgreSQL optional for the current local demo; the backend can run in demo mode without it. The schema is included for the DB integration phase.

### 1. Start the backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows CMD; on PowerShell use Copy-Item
# macOS/Linux: cp .env.example .env
python app.py
```
Backend runs at `http://localhost:5000`.

If Tesseract is not installed, the app will mark OCR unavailable or allow you to use the built-in synthetic demo scenarios. Do not claim real OCR ran if it did not.

### 2. Start the frontend (new terminal)
```bash
cd frontend
npm install
copy .env.example .env   # Windows CMD; PowerShell: Copy-Item
npm run dev
```
Open the URL Vite prints, usually `http://localhost:5173`.

## Run the three guided demo cases
Use the dashboard's “Load demo case” control:
1. **Indore Sale Deed — lower concern:** consistent fields; synthetic registry match.
2. **Bhopal Kolar Khasra — manual verification:** survey number `142/1` vs `142/9`.
3. **Jabalpur Registry — elevated concern:** area discrepancy `0.450 Ha` vs `3.400 Ha`, with synthetic anomaly indicators.

Demo cases are explicitly simulated examples. They are not evidence about real records.

## Phase map — how the project maps to the official four phases

### Phase 1 — Ideation & Planning (10:00 AM–3:00 PM, 9 Oct)
Artifacts: `docs/problem-and-scope.md`, `docs/architecture.md`, `docs/api-contracts.md`, `docs/risk-model.md`, `docs/team-task-board.md`, `docs/phase1-checklist.md`, database schema and synthetic seed data.
Outcome: agreed scope, API, schema, risk policy, team ownership, deployment plan.

### Phase 2 — Design & Development (3:00 PM–10:00 PM, 9 Oct)
Build: frontend dashboard/upload/report; backend Flask routes; upload validation; file hashing; demo-case UI; first connected prototype.
Acceptance: frontend can call `/api/v1/health`, load demo cases, and display analysis findings.

### Phase 3 — Integration, Development & Testing (10:00 PM, 9 Oct–9:00 AM, 10 Oct)
Build/test: OCR availability and failure paths, real upload analysis, cross-page field comparisons, risk aggregation, registry matching, API integration, responsive UI, unit tests.
Acceptance: three demo scenarios work, errors are understandable, unavailable checks are disclosed, no secrets are committed.

### Phase 4 — Finalization & Pitch (9:00 AM–3:30 PM, 10 Oct)
Finalize: deployment, demo rehearsal, README, architecture slide, limitations, screenshots/video fallback, pitch.
Acceptance: reproducible demo; all claims match implemented functionality; legal disclaimer visible.

## Team of four
- Member 1 — Frontend: React/TypeScript/Vite, dashboard, upload/report UI, Vercel.
- Member 2 — Backend/integration: Flask routes, validation, CORS, Render.
- Member 3 — OCR/document intelligence: Tesseract, extraction, cross-page comparisons.
- Member 4 — Database/risk/QA: schema, synthetic fixtures, scoring, tests and demo fallback.

## API
- `GET /api/v1/health`
- `GET /api/v1/demo-cases`
- `POST /api/v1/documents` multipart upload
- `POST /api/v1/documents/<document_id>/analyze`
- `GET /api/v1/verifications/<verification_id>`
- `GET /api/v1/verifications/<verification_id>/report`
- `GET /api/v1/registry/search?q=...`

## Deployment overview
- Frontend on Vercel, root `frontend`, build `npm run build`, output `dist`.
- Backend on Render, root `backend`, build `pip install -r requirements.txt`, start `gunicorn app:app`.
- Set frontend `VITE_API_BASE_URL` to the deployed backend base URL ending in `/api/v1`.
- Set backend `FRONTEND_ORIGIN` to the deployed frontend origin.
- Set `ANTHROPIC_API_KEY` only if an AI integration is implemented; this MVP does not require it.
- PostgreSQL schema is supplied. Configure `DATABASE_URL` when DB persistence is integrated; local demo scenarios work without it.

## Limitations to explain honestly
- Forensic checks are heuristic indicators, not proof of tampering.
- OCR quality varies with scan quality, language, skew, and handwriting.
- Synthetic registry matches do not access government data.
- Signature and seal checks are not expert verification.
- Risk score is a screening heuristic, not a probability that a document is fake.
- Do not use real sensitive documents in an unapproved demo environment.


## MP Bhulekh reference and multilingual UI

- Reference portal: https://webgis2.mpbhulekh.gov.in/#/home
- The UI borrows land-record navigation concepts such as District → Tehsil → Village → Khasra and links users to the official portal for independent checking.
- The portal is a reference only. No official API, direct government database access, scraping, or government endorsement is claimed. Live record comparison must only be added through a documented and authorized data interface.
- Hindi (`hi`) is the default display language. Users can switch the UI to English, Marathi, Gujarati, Punjabi, Bengali, Tamil, Telugu, Kannada, Malayalam, Odia, or Urdu. The choice is saved in the browser for the next visit. The current prototype localizes the core navigation and common actions; technical findings returned by the backend may remain in the source language.
- Urdu uses right-to-left page direction. OCR is independent from UI language; Hindi OCR requires Tesseract's Hindi language data.


## 50-document synthetic reference matching (hackathon update)
The backend now bundles 50 generated synthetic PDFs and canonical reference fields under `backend/reference_dataset/`. Every PDF is visibly watermarked as synthetic and not a government record. Upload analysis attempts to match extracted identifiers to this local catalogue and returns field-by-field comparisons. This is a demo matching workflow only; no official MP Bhulekh integration is implemented. See `docs/synthetic-reference-dataset.md`.

To load the optional PostgreSQL catalogue, run `database/schema.sql`, then `database/seed_50_synthetic_documents.sql`. The running Flask API currently loads the JSON catalogue from the project files, so the benchmark matching works without PostgreSQL.
