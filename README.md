# Web Data Lab

A personal laboratory for learning and testing multi-source data collection with public APIs and HTML scraping.

## Architecture

- `frontend/`: React + Vite single-page application, deployed independently to GitHub Pages.
- `backend/`: Python + FastAPI service for API requests, HTML retrieval, parsing, and SQLite persistence.
- Frontend and backend communicate through HTTPS REST endpoints. The backend is not hosted by GitHub Pages.

## Development status

| Phase | Scope | Status |
|---|---|---|
| 1 | Project foundation, frontend/backend skeleton, health check, CI/CD baseline | In progress |
| 2 | API collection | Planned |
| 3 | HTML scraping | Planned |
| 4 | Storage, history, scheduling, exports | Planned |
| 5 | Security hardening, responsive polish, deployment and verification | Planned |

## Local development

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check: `http://127.0.0.1:8000/api/health`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://127.0.0.1:8000` for local API requests. Set `VITE_API_BASE_URL` when using a separately hosted backend.

## Important notes

- GitHub Pages hosts only the frontend. Deploy the FastAPI backend to a separate HTTPS-capable service.
- Never put API keys, passwords, or other secrets in frontend environment variables or committed files.
- Scraping features must respect each site's terms, robots.txt, licensing, rate limits, and privacy requirements.
- The backend must validate target URLs and block private/local network destinations before enabling arbitrary URL fetching.
- SQLite is the initial database. Production deployment must use persistent storage or a managed database; ephemeral container storage is not sufficient.

## License

To be decided.
