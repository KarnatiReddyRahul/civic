# Project Constitution

This document defines the rules, architecture, and coding standards for CivicAssist AI.

## Core Architecture

CivicAssist AI is an AI-powered citizen grievance management platform comprised of:
1. **Frontend**: Streamlit application (`app.py` and `pages/`) providing user interface dashboards, issue submission, status tracking, admin views, and AI logs.
2. **Backend**: FastAPI server (`backend/main.py`) exposing REST API endpoints to manage complaints, analytics, and department routing.
3. **AI Agents**: Modular agents implementing LLM (Llama 3/Ollama) and helper functions for Complaint Classification, Department Routing, Complaint Document Generation, PDF Rendering, Email Dispatch, and Status Tracking.
4. **Database**: SQLite database (`backend/complaints.db`) for tracking states and histories.

## Quality and Compliance Standards

- **Formatting & Style**: Code must adhere to PEP 8 standards enforced via Ruff formatter and linter (100 characters line limit).
- **Type Checking**: Mypy must be run with strict checks where possible. Imports from external dependencies should specify typings.
- **Testing**: Automated testing using pytest and pytest-cov. Maintain test coverage.
- **Security Check**: Pre-commit hooks and CI scan python vulnerabilities (Bandit) and credentials leak (Gitleaks).
- **Licensing**: Open-source license (AGPLv3) applies.
