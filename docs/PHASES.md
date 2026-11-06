# Development phases

| Phase | Deliverables | Acceptance |
|---|---|---|
| 1 — Foundation | React/Vite frontend, FastAPI backend, SQLite connectivity, health endpoint, i18n/theme shell, Pages workflow | Frontend build passes; health endpoint returns API and DB status |
| 2 — API collection | GET/POST, headers, query/body params, JSON/XML parsing, timeout/error handling, starter sources | Add and run an API source; inspect raw and normalized data |
| 3 — HTML scraping | HTTP fetch, BeautifulSoup, CSS selectors, XPath, field extraction; browser automation only where needed | Extract fields from at least three permitted public pages |
| 4 — Data management | Persistent records, task history, scheduled jobs, snapshots/diffs, CSV/JSON export | Review history and export collected data |
| 5 — Hardening and release | SSRF protections, limits, monitoring, responsive UI, translations, theme, end-to-end verification | Frontend and backend independently deployed and tested |

## Working rules

- Keep the frontend and backend deployment lifecycles independent.
- Never commit credentials or private data.
- Respect source terms, robots.txt, licenses, and request limits.
- Do not mark a phase complete until its acceptance checks have been run and evidenced.
