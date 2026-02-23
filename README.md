# NDA Generator & Tracker

A self-service NDA generation tool for in-house legal teams. Generate pre-approved Mutual NDAs by filling in a short form, download the signed-ready Word document, and track all NDAs in a built-in registry.

## Getting Started

### Option 1: Use the hosted version (easiest)

<!-- TODO: Replace with your deployed URL -->
> **Coming soon** — A hosted version will be available at `https://your-url-here.com`.
> No installation required — just open the link in your browser.

### Option 2: Run locally (one command)

**Prerequisites:** [Python 3.11+](https://www.python.org/downloads/)

**Mac / Linux:**
```bash
git clone https://github.com/yourusername/nda-generator.git
cd nda-generator
./start.sh
```

**Windows:**
```
git clone https://github.com/yourusername/nda-generator.git
cd nda-generator
start.bat
```

This installs dependencies automatically on first run, starts the app, and opens it in your browser.

### Option 3: Run with Docker

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
git clone https://github.com/yourusername/nda-generator.git
cd nda-generator
docker compose up --build
```

Open `http://localhost:8501` in your browser.

## Deploy Your Own

Deploy your own instance to Railway with one click:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/your-template-id)

Or manually:

1. Fork this repo on GitHub
2. Sign up at [railway.com](https://railway.com) (free tier available)
3. Create a new project → "Deploy from GitHub repo" → select your fork
4. Railway auto-detects the config and deploys. Done.

Once deployed, you can point a custom domain (e.g., `nda.yourcompany.com`) at it from Railway's settings.

## Features

- **NDA Generation** — Fill in party names, jurisdiction, term, and purpose; get a professional .docx NDA
- **NDA Registry** — Every generated NDA is logged with status tracking (draft, sent, executed, expired)
- **Jurisdiction Management** — Preset jurisdictions (US states + international) with usage-based "top picks" and custom jurisdiction support
- **REST API** — Full API with Swagger docs for integration with other tools
- **Web Frontend** — Simple, clean interface for generating and managing NDAs

---

## For Developers

### API Documentation

With the app running, visit `http://localhost:8000/docs` for interactive Swagger API documentation.

### API Examples

Generate an NDA:
```bash
curl -X POST http://localhost:8000/api/ndas/ \
  -H "Content-Type: application/json" \
  -d @data/sample/sample_request.json
```

List all NDAs:
```bash
curl http://localhost:8000/api/ndas/
```

Download a generated NDA:
```bash
curl -O http://localhost:8000/api/ndas/1/download
```

See `data/sample/sample_request.json` for a full example request payload.

### Project Structure

```
nda-generator/
├── app/
│   ├── api/routes/       # FastAPI route handlers
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic validation schemas
│   ├── services/         # Business logic (generation, tracking)
│   ├── templates/        # NDA .docx templates
│   ├── config.py         # App configuration
│   ├── database.py       # Database setup
│   └── main.py           # FastAPI app entry point
├── frontend/             # Streamlit web UI
├── tests/                # pytest test suite
├── data/sample/          # Sample data for testing
├── start.sh / start.bat  # One-command startup scripts
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

### Running Tests

```bash
pytest -v
```

### Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Document Generation:** docxtpl (Jinja2-based Word templates)
- **Frontend:** Streamlit
- **Deployment:** Docker, Railway

## License

MIT
