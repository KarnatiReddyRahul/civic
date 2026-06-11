# Spec: Complaint Management

## Overview

CivicAssist AI is an AI-powered citizen grievance management platform. Citizens submit complaints about civic issues (potholes, garbage, water leakage, streetlights, drainage), which are automatically classified, routed to the responsible government department, converted into a formal complaint letter, packaged as a PDF, and dispatched via email — all in one pipeline. Citizens and administrators can then track the complaint through its lifecycle: Submitted → Assigned → In Progress → Resolved.

The platform operates in a **client-server architecture**: the Streamlit frontend communicates with the FastAPI backend over HTTP. There is no standalone/dual-mode — all pages connect to the API exclusively.

---

## Business Goals

1. **Reduce friction** — Citizens should be able to report an issue in under 2 minutes with no account required.
2. **Automate routing** — Eliminate manual triage by automatically detecting the issue type and assigning it to the correct department.
3. **Formalize complaints** — Generate legally-appropriate formatted complaint letters suitable for government records.
4. **Enable transparency** — Citizens and administrators can track status at every stage of the lifecycle.
5. **Scale to cities** — Support hundreds of concurrent complaints without performance degradation.

---

## User Personas

### Citizen (Primary)
- Demographics: Urban resident of Hyderabad, Telangana; comfortable with basic smartphone apps; may prefer voice input in English or Telugu.
- Goal: Report a civic issue quickly and track its resolution without visiting a government office.
- Pain point: Existing systems (phone calls, in-person visits) are slow and non-transparent.

### Administrator (Secondary)
- Demographics: GHMC municipal staff member responsible for complaint triage and resolution.
- Goal: View all complaints in one place, update statuses, monitor department performance, identify hotspots.
- Pain point: No centralized dashboard exists today; complaints arrive via multiple disconnected channels.

---

## Functional Requirements

### FR1: Complaint Submission
- **ID**: FR1
- **Description**: Citizen can submit a complaint with descriptive text, location, and optional contact details.
- **Input fields**: Complaint text (required), location (required — via text search or map click), citizen name (optional), phone (optional), email (optional), voice recording (optional — transcribed to text).
- **Validation**: Complaint text must be at least 10 characters; location must resolve to valid coordinates.
- **Backend**: Submits via `POST /api/complaints/` to the FastAPI backend.
- **Acceptance**: See FR1-AC below.

### FR2: AI Classification
- **ID**: FR2
- **Description**: Submitted complaint text is automatically classified into an issue category and assigned a priority level.
- **Categories**: Pothole, Streetlight, Garbage, Water Leakage, Drainage Issue, Other.
- **Priorities**: High, Medium, Low.
- **Current implementation**: AI-first — calls Ollama/Llama3 for LLM-based classification when available; falls back to keyword matching with expanded keywords. Returns `(category, priority)` tuple.
- **Priority derivation**: Urgency keywords (danger, accident, school, hospital, etc.) map to High; minor keywords (slight, small) map to Low; otherwise Medium.
- **Planned upgrade**: scikit-learn TF-IDF + LogisticRegression model (see future roadmap).
- **Acceptance**: Classification runs in <2s (LLM) or <500ms (keyword fallback).

### FR3: Department Routing
- **ID**: FR3
- **Description**: Each classified category is mapped to a government department, contact email, and priority level.
- **Data source**: `backend/data/departments.json`.
- **Override**: The classifier-derived priority can override the JSON-defined priority via `route(category, priority_override)`.
- **Acceptance**: Unknown categories route to "Municipal Corporation" with Medium priority.

### FR4: Complaint Letter Generation
- **ID**: FR4
- **Description**: A formal complaint letter is generated from the complaint text, category, and location.
- **Implementation**: Calls Ollama/Llama3 (`AI_GENERATOR_BASE`) with a prompt; falls back to a plain text template.
- **Acceptance**: Letter includes date, citizen name, addressee, subject line, issue description, and request for action.

### FR5: PDF Generation
- **ID**: FR5
- **Description**: The generated letter is converted to a PDF document using ReportLab.
- **Storage**: `backend/generated_pdfs/{complaint_id}.pdf`.
- **Download**: `GET /api/complaints/{id}/pdf` serves the file with `application/pdf` content type.
- **Acceptance**: PDF is valid and opens in any PDF reader.

### FR6: Complaint Tracking
- **ID**: FR6
- **Description**: Status can be updated through lifecycle stages: Submitted → Assigned → In Progress → Resolved (also Rejected).
- **Endpoint**: `PUT /api/complaints/{id}/status`.
- **Acceptance**: Status updates are persisted immediately and visible on next page load.

### FR7: Dashboard & Analytics
- **ID**: FR7
- **Description**: Home dashboard shows KPIs (total, resolved, pending, high-priority), complaint trends chart, department distribution pie chart, and recent complaints table.
- **Refresh**: Auto-refresh every 10 seconds (cached).
- **Acceptance**: All charts render with live data from the database.

### FR8: Admin Management
- **ID**: FR8
- **Description**: Admin dashboard shows KPI cards, a full complaint table with status update controls, weekly trends, top categories, department performance bars, and a hotspot map.
- **Statuses available for update**: Submitted, Assigned, In Progress, Resolved, Rejected.
- **Status update**: Calls `PUT /api/complaints/{id}/status` via HTTP.
- **Acceptance**: Status changes are reflected immediately across all dashboard views.

### FR9: Complaint History & Search
- **ID**: FR9
- **Description**: Citizens can search, filter, and paginate through all complaints. Clicking a complaint shows full detail with a progress timeline.
- **Data source**: `GET /api/complaints/` — no standalone DB path.
- **Filters**: Free-text search, status dropdown, department dropdown, priority dropdown.
- **Pagination**: 12 complaints per page.
- **Acceptance**: Filters work in combination and results update instantly.

### FR10: Voice Input
- **ID**: FR10
- **Description**: Citizens can record their complaint via microphone. Audio is transcribed to text using Google Speech Recognition and appended to the complaint text field.
- **Languages**: English (en-US), Telugu (te-IN).
- **Storage**: Raw audio saved to `recorded_audio/` as both `.webm` and `.wav`.
- **Acceptance**: Transcription accuracy is at least 80% for clear speech.

### FR11: AI Complaint Letter View
- **ID**: FR11
- **Description**: Dedicated page to review, copy, download, and dispatch AI-generated complaint letters. Shows meta pills (ID, category, priority, date, department), dispatch status indicators, and the rendered letter in a serif-font card with watermark.
- **Actions**: Copy to clipboard, Download PDF (via `GET /api/complaints/{id}/pdf`), Dispatch Email (via `POST /api/complaints/{id}/dispatch-email`), New Letter (reset).
- **Email status**: Dispatch indicator reflects actual `email_sent` field from the database.
- **Acceptance**: All four buttons work end-to-end.

### FR12: Civic Chatbot
- **ID**: FR12
- **Description**: Rule-based chatbot answering SLA-related questions about complaint resolution timelines. Supports English and Telugu.
- **Data source**: `departments.json` for department names and priority-based SLA times.
- **SLA defaults**: High = 2-3 days, Medium = 5-7 days, Low = 7-10 days.
- **Input**: Text or voice (Telugu microphone supported on chatbot).
- **Acceptance**: Recognizes keywords "water", "garbage", "pothole" in both languages and responds with correct department + timeline.

---

## Non-Functional Requirements

### NFR1: Performance
- Page load <3s on a standard broadband connection.
- Complaint submission pipeline completes <10s including AI letter generation.
- Database queries <200ms for 10,000 complaints.

### NFR2: Reliability
- System must handle concurrent submissions without data loss.
- LLM failures must not block complaint submission (graceful fallback to keyword matching and template).
- Email/SMS failures must not block status updates.

### NFR3: Security
- No authentication currently implemented (planned).
- SQLite database is local file — no network exposure.
- API has no auth — not suitable for production deployment without changes.
- CORS middleware allows all origins (development setting).

### NFR4: Maintainability
- All services are single-file modules in `backend/services/`.
- Code style enforced via Ruff (100 char lines, PEP8).
- Type checking via MyPy.
- Testing via pytest with coverage reporting.

### NFR5: Scalability
- SQLite is single-user — not suitable for concurrent multi-user production use.
- Future: Migrate to PostgreSQL for true concurrency.

---

## Acceptance Criteria

### FR1-AC (Complaint Submission)
- [x] User can type a complaint in the text area
- [x] User can speak a complaint (record → transcribe → append)
- [x] User can search/find location via text or map click
- [x] User can enter name, phone, and email in separate fields
- [x] `Submit Complaint` button persists complaint to database via `POST /api/complaints/`
- [x] Complaint ID, category, department, and priority are displayed on success

### FR2-AC (AI Classification)
- [x] Classification runs on complaint text (Ollama LLM when available, keyword fallback)
- [x] Returns one of: Pothole, Streetlight, Garbage, Water Leakage, Drainage Issue, Other
- [x] Returns priority: High, Medium, or Low
- [ ] Classification uses an ML model with confidence scoring
- [ ] Confidence score >80% for clear cases

> **NOTE**: Classifier uses LLM (Ollama/Llama3) with keyword fallback. This is AI-driven but not ML-model-based. No confidence scoring.

### FR3-AC (Department Routing)
- [x] Each category maps to a department, email, and priority
- [x] Classifier priority overrides JSON-defined priority when provided
- [x] Unknown categories fall back to Municipal Corporation, Medium
- [x] Routing data is in a configurable JSON file

### FR4-AC (Letter Generation)
- [x] Backend generates a letter via Ollama/Llama3 when available
- [x] Backend falls back to a plain template when Ollama is unavailable

### FR5-AC (PDF Generation)
- [x] Backend generates PDF via ReportLab
- [x] PDF saved to `backend/generated_pdfs/`
- [x] Frontend PDF download calls `GET /api/complaints/{id}/pdf` and serves the file

### FR6-AC (Complaint Tracking)
- [x] Status can be updated via API `PUT` endpoint
- [x] Status can be updated via Admin Dashboard dropdown (calls API)
- [x] Status persists in SQLite database
- [ ] Status changes trigger citizen notifications (email/SMS)

### FR7-AC (Dashboard & Analytics)
- [x] KPI cards render with live data
- [x] Complaint trends line chart renders
- [x] Department distribution pie chart renders
- [x] Recent complaints table renders
- [x] Data refreshes every 10 seconds

### FR8-AC (Admin Management)
- [x] KPI cards render
- [x] Complaint table with select and status update works (calls API)
- [x] Weekly trends chart renders
- [x] Top categories chart renders
- [x] Department performance bars render
- [ ] Hotspot map works for all locations (only 12 hardcoded coordinates)
- [x] Average resolve time shows correctly (currently always 0.0 — feature not implemented)

### FR9-AC (History & Search)
- [x] Table renders with all complaints
- [x] Free-text search filters results
- [x] Status/department/priority dropdowns filter results
- [x] Pagination (12/page) with prev/next works
- [x] Detail popup shows full info + progress timeline
- [x] Connection error gracefully handled with user-facing message

### FR10-AC (Voice Input)
- [x] Microphone recorder widget appears
- [x] Audio is saved to `recorded_audio/` as WEBM + WAV
- [x] Speech is transcribed via Google Speech Recognition
- [x] English and Telugu language selection affects transcription
- [x] Transcribed text is appended to complaint text area

### FR11-AC (AI Complaint View)
- [x] Complaint selector dropdown works
- [x] Letter generation button works (template-based)
- [x] Meta pills render correctly
- [x] Dispatch status indicators render
- [x] Email dispatch indicator reflects actual `email_sent` status
- [x] Copy to clipboard copies letter text
- [x] Download PDF generates and serves a PDF via API
- [x] Dispatch Email sends email via `POST /api/complaints/{id}/dispatch-email`

### FR12-AC (Civic Chatbot)
- [x] Recognizes English keywords: water, garbage, pothole
- [x] Recognizes Telugu keywords: నీర, చెత్త, గుంత
- [x] Returns correct department name and SLA timeline
- [x] Falls back to generic response for unrecognized queries
- [x] Voice input supported for Telugu chatbot

---

## Future Features (Not Yet Specified)

The following features were discussed as future roadmap items and are NOT yet part of this specification:

1. **User Authentication** — login/signup with persistent sessions, "My Complaints" view
2. **Real-time Notifications** — email and SMS alerts on status changes via SMTP + Twilio
3. **Photo Upload** — attach images to complaints for visual evidence
4. **ML Classifier** — replace keyword matching with scikit-learn TF-IDF + LogisticRegression
5. **SLA Auto-Escalation** — automatically escalate complaints stuck beyond their SLA limits
6. **Multi-language Expansion** — add Hindi and other Indian languages beyond Telugu
7. **WhatsApp Bot** — submit/track complaints via WhatsApp
8. **Public Heatmap** — publicly viewable complaint hotspot map
9. **PostgreSQL Migration** — replace SQLite for production-scale concurrency

---

## Current Gaps Summary

| # | Gap | Severity | Affected Feature |
|---|-----|----------|-----------------|
| 1 | No ML classifier — keyword fallback when Ollama unavailable | Medium | FR2 |
| 2 | No photo upload support | Low | FR1 |
| 3 | Hotspot map only works for 12 hardcoded locations | Low | FR8 |
| 4 | Average resolve time always shows 0.0 | Low | FR8 |
| 5 | No authentication on any endpoint | Low* | Security |
| 6 | No citizen notifications on status change | Medium | FR6 |

*Low severity for current demo/prototype stage; Critical for production.
