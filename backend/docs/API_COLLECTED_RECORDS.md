# Collected Records API

Base path: `/api/records`

This API provides read-only access to collected record snapshots. Records are treated as immutable history: there are intentionally no public create, update, or delete endpoints. Future API and HTML collectors will persist records through backend collection services rather than accepting arbitrary record writes from this read API.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/records` | List records with pagination and filters |
| GET | `/api/records/{record_id}` | Read one record, including its optional raw payload |

## List and filters

Supported query parameters:

- `limit`: 1–100, default 50
- `offset`: zero-based offset, default 0
- `source_id`: filter by data source ID
- `run_id`: filter by collection run ID
- `external_id`: exact match against the external record identifier

The response contains `items`, `total`, `limit`, and `offset`. Results are ordered by `collected_at` descending, then `id` descending. The list response includes `data_json` but omits `raw_data` to avoid returning potentially large original payloads for every row.

Example:

```http
GET /api/records?source_id=2&run_id=3&limit=20&offset=0
```

## Read one record

```http
GET /api/records/1
```

The detail response includes `data_json`, optional `raw_data`, `content_hash`, identifiers, and `collected_at`.

An unknown record ID returns HTTP 404.

## Data lifecycle and safety

- Collected records are historical snapshots and are not edited through this API.
- No public create or delete endpoint is provided, preserving the audit/history relationship to sources and runs.
- Future collectors are responsible for validating and normalizing collected data before persistence.
- Source URL fetching must separately enforce SSRF protections at request time; this read API does not perform outbound requests.

## HTTP status summary

| Condition | HTTP status |
| --- | --- |
| Successful list or detail read | 200 |
| Record ID does not exist | 404 |
| Invalid query parameter | 422 |
