# Tasks: Complaint Management

> **Legend**: [✓] = Completed | [ ] = Not started / Pending | [!] = Partially complete / Needs rework

---

## Module 1: Backend API & Database

### 1.1 Database Models
- [✓] Define `Complaint` ORM model with all 18 columns in `backend/models.py`
- [✓] Use SQLAlchemy 2.0 `DeclarativeBase` style
- [✓] Create SQLite database engine in `backend/database.py`
- [✓] Auto-create tables on FastAPI startup
- [✓] Test helper setup with in-memory SQLite

**Pending improvements:**
- [ ] Add indexes on `status`, `department`, `created_at` for query performance
- [ ] Add `User` model for authentication (Phase 1)
- [ ] Add `image_path` column for photo upload (Phase 1)
- [ ] Add `escalated` and `escalated_at` columns for SLA (Phase 2)

### 1.2 API Endpoints
- [✓] `GET /` — health check with response `{"message": "CivicAssist AI Backend Running"}`
- [✓] `GET /api/admin/health` — simple status check
- [✓] `GET /api/dashboard/stats` — aggregate complaint counts
- [✓] `POST /api/complaints/` — full submission pipeline (classify returns category+priority tuple)
- [✓] `GET /api/complaints/` — list all complaints
- [✓] `GET /api/complaints/{id}` — single complaint detail (returns 404 via HTTPException)
- [✓] `PUT /api/complaints/{id}/status` — update complaint status
- [✓] `GET /api/complaints/{id}/pdf` — download generated PDF as FileResponse
- [✓] `POST /api/complaints/{id}/dispatch-email` — dispatch complaint email via SMTP

**Pending improvements:**
- [ ] Add `DELETE /api/complaints/{id}` for admin use
- [ ] Add filtering/sorting query params to `GET /api/complaints/` (by status, department, date range)
- [ ] Add pagination to `GET /api/complaints/` (page + limit params)
- [ ] Add auth middleware to all admin endpoints (Phase 1)

### 1.3 Schema Validation
- [✓] `ComplaintCreate` — validates input with required + optional fields
- [✓] `ComplaintResponse` — shapes the POST response

**Pending:**
- [ ] Add phone number format validation (Indian mobile: 10 digits)
- [ ] Add email format validation (library `email-validator` exists in requirements.txt but is unused)
- [ ] Add character limits — `complaint_text` max 5000 chars, `citizen_name` max 100 chars

### 1.4 Database Helper Functions
- [!] `backend/db_helper.py` was **deleted** — standalone mode removed
- [✓] All CRUD now goes through FastAPI routers via `get_db()` dependency injection
- [✓] `create_complaint()` logic moved into `complaints.py` router
- [✓] `get_complaint_by_id()` logic moved into `complaints.py` router
- [✓] `update_complaint_status()` logic moved into `complaints.py` router

---

## Module 2: Services

### 2.1 AI Classifier (`backend/services/ai_classifier.py`)
- [✓] `classify(text, location)` returns `tuple[str, str]` — category and priority
- [✓] Ollama/Llama3 LLM-based classification when available (AI-first)
- [✓] Graceful fallback to keyword matching with expanded keyword set
- [✓] Returns all 6 categories: Pothole, Streetlight, Garbage, Water Leakage, Drainage Issue, Other
- [✓] Priority derivation from urgency keywords (danger/accident/emergency → High, minor/small → Low, else Medium)

**Issues to fix:**
- [!] LLM-based only — no ML model, no confidence scoring
- [!] Keyword fallback is still fragile for misspellings
- [!] Ollama endpoint has a 10s timeout — slow responses lead to fallback

**Phase 1 tasks:**
- [ ] Train scikit-learn TF-IDF + LogisticRegression model on seed data
- [ ] Save model + vectorizer as `.joblib` files
- [ ] Rewrite `classify()` to load model and return `(category, confidence, priority)`
- [ ] Add fallback to keyword matching if model files are missing
- [ ] Create `backend/data/training_data.json` with 30+ samples per category

### 2.2 AI Letter Generator (`backend/services/ai_generator.py`)
- [✓] `generate_letter()` calls Ollama/Llama3 at `AI_GENERATOR_BASE`
- [✓] Falls back to plain text template on connection failure
- [✓] Timeout set to 10 seconds

**Pending:**
- [ ] Add retry logic (3 attempts with exponential backoff)
- [ ] Improve prompt with GHMC-specific formatting instructions
- [ ] Add configurable model name (currently hardcoded to "llama3")

### 2.3 Department Router (`backend/services/router_service.py`)
- [✓] `route(category, priority_override=None)` — JSON lookup in `departments.json`
- [✓] `priority_override` overrides JSON-defined priority when provided (from classifier)
- [✓] Default fallback: Municipal Corporation, Medium priority
- [✓] Data file loaded once at module import time
- [✓] "Drainage Issue" entry added to `departments.json`

**Pending:**
- [ ] Add cache invalidation if JSON file changes at runtime (currently cached for process lifetime)
- [ ] Move routing data to database table for admin configurability (future)

### 2.4 PDF Generator (`backend/services/pdf_service.py`)
- [✓] `create_pdf(complaint_id, letter)` — creates PDF via ReportLab
- [✓] Auto-creates `backend/generated_pdfs/` directory
- [✓] Returns absolute file path

**Pending:**
- [ ] Improve PDF layout with letterhead, date block, signature line
- [ ] Add multi-page support for long complaint letters
- [ ] Serve PDF via FastAPI endpoint for frontend download (currently only saved to disk)

### 2.5 Email Service (`backend/services/email_service.py`)
- [✓] **Full SMTP implementation** with `smtplib` and STARTTLS
- [✓] Configurable via env vars: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`
- [✓] HTML email body with complaint details (complaint ID, category, citizen, location, priority)
- [✓] PDF attachment support (attaches generated PDF if file exists)
- [✓] Graceful fallback: logs to console when SMTP not configured
- [✓] Returns `True` on success, `False` on failure

**Pending:**
- [ ] Add HTML email template with proper branding
- [ ] Add retry logic on SMTP failure (3 attempts)

---

## Module 3: Streamlit Frontend

### 3.1 Navigation & Theme
- [✓] Sidebar navigation with 5 page links
- [✓] Shared CSS theme (DM Sans, navy sidebar, card system, badges)
- [✓] Google Fonts integration
- [✓] Responsive layout with `layout="wide"`

**Pending:**
- [ ] Move shared CSS to a single importable file (currently duplicated on every page)
- [ ] Add dark mode toggle
- [ ] Add mobile-responsive sidebar collapse

### 3.2 Home Dashboard (`app.py`)
- [✓] Hero section with AI branding
- [✓] 4 KPI stat cards: Total, Resolved, Pending, High Priority
- [✓] Trends line chart (last 90 days)
- [✓] Department distribution pie chart
- [✓] Recent complaints table (top 8)
- [✓] Auto-refresh every 10 seconds
- [✓] Footer with version info
- [✓] "Powered by Anthropic Claude" changed to "Powered by AI"
- [✓] Removed `db_helper` import — always uses API
- [✓] `API_BASE` default changed to `http://localhost:8001`

**Pending:**
- [ ] Handle empty state gracefully (currently shows warning and stops)

### 3.3 Report Issue (`pages/1_Report_Issue.py`)
- [✓] Complaint text area with placeholder
- [✓] Voice recorder with English + Telugu transcription
- [✓] Audio saved as WEBM + WAV to `recorded_audio/`
- [✓] Location search via Nominatim (text + dropdown + map click)
- [✓] 80+ Hyderabad area presets
- [✓] Folium interactive map with click-to-select
- [✓] AI Detection Preview panel (keyword-based)
- [✓] Real-time category/department/priority display
- [✓] Progress step indicator (4 steps)
- [✓] Civic chatbot (English + Telugu, rule-based, SLA queries)
- [✓] Chatbot voice input (Telugu supported)
- [✓] **Submit button now persists!** Calls `POST /api/complaints/` with all fields
- [✓] **Separate Phone and Email fields** (was combined "Phone / Email")
- [✓] **Input validation** — checks for empty location and empty complaint text before submitting
- [✓] **Error handling** — backend connection errors shown to user
- [✓] **PDF/Email buttons** now redirect to AI Complaint View instead of simulating

**Phase 1 tasks:**
- [ ] Add photo upload widget (see Phase 1 feature)

### 3.4 Complaint History (`pages/2_Complaint_History.py`)
- [✓] Data fetching from API (cached 10s) — standalone mode removed
- [✓] Free-text search across all fields
- [✓] Status dropdown filter
- [✓] Department dropdown filter
- [✓] Priority dropdown filter
- [✓] Pagination (12 per page) with prev/next
- [✓] Summary badges (count per status)
- [✓] Detail popup with full info + progress timeline
- [✓] Connection error handling with user-facing message
- [✓] `API_BASE` default changed to `http://localhost:8001`

**Pending:**
- [ ] Add export to CSV button
- [ ] Add date range filter
- [ ] Add column sorting by clicking headers
- [ ] Show citizen contact info in detail popup

### 3.5 Admin Dashboard (`pages/3_Admin_Dashboard.py`)
- [✓] 4 KPI cards: Total, Resolution Rate (%), Avg Resolve Time, High Priority Open
- [✓] Full complaint table with status update
- [✓] Status update via dropdown + button (calls `PUT /api/complaints/{id}/status`)
- [✓] Weekly trends stacked bar chart
- [✓] Top categories horizontal bar chart
- [✓] Department performance bars
- [✓] Hotspot map (Plotly Mapbox)
- [✓] Removed `db_helper` import — always uses API
- [✓] Connection error handling with user-facing message

**Issues to fix:**
- [!] Average resolve time always shows 0.0 — the "Resolve Days" column is never populated
- [!] Hotspot map only shows 12 hardcoded locations — needs full coordinate support
- [ ] Hotspot map uses Plotly Mapbox (requires Mapbox token) — may fail without one

### 3.6 AI Complaint View (`pages/4_AI_Complaint_View.py`)
- [✓] Complaint selector dropdown
- [✓] "Generate AI Letter" button (template-based)
- [✓] Meta pills: ID, category, priority, date, department
- [✓] 4 action buttons: Copy, Download PDF, Dispatch Email, New Letter
- [✓] Dispatch status indicators (Classified, Routed, Generated, Email)
- [✓] Formal letter card with serif font + watermark + stamp
- [✓] Removed `db_helper` import — always uses API
- [✓] **Download PDF works** — calls `GET /api/complaints/{cid}/pdf` and provides download link
- [✓] **Dispatch Email works** — calls `POST /api/complaints/{cid}/dispatch-email` with success/error handling
- [✓] **Email status reflects actual `email_sent` field** from database (green if sent, amber if pending)

---

## Module 4: Testing

### 4.1 Existing Tests (`tests/test_backend.py`) — 7 tests
- [✓] `test_root` — health check
- [✓] `test_admin_health` — admin health
- [✓] `test_dashboard_stats_empty` — empty stats
- [✓] `test_complaints_empty` — empty list
- [✓] `test_get_nonexistent_complaint` — 404 case (expects `{"detail": "Complaint not found"}`)
- [✓] `test_update_status_nonexistent_complaint` — 404 case (expects `{"detail": "Complaint not found"}`)
- [✓] `test_submit_complaint` — full integration with mocks (classify returns tuple, route accepts two args)

### 4.2 Tests to Add
- [ ] Test complaint creation with all fields (including lat/lng)
- [ ] Test complaint creation with minimal fields
- [ ] Test status update to each valid status (Assigned, In Progress, Resolved, Rejected)
- [ ] Test status update with invalid status value
- [ ] Test duplicate complaint_id scenario
- [ ] Test PDF download endpoint (200 + 404 cases)
- [ ] Test email dispatch endpoint (success + failure cases)
- [ ] Test `ai_classifier.classify()` for all categories + edge cases (empty string, special chars, LLM response parsing)
- [ ] Test `router_service.route()` for all categories + unknown + priority override
- [ ] Test `ai_generator.generate_letter()` — success path + fallback path
- [ ] Test `pdf_service.create_pdf()` — verify file created, verify file is valid PDF
- [ ] Test `ComplaintCreate` schema validation failures (missing required fields)

---

## Module 5: Configuration & DevOps

### 5.1 Environment & Deployment
- [✓] `.env.example` with API_BASE, AI_GENERATOR_BASE, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
- [✓] `Dockerfile` — single-stage build, runs Streamlit on port 8501
- [✓] `.gitlab-ci.yml` — 6 stages: format → lint → type_check → security → test → coverage
- [✓] `.pre-commit-config.yaml` — 10 hooks (ruff, mypy, gitleaks, bandit, pyupgrade, flake8, pylint, vulture, semgrep)
- [✓] `.dockerignore`
- [✓] `.editorconfig`

**Pending:**
- [ ] Add `docker-compose.yml` with FastAPI + Streamlit + Ollama services
- [ ] Add PostgreSQL support (optional, via env var)
- [ ] Add healthcheck to Dockerfile
- [ ] Add `.env` to `.gitignore` (currently not listed — risk of creds exposure)

### 5.2 Linting & Formatting
- [✓] Ruff config in `pyproject.toml` and `.ruff.toml`
- [✓] Line length: 100
- [✓] Quote style: double
- [✓] Target: Python 3.11
- [✓] Lint rules: E, W, F, I, B, S

**Pending:**
- [ ] Reduce ignore rules (currently ignoring E501 despite Ruff's 100-char limit)

### 5.3 Type Checking
- [✓] MyPy config in `pyproject.toml`
- [✓] `ignore_missing_imports = true` (needed for Streamlit, ReportLab, etc.)
- [✓] `warn_return_any = true`

**Pending:**
- [ ] Add type annotations to all function signatures in backend services
- [ ] Add type annotations to Streamlit page functions

---

## Module 6: Documentation

### 6.1 Project Documentation
- [✓] `README.md` — project overview
- [✓] `AGENTS.md` — logical agent definitions
- [✓] `USER_MANUAL.md` — end-user guide
- [✓] `CHANGELOG.md` — release history (managed via cliff)
- [✓] `CONTRIBUTING.md` — contribution guidelines
- [✓] `CODE_OF_CONDUCT.md` — community standards
- [✓] `SECURITY.md` — security policy
- [✓] `LICENSE` — AGPLv3
- [✓] `specs/complaint-management/plan.md` — technical plan
- [✓] `specs/complaint-management/spec.md` — feature spec
- [✓] `specs/complaint-management/tasks.md` — task tracking

### 6.2 Documentation Updates Needed
- [ ] `AGENTS.md` — update Agent 1 (classifier) to reflect AI-powered classification
- [ ] `AGENTS.md` — update Agent 5 (email) to reflect SMTP implementation
- [ ] `USER_MANUAL.md` — update with correct information about working features
- [ ] Add API documentation (can generate via FastAPI's built-in Swagger at `/docs`)

---

## Module 7: Future Roadmap Tasks

### Phase 1 — Core Fixes & MVP Completion

**Priority: Critical — Most resolved in current changes**

| # | Task | Status | Est. Effort |
|---|------|--------|-------------|
| 1 | Wire "Submit Complaint" button to API endpoint | ✓ Done | 1 day |
| 2 | Wire "Generate PDF" and "Download PDF" to `pdf_service.create_pdf()` + API | ✓ Done | 0.5 day |
| 3 | Wire "Send Email" and "Dispatch Email" to real SMTP email service | ✓ Done | 1 day |
| 4 | Remove "Powered by Anthropic Claude" from app.py footer | ✓ Done | 0.1 day |
| 5 | Harmonize CATEGORY_MAP (page 1) with backend ai_classifier | ✓ Done | 0.5 day |
| 6 | Add "Drainage Issue" category to `departments.json` and `ai_classifier.py` | ✓ Done | 0.5 day |

**Priority: High**

| # | Task | Dependencies | Est. Effort |
|---|------|-------------|-------------|
| 7 | User authentication — User model, signup/login, session management | None | 2 days |
| 8 | ML classifier — scikit-learn model training + integration | None | 2 days |
| 9 | Photo upload — model column, upload endpoint, frontend widget | None | 1.5 days |
| 10 | Add form validation (phone format, email format, character limits) | None | 0.5 day |
| 11 | Populate "Resolve Days" in Admin Dashboard | None | 0.5 day |

### Phase 2 — Notifications & SLA

**Priority: Medium**

| # | Task | Dependencies | Est. Effort |
|---|------|-------------|-------------|
| 12 | Real SMTP email notifications on status change | None | 1 day |
| 13 | Twilio SMS notifications on status change | None | 1 day |
| 14 | SLA auto-escalation — background check for stuck complaints | None | 1.5 days |
| 15 | Add extensive test coverage (see Module 4.2) | None | 2 days |
| 16 | Add database indexes for performance | None | 0.5 day |

### Phase 3 — Scale & Production

**Priority: Low**

| # | Task | Dependencies | Est. Effort |
|---|------|-------------|-------------|
| 17 | PostgreSQL migration | None | 2 days |
| 18 | API authentication (JWT or API keys) | #7 | 1 day |
| 19 | WhatsApp bot integration | None | 3 days |
| 20 | Multi-language expansion (Hindi, Tamil, Kannada) | None | 3 days |
| 21 | Public heatmap dashboard | None | 1 day |
| 22 | docker-compose with FastAPI + Streamlit + Ollama | None | 0.5 day |

---

## Completion Summary

### Total Tasks
- **Completed (✓)**: ~75 tasks
- **Not Started / Pending ( )**: ~20 tasks
- **Partially Complete / Needs Rework (!)**: ~8 tasks
- **Future Roadmap**: ~16 tasks

### Critical Path — Now Complete
The following critical tasks were the most important and are now **resolved**:

1. **Task #1** — Submit Complaint button now calls the API and persists to database
2. **Task #2** — PDF Download works via API endpoint
3. **Task #3** — Email Dispatch works via SMTP
4. **Task #4** — Removed false "Powered by Anthropic Claude" branding
5. **Task #5** — Harmonized routing/classification between page 1 and backend
6. **Task #6** — Added "Drainage Issue" category

### Known Technical Debt
1. Shared CSS duplicated across 5 pages (5 × ~80 lines = 400 lines of identical CSS)
2. No error handling for Nominatim API failures (free tier can be rate-limited)
3. `print()` still used instead of proper logging in some paths
4. No database migration system — schema changes require manual alter or DB delete
5. `streamlit-folium` reruns on every map interaction, causing performance issues
6. `db_helper.py` deleted — standalone mode no longer supported (API-only architecture)
