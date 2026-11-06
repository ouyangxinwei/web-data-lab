# Development phases

## Confirmed deployment architecture

- Frontend: React/Vite static site on GitHub Pages.
- Backend: FastAPI deployed as a cloud service (hosting provider to be selected).
- Production database: Neon managed PostgreSQL.
- Local SQLite is optional for development only; it is not the production data store.
- Database credentials are backend-only secrets and must never be committed or exposed through frontend build variables.

## Delivery sequence

| Step | Work | Acceptance |
|---|---|---|
| 1 | Confirm cloud architecture and database boundaries | Architecture documentation identifies GitHub Pages, cloud FastAPI, Neon PostgreSQL, secret handling, migration and backup rules |
| 2 | Configure FastAPI + Neon PostgreSQL | Backend connects using environment configuration; PostgreSQL driver and pool settings are in place; Alembic migration creates all four core tables successfully on Neon |
| 3 | Establish React + Vite frontend | Frontend build succeeds and API base URL is environment-configurable |
| 4 | Complete frontend/backend communication | Browser calls the deployed FastAPI health endpoint over HTTPS; CORS is restricted to approved origins |
| 5 | Configure GitHub Actions | Frontend deployment and backend delivery workflow are reproducible; secrets are configured outside Git |
| 6 | Test and deploy frontend | GitHub Pages build/deploy succeeds and the deployed frontend can reach the cloud API |

## Original product phases

| Phase | Deliverables | Acceptance |
|---|---|---|
| 1 — Foundation | React/Vite frontend, FastAPI backend, database connectivity, health endpoint, i18n/theme shell, Pages workflow | Frontend build passes; health endpoint reports API and database status |
| 2 — API collection | GET/POST, headers, query/body params, JSON/XML parsing, timeout/error handling, starter sources | Add and run an API source; inspect raw and normalized data |
| 3 — HTML scraping | HTTP fetch, BeautifulSoup, CSS selectors, XPath, field extraction; browser automation only where needed | Extract fields from at least three permitted public pages |
| 4 — Data management | Persistent records, task history, scheduled jobs, snapshots/diffs, CSV/JSON export | Review history and export collected data |
| 5 — Hardening and release | SSRF protections, limits, monitoring, responsive UI, translations, theme, end-to-end verification | Frontend and backend independently deployed and tested |

## Working rules

- Keep frontend and backend deployment lifecycles independent.
- Never commit credentials or private data.
- Use Alembic for schema changes; do not hand-edit a deployed database schema.
- Test migrations against PostgreSQL before production use.
- Respect source terms, robots.txt, licenses, and request limits.
- Do not mark a phase complete until its acceptance checks have been run and evidenced.
- Every formal release must update `VERSION.md` and `frontend/package.json` together, record the commit SHA, and report frontend/backend deployment status separately.
