# Architecture — Phase 1

## Runtime boundaries

- React/Vite is a static frontend. GitHub Pages serves the built files from the repository subpath.
- FastAPI is an independent service. It owns outbound collection requests, parsing, validation, and persistence.
- The browser calls the backend through `VITE_API_BASE_URL`; CORS origins are configured on the backend.

## Current request flow

1. The frontend loads and renders the workspace shell.
2. `src/services/api.js` calls `GET /api/health`.
3. FastAPI responds with API and SQLite connectivity status.
4. The UI displays the connection state and allows a manual retry.

## Database

SQLAlchemy is configured with SQLite by default. The data directory is ignored by Git. For hosted use, mount a persistent volume or switch to a managed database URL before storing important data.

## Security boundaries for future collectors

The backend must own all external HTTP requests. Before arbitrary URL fetching is implemented, add URL scheme validation, DNS/IP checks that reject loopback/private/link-local/reserved destinations, redirect re-validation, request timeouts, response-size limits, per-source rate limits, and safe secret handling. Do not expose arbitrary proxy/fetch endpoints directly to the public internet.

## Planned extension points

- `app/api/routes`: REST endpoints
- `app/scrapers`: API, HTML, RSS collectors
- `app/parsers`: format-specific parsing and normalization
- `app/models`: SQLAlchemy models
- `app/scheduler`: scheduled collection jobs
