# Dealer Stock & Enquiry Tracker
A small full-stack learning project for managing fictional vehicle stock and enquiry follow-ups. It helps a dealer see stock state and outstanding work in one place.

## Run
Python 3.10+ (tested here on 3.12):
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/WSL:
source .venv/bin/activate
python -m pip install -r requirements.txt
python start.py
```
Open http://127.0.0.1:8090. Stop with Ctrl+C. First installation needs internet; afterwards normal local use does not.
Optional fictional seed: `python -m scripts.seed_demo`.

## Architecture
Browser HTML/CSS/JavaScript → frontend/api.js → FastAPI functions and Pydantic input classes → SQLite helpers. FastAPI serves the browser and API from one origin. Data lives in data/dealer.sqlite3; DEALER_DB selects another path. Store integer pence.
Contract: openapi.yaml. Interactive API docs: /docs. Spec: product-spec.md. AI workflow: docs/ai-usage-report.md.

## Checks and container
`python -m pytest -q`; `node --test tests/frontend.test.mjs`; `python scripts/check_public_files.py` before adding private data.
`docker compose up --build` runs the whole app. First build needs internet. The volume keeps the database; `docker compose down` stops it.

## Status
Local reference application. No public deployment, authenticated customer system, verified MCP host demo, complete observability or external scanner runs yet. Read docs/deployment.md, security/audit.md and docs/requirements-matrix.md before claiming submission readiness. Use fictional data only.
