# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-03
### Added
- Configured Ruff, Mypy, Pytest, and Coverage configurations in `pyproject.toml`.
- Created Gitlab CI/CD workflow in `.gitlab-ci.yml`.
- Expanded `.pre-commit-config.yaml` to run Ruff, Ruff Format, Mypy, Gitleaks, and Bandit.
- Dockerized Streamlit application using a Python 3.11 base image.
- Implemented FastAPI backend test suite using Pytest.
- Added repository compliance files: `CHANGELOG.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, and `LICENSE` (AGPLv3).
- Added specifications and configuration memory: `specs/complaint-management.md` and `.specify/memory/constitution.md`.
- Added directory `.specify/templates/` with tracking file.
- Added `.env.example` file.
