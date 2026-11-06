# Architecture — Cloud PostgreSQL target

## 1. Target runtime architecture

Web Data Lab uses a separately deployed frontend, API, and managed database:

```text
Browser
  |
  v
React + Vite frontend
  |
  | HTTPS / JSON API (VITE_API_BASE_URL)
  v
Cloud-hosted FastAPI service
  |
  | SQLAlchemy + PostgreSQL driver
  | TLS connection; credentials from backend environment
  v
Neon managed PostgreSQL
```

- **Frontend:** React/Vite static assets hosted on GitHub Pages.
- **Backend:** FastAPI deployed as an independent cloud service. The hosting provider is a separate decision and must be selected before backend deployment.
- **Database:** Neon managed PostgreSQL is the production database. The database is not stored on the user's computer.
- **Migrations:** Alembic is the only schema-change mechanism. Apply migrations to the target database before starting a release that depends on the new schema.

A replacement computer can continue using the same data because the data is held by Neon, not by the browser or local project directory. This depends on the cloud API and Neon account remaining available and correctly configured. Backups and restore testing are still required.

## 2. Database strategy

### Production

- Use Neon PostgreSQL.
- Set `WDL_DATABASE_URL` in the cloud backend's secret/environment configuration.
- Use a Neon connection string with TLS enabled (Neon's supplied connection string includes the required SSL settings).
- Use Neon's pooled connection string for normal serverless or horizontally scaled application traffic when appropriate; use the direct connection string for migrations or administrative operations where a stable direct connection is preferred.
- Never commit a real connection string, password, or API secret.
- Do not expose database credentials to the browser or place them in any `VITE_*` variable.

### Local development

- SQLite may remain an optional local-development fallback so contributors can run the API without cloud credentials.
- Production must not silently fall back to SQLite. Deployment configuration must explicitly provide the Neon PostgreSQL URL, and startup/health checks must make the active database backend observable.
- Do not put a SQLite database file on a shared cloud drive as a substitute for a managed database.

## 3. Core data model

Keep the four existing business tables and their relationships:

- `data_sources` 1:N `collection_tasks`
- `collection_tasks` 1:N `collection_runs`
- `collection_runs` 1:N `collected_records`
- `collected_records` also references `data_sources` for efficient source-level queries.

The current SQLAlchemy model layer is intended to remain database-portable. The initial Alembic revision was authored before the Neon decision and must be reviewed and tested against PostgreSQL before it is treated as production-ready. In particular, verify server defaults, JSON columns, check constraints, foreign keys, indexes, timestamp behavior, and downgrade behavior.

## 4. Connection and transaction handling

- Keep SQLAlchemy sessions request-scoped and always close them.
- Use connection health checks and bounded connection-pool settings suitable for the chosen FastAPI host and Neon connection mode.
- Keep transaction boundaries explicit in service functions.
- Run Alembic migrations as a controlled deployment step, not independently in every web worker.
- Treat transient connection failures as service errors; do not report the database as healthy when it cannot be reached.

## 5. Secrets and network boundaries

- Store `WDL_DATABASE_URL` and any future API credentials only in the backend host's encrypted environment/secret settings.
- Restrict CORS to the deployed frontend origin and explicitly required local development origins.
- The frontend communicates only with FastAPI over HTTPS.
- The backend owns all external data-collection requests.
- Before arbitrary URL fetching is implemented, add URL scheme validation, DNS/IP checks that reject loopback/private/link-local/reserved destinations, redirect re-validation, request timeouts, response-size limits, per-source rate limits, and safe secret handling.
- Never expose an arbitrary proxy/fetch endpoint directly to the public internet.

## 6. Backup and recovery

- Enable and understand the backup/restore capabilities available for the selected Neon plan before storing important user data.
- Define a recovery procedure and perform a restore test before calling the service production-ready.
- GitHub is for source code and migrations; it is not a database backup.

## 7. Current implementation status

- React/Vite frontend: deployed on GitHub Pages.
- FastAPI backend: scaffolded, not yet deployed.
- SQLAlchemy models: four core tables defined.
- Alembic: initial migration exists, but PostgreSQL execution has not yet been verified.
- Neon project/database: selected by the user, provisioning and connection configuration are the next implementation tasks.
- Cloud FastAPI hosting provider: not selected yet.

## 8. Planned extension points

- `app/api/routes`: REST endpoints
- `app/scrapers`: API, HTML, RSS collectors
- `app/parsers`: format-specific parsing and normalization
- `app/models`: SQLAlchemy models
- `app/scheduler`: scheduled collection jobs
