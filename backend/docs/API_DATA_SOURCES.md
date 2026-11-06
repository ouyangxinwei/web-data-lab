# Data Sources API

Base path: `/api/sources`

The API manages source definitions only. It does not fetch the configured URL yet.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/sources` | List sources; supports `limit`, `offset`, `source_type=api|html`, and `is_active=true|false` |
| POST | `/api/sources` | Create a source |
| GET | `/api/sources/{id}` | Read one source |
| PUT | `/api/sources/{id}` | Replace all editable fields |
| DELETE | `/api/sources/{id}` | Delete an unused source |

List responses contain `items`, `total`, `limit`, and `offset`. Create returns HTTP 201. Delete returns HTTP 204. Missing IDs return 404. Deleting a source referenced by a collection task or record returns 409.

## Create / replace request

```json
{
  "name": "Example public API",
  "source_type": "api",
  "base_url": "https://example.com/api",
  "description": "A public test endpoint",
  "config_json": {
    "response_format": "json"
  }
}
```

`source_type` must be `api` or `html`. The URL must be an absolute HTTP(S) URL and must not embed credentials. Credential-like keys (for example `api_key`, `token`, `password`, or `authorization`) are rejected recursively inside `config_json`. Store secrets in environment variables or a dedicated secret store, not in source configuration.

This endpoint only stores a URL; it does not make an outbound request. Before implementing a collector, enforce SSRF protections at request time (including DNS/IP checks, redirect validation, and blocking loopback, private, link-local, and metadata-service destinations).

## Local smoke test (PowerShell)

With FastAPI running from the `backend` directory:

```powershell
$body = @{
  name = "Example public API"
  source_type = "api"
  base_url = "https://example.com/api"
  description = "A public test endpoint"
  config_json = @{ response_format = "json" }
} | ConvertTo-Json -Depth 10

$created = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/sources" -ContentType "application/json" -Body $body
$created
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/sources"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/sources/$($created.id)"
```

For replacement, send a complete JSON body with `PUT`. For deletion, use `Invoke-WebRequest -Method Delete` and expect HTTP 204.
