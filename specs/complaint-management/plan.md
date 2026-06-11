# Plan: Complaint Management

## Technical Architecture

### System Overview

CivicAssist AI follows a **Python client-server architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Frontend                     │
│  app.py (Home)   │ pages/1-4 (Report, History, Admin,   │
│                  │         AI View)                      │
├─────────────────────────────────────────────────────────┤
│               HTTP (requests to FastAPI)                 │
├─────────────────────────────────────────────────────────┤
│                    FastAPI Backend                        │
│                    routers/ complaints.py                 │
│                    routers/ dashboard.py                  │
│                    routers/ admin.py                      │
├─────────────────────────────────────────────────────────┤
│                    SQLite DB                             │
└─────────────────────────────────────────────────────────┘
```

All Streamlit pages communicate exclusively with the FastAPI backend over HTTP. The standalone `db_helper.py` mode has been removed — there is no direct DB access from the frontend.

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Streamlit | ≥1.32.0 | UI framework — all pages, charts, forms |
| Backend API | FastAPI + Uvicorn | ≥0.115.0 | REST API for complaint CRUD |
| ORM | SQLAlchemy | ≥2.0.0 | Object-relational mapping |
| Database | SQLite | — | Embedded single-file database |
| Validation | Pydantic | ≥2.0.0 | Request/response schema validation |
| PDF | ReportLab | ≥4.0.0 | PDF generation for complaint letters |
| LLM Client | Ollama (Llama 3) | — | AI classification + letter generation (optional) |
| Voice STT | Google Speech API (via SpeechRecognition) | — | Speech-to-text for voice complaints |
| Maps | Folium + OpenStreetMap + Nominatim | — | Location search and map interaction |
| Charts | Plotly | ≥5.18.0 | Interactive charts (trends, pies, bars) |
| Audio | pydub + static-ffmpeg | — | Audio format conversion |
| Language | Python | 3.11 | Runtime |

### Dependencies

**Core (requirements.txt):**
```
streamlit, pandas, numpy, plotly
fastapi, uvicorn, sqlalchemy, pydantic
requests, reportlab, python-multipart, email-validator
folium, streamlit-folium, Pillow
SpeechRecognition, streamlit-mic-recorder, static-ffmpeg, pydub
```

**Dev tooling:**
```
ruff (linter + formatter), mypy (type checker)
pytest + pytest-cov (testing + coverage)
pre-commit (git hooks: ruff, mypy, gitleaks, bandit, pyupgrade, flake8, pylint, vulture, semgrep)
```

---

## Database Design

### Current Schema

**Table: `complaints`**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | PK, AUTOINCREMENT | Internal row ID |
| `complaint_id` | VARCHAR | UNIQUE | Public-facing ID (UUID[:8], e.g. "a1b2c3d4") |
| `citizen_name` | VARCHAR | | User-supplied or "Anonymous" |
| `email` | VARCHAR | | User-supplied or default |
| `phone` | VARCHAR | | User-supplied or default |
| `issue_category` | VARCHAR | | From classifier: Pothole, Garbage, etc. |
| `complaint_text` | VARCHAR | | Raw user complaint |
| `generated_letter` | VARCHAR | | Formatted complaint letter text |
| `department` | VARCHAR | | Mapped via departments.json |
| `department_email` | VARCHAR | | |
| `priority` | VARCHAR | | High/Medium/Low |
| `location` | VARCHAR | | Free-text location description |
| `latitude` | FLOAT | | From Nominatim geocoding or map click |
| `longitude` | FLOAT | | |
| `status` | VARCHAR | | Submitted / Assigned / In Progress / Resolved / Rejected |
| `email_sent` | BOOLEAN | | Whether the complaint was emailed to the department |
| `pdf_path` | VARCHAR | | File path to generated PDF |
| `created_at` | DATETIME | | UTC timestamp of creation |
| `updated_at` | DATETIME | | UTC timestamp of last update |

**No indexes exist beyond PRIMARY KEY and UNIQUE on complaint_id.** For 10K+ rows, consider adding indexes on `status`, `department`, `created_at`.

### Data Directory Structure

```
backend/
├── data/
│   └── departments.json         # Category → department routing map
├── generated_pdfs/              # ReportLab PDF output directory
│   └── {complaint_id}.pdf
├── complaints.db                # SQLite database file
└── services/
    ├── ai_classifier.py
    ├── ai_generator.py
    ├── router_service.py
    ├── pdf_service.py
    └── email_service.py
```

### departments.json Structure

```json
{
  "Pothole":         { "department": "Roads Department",        "email": "roads@demo.gov",     "priority": "High" },
  "Streetlight":     { "department": "Electricity Department",   "email": "electricity@demo.gov","priority": "Medium" },
  "Garbage":         { "department": "Sanitation Department",    "email": "sanitation@demo.gov","priority": "High" },
  "Water Leakage":   { "department": "Water Works Department",   "email": "water@demo.gov",     "priority": "High" },
  "Drainage Issue":  { "department": "Drainage Department",      "email": "drainage@demo.gov",  "priority": "Medium" }
}
```

All 5 categories from AGENTS.md are now mapped. Unknown categories fall back to Municipal Corporation.

---

## API Structure

### Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| GET | `/` | `root()` | Health check |
| GET | `/api/admin/health` | `health()` | Admin health check |
| GET | `/api/dashboard/stats` | `stats()` | Aggregate counts: total, resolved, pending, high_priority |
| POST | `/api/complaints/` | `submit_complaint()` | Full pipeline: classify → route → generate → PDF → save |
| GET | `/api/complaints/` | `get_complaints()` | List all complaints |
| GET | `/api/complaints/{id}` | `get_complaint_by_id()` | Single complaint detail |
| PUT | `/api/complaints/{id}/status` | `update_complaint_status()` | Update status field |
| GET | `/api/complaints/{id}/pdf` | `download_pdf()` | Download generated PDF file |
| POST | `/api/complaints/{id}/dispatch-email` | `dispatch_email()` | Send complaint email to department |

### Request/Response Shapes

**POST /api/complaints/**
```
Request:
{
  "citizen_name": "string (required)",
  "email": "string (required)",
  "phone": "string (required)",
  "complaint_text": "string (required)",
  "location": "string (required)",
  "latitude": "float (optional)",
  "longitude": "float (optional)"
}

Response:
{
  "complaint_id": "string (UUID[:8])",
  "category": "string",
  "department": "string",
  "priority": "string (High|Medium|Low)",
  "generated_letter": "string"
}
```

**GET /api/complaints/** — returns `[ComplaintObject]` where ComplaintObject includes all fields from the `complaints` table plus `created_at` and `updated_at` as strings.

**GET /api/complaints/{id}** — same shape as single item above, or 404 `{"detail": "Complaint not found"}`.

**PUT /api/complaints/{id}/status**
```
Request:  {"status": "Submitted|Assigned|In Progress|Resolved|Rejected"}
Response: {"message": "Status updated successfully", "complaint_id": "...", "new_status": "..."}
         OR 404 {"detail": "Complaint not found"}
```

**GET /api/complaints/{id}/pdf** — returns PDF as `FileResponse` with `application/pdf` content type, or 404.

**POST /api/complaints/{id}/dispatch-email**
```
Response: {"message": "Email dispatched", "complaint_id": "...", "success": true}
         OR {"message": "Email dispatch failed", "complaint_id": "...", "success": false}
```

---

## Module Architecture

### backend/main.py — Application Entry Point
- Creates all database tables on startup via `Base.metadata.create_all(bind=engine)`
- Creates FastAPI app with title "CivicAssist AI"
- Registers three routers with prefixes
- Adds CORS middleware (allows all origins)

### backend/database.py — Database Engine
- SQLite engine with `check_same_thread=False` (required for SQLAlchemy with SQLite)
- Session factory (`SessionLocal`) with `autocommit=False, autoflush=False`
- `get_db()` dependency generator for FastAPI routes

### backend/models.py — ORM Models
- Single `Complaint` model mapped to `complaints` table
- Uses SQLAlchemy 2.0 `DeclarativeBase` style (not the old `declarative_base()` function)

### backend/schemas.py — Pydantic Models
- `ComplaintCreate` — input validation for complaint submission
- `ComplaintResponse` — output shape for the POST response

### backend/routers/ — API Route Handlers

**complaints.py** (9 endpoints):
- Full pipeline at POST: classify (returns category + priority) → route → generate letter → create PDF → save
- GET endpoints return all complaint fields
- Status update at PUT
- PDF download endpoint (serves file from disk)
- Email dispatch endpoint (calls `email_service.send_email`, marks `email_sent=True`)
- 404 errors use `HTTPException` (proper HTTP error responses)

**dashboard.py** (1 endpoint):
- Aggregation queries: total, resolved, pending, high_priority counts

**admin.py** (1 endpoint):
- Simple health check

### backend/services/ — Business Logic Modules

**ai_classifier.py**:
- `classify(text, location)` → `tuple[str, str]` (category, priority)
- **AI-first**: Tries Ollama/Llama3 with a prompt requesting both category and priority
- Falls back to keyword matching with expanded keyword set
- Priority derived from urgency words in text (danger/accident/emergency → High, minor/small → Low, else Medium)
- Categories: Pothole, Streetlight, Garbage, Water Leakage, Drainage Issue, Other

**ai_generator.py**:
- `generate_letter(category, location, description)` → str
- Calls `{AI_GENERATOR_BASE}/api/generate` with `model:"llama3"`
- Falls back to plain template: `"Complaint regarding {category} at {location}\n\nDescription:\n{description}"`

**router_service.py**:
- `route(category, priority_override=None)` → dict with keys: department, email, priority
- Loads `departments.json` at module import time
- `priority_override` overrides the JSON-defined priority when provided
- Default fallback: "Municipal Corporation", "municipal@demo.gov", "Medium"

**pdf_service.py**:
- `create_pdf(complaint_id, letter)` → file path string
- Creates directory `backend/generated_pdfs/` if it doesn't exist
- Uses ReportLab `SimpleDocTemplate` with a single `Paragraph`
- Returns absolute path to the generated PDF

**email_service.py**:
- `send_email(receiver, subject, body, pdf_path)` → bool
- **Full SMTP implementation** using `smtplib` with STARTTLS
- Configurable via env vars: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`
- HTML email body with PDF attachment support
- Graceful fallback: logs to console when SMTP not configured
- Returns `True` on success, `False` on failure

---

## Streamlit Page Architecture

### Page Structure

```
app.py                              # Home Dashboard (entry point)
pages/
├── 1_Report_Issue.py               # Complaint submission form + chatbot
├── 2_Complaint_History.py          # Search, filter, paginate, detail
├── 3_Admin_Dashboard.py            # KPIs, charts, status management
└── 4_AI_Complaint_View.py          # Letter review, PDF, email dispatch
```

### Navigation & Sidebar
- Every page includes an identical sidebar with 5 page links
- Sidebar also shows project branding: "CivicAssist AI · Citizen Services Platform"
- Footer: "v2.4.1 · © 2025 CivicAssist"

### Data Fetching
- All pages use `requests.get(f"{API_BASE}/api/complaints/")` exclusively
- No direct DB access — `db_helper.py` has been removed
- `API_BASE` defaults to `http://localhost:8001`
- `st.cache_data(ttl=10)` on data-fetching functions — auto-refreshes every 10 seconds

### State Management
- `st.session_state` used for: complaint input text, voice recording state, map coordinates, chatbot messages, pagination page numbers, generated letters
- Session state is **in-memory only** — cleared on browser refresh

### Shared CSS Theme
- Font: DM Sans (body) + Playfair Display (headings) — loaded via Google Fonts
- Colors: Navy (#0A1628) sidebar, Blue (#1A56DB) accents, various badge colors
- Components: ca-card, stat-card, badge, hero, section-header, letter-card, notif-success/error
- All styling is hardcoded as `st.markdown("<style>...</style>")` on each page (no shared CSS file)

---

## Data Flow Diagram

### Submission Pipeline

```
User → Enter complaint in pages/1_Report_Issue.py → Click Submit
  │
  └─► POST /api/complaints/
        │
        ├─► ai_classifier.classify(text, location)  → ("Pothole", "High")
        ├─► router_service.route("Pothole", "High") → {"department":"Roads","email":"roads@demo.gov","priority":"High"}
        ├─► generate UUID (first 8 chars)
        ├─► ai_generator.generate_letter(...)        → "Dear Sir/Madam, ..."
        ├─► pdf_service.create_pdf(id, letter)       → "/backend/generated_pdfs/a1b2c3d4.pdf"
        └─► Complaint ORM → INSERT → SQLite
        │
        ◄── Response: {complaint_id, category, department, priority, generated_letter}
```

### PDF Download Flow

```
User clicks "Download PDF" in pages/4_AI_Complaint_View.py
  │
  └─► GET /api/complaints/{cid}/pdf
        │
        └─► FileResponse(pdf_path, media_type="application/pdf")
```

### Email Dispatch Flow

```
User clicks "Dispatch Email" in pages/4_AI_Complaint_View.py
  │
  └─► POST /api/complaints/{cid}/dispatch-email
        │
        ├─► email_service.send_email(department_email, subject, html_body, pdf_path)
        │     ├─► SMTP connect → STARTTLS → login → send
        │     └─► If success: complaint.email_sent = True, db.commit()
        └─► Response: {success: true/false}
```

### Tracking Flow

```
Admin Dashboard (pages/3_Admin_Dashboard.py)
  │
  ├─► Select complaint from dropdown
  ├─► Select new status from dropdown
  └─► PUT /api/complaints/{id}/status
       │
       └─► Query complaint → set status → commit
```

---

## Testing Strategy

### Test Framework
- pytest with pytest-cov for coverage
- In-memory SQLite (`sqlite:///:memory:`) with `StaticPool` for test isolation
- FastAPI `TestClient` for HTTP-level testing
- Dependency overrides: production `get_db` replaced with test `get_db` using in-memory engine

### Test Fixture
```python
@pytest.fixture(autouse=True)
def setup_db():
    backend.models.Base.metadata.drop_all(bind=engine)
    backend.models.Base.metadata.create_all(bind=engine)
    yield
```

### Existing Tests (7 total)
- `test_root` — health check
- `test_admin_health` — admin endpoint
- `test_dashboard_stats_empty` — stats with no data
- `test_complaints_empty` — list with no data
- `test_get_nonexistent_complaint` — 404 with `{"detail": "Complaint not found"}`
- `test_update_status_nonexistent_complaint` — 404 with `{"detail": "Complaint not found"}`
- `test_submit_complaint` — full integration (with mocked classify returning tuple, route accepting two args)

### Test Coverage
- Run: `pytest --cov=backend --cov-report=term-missing --cov-report=xml`
- Coverage threshold: Not enforced (currently partial — covers routes, not services)

---

## CI/CD Pipeline (GitLab CI)

Six stages run sequentially:

1. **format** — `ruff format --check .`
2. **lint** — `ruff check .`
3. **type_check** — `mypy backend --ignore-missing-imports`
4. **security** — bandit (SAST), gitleaks (secrets), pip-audit (dependencies)
5. **test** — `pytest`
6. **coverage** — `pytest --cov=backend --cov-report=xml --cov-report=term`

---

## Deployment

### Docker
- `python:3.11-slim` base image
- Exposes port 8501
- Entrypoint: `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`
- The Docker image only runs the Streamlit frontend, NOT the FastAPI backend
- To run FastAPI alongside, a second container or docker-compose is needed

### Environment Variables
- `API_BASE` — FastAPI backend URL (default: `http://localhost:8001`)
- `AI_GENERATOR_BASE` — Ollama server URL (default: `http://localhost:11434`)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` — Email dispatch config

### Pre-commit Hooks
- ruff, ruff-format, mypy, gitleaks, bandit (on `backend/`), pyupgrade, flake8, pylint, vulture, semgrep

---

## Key Implementation Status

### Resolved Gaps

1. **Submit button now persists** — `pages/1_Report_Issue.py` submit button calls `POST /api/complaints/` with all form fields. Complaints are created in the database through the full pipeline.

2. **Email service implemented** — `backend/services/email_service.py` now has real SMTP integration via `smtplib` with STARTTLS, configurable env vars, HTML body, and PDF attachments. Falls back to logging when SMTP not configured.

3. **Classifier is AI-powered** — `ai_classifier.py` now uses Ollama/Llama3 for LLM-based classification when available. Falls back to improved keyword matching. Returns `(category, priority)` tuple.

4. **"Drainage Issue" added** — Both in `departments.json` and `ai_classifier.py`.

5. **"Powered by Anthropic Claude" removed** — Footer now says "Powered by AI".

6. **PDF download works** — `GET /api/complaints/{id}/pdf` endpoint serves the generated PDF as a downloadable file.

7. **Email dispatch works** — `POST /api/complaints/{id}/dispatch-email` sends the complaint email via SMTP and marks `email_sent=True`.

### Remaining Gaps

1. **Hotspot map**: Only 12 hardcoded Hyderabad locations have coordinates.
2. **Average resolve time**: Always shows 0.0d — the feature was never implemented.
3. **No authentication**: All endpoints are public with no auth required.
4. **No ML classifier**: Falls back to keyword matching when Ollama is unavailable.
5. **No photo upload**: Image attachment not yet supported.

---

## Future Enhancements (Roadmap)

These features are planned but NOT yet specified or implemented:

### Phase 1 (Near-term)
1. **User Authentication** — User model, signup/login endpoints, session management, "My Complaints" page
2. **ML Classifier** — scikit-learn TF-IDF + LogisticRegression to replace keyword matching, with confidence scores
3. **Photo Upload** — Image attachment per complaint, stored in `uploads/`, displayed in detail views

### Phase 2 (Medium-term)
4. **Email Notifications** — Real SMTP integration with HTML templates and PDF attachments
5. **SMS Notifications** — Twilio integration for SMS status alerts
6. **SLA Auto-Escalation** — Background check for complaints stuck beyond SLA limits per priority

### Phase 3 (Long-term)
7. **PostgreSQL Migration** — Replace SQLite for concurrent multi-user production use
8. **WhatsApp Bot Integration** — Submit and track via WhatsApp (highly relevant for Indian users)
9. **Public Heatmap Dashboard** — Anonymized public view of complaint hotspots
10. **Multi-language Expansion** — Hindi and additional regional languages
