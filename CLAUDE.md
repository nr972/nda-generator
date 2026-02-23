# CLAUDE.md — NDA Generator & Tracker

## Project Summary

Self-service NDA generation tool for in-house legal teams. Users fill a web form (party names, mutual vs. one-way, jurisdiction, term, carve-outs), the tool generates a Word (.docx) NDA from approved templates, logs it in a registry, and tracks expiry/renewal.

## Tech Stack

- **Backend:** Python (FastAPI)
- **Template engine:** docxtpl (Jinja2-based Word template rendering)
- **Database:** SQLite (prototype) — use SQLAlchemy ORM for future PostgreSQL migration
- **Frontend:** Streamlit (rapid prototype)
- **Deployment:** Docker
- **Package management:** pyproject.toml (PEP 621)

## Project Structure

```
nda-generator/
├── app/                  # FastAPI backend
│   ├── api/              # API route handlers
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic (generation, tracking)
│   ├── templates/        # NDA .docx templates
│   └── config.py         # App configuration
├── frontend/             # Streamlit app
├── data/
│   └── sample/           # Sample/synthetic data for testing
├── tests/                # pytest tests
├── pyproject.toml
├── Dockerfile
└── README.md
```

## Coding Conventions

- Python 3.11+
- Type hints on all function signatures
- Pydantic for data validation (v2)
- SQLAlchemy 2.0 style (mapped_column, DeclarativeBase)
- FastAPI dependency injection for DB sessions
- pytest for testing
- Keep modules small and focused

## Key Rules

- **No real data.** All sample data must be synthetic. Never commit real company names, client data, or internal policies.
- **Generic framework.** Keep the public codebase company-agnostic. Company-specific config stays out of the repo.
- **MIT License.**
- **SQLite for now.** Use SQLAlchemy so the DB layer is swappable to PostgreSQL later.
- **Templates are .docx files** with Jinja2 placeholders processed by docxtpl.

## Running the Project

```bash
# Install dependencies
pip install -e ".[dev]"

# Run FastAPI backend
uvicorn app.main:app --reload

# Run Streamlit frontend
streamlit run frontend/app.py

# Run tests
pytest
```

## Git Workflow

- Main branch: `main`
- Commit messages: imperative mood, concise
- PROJECT.md is gitignored (private project context)
- CLAUDE.md is committed (project instructions for AI tooling)
