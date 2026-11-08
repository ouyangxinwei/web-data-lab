# Collection Runs API

Base path: `/api/runs`

This API manages collection execution records. It records a pending run and manages its lifecycle; it does **not** execute an API/HTML collector or start a scheduler.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/runs` | List runs with pagination and filters |
| POST | `/api/runs` | Create a pending run for an enabled task |
| GET | `/api/runs/{run_id}` | Read one run |
| PATCH | `/api/runs/{run_id}/status` | Move a run through its allowed status lifecycle |

List filters: `task_id` and `status=pending|running|success|failed`. Pagination uses `limit` (1–100, default 50) and `offset` (default 0). The response envelope contains `items`, `total`, `limit`, and `offset`.

## Create a run

Request:

```json
{
  "task_id": 1
}
```

The endpoint creates a record with `status=pending`. The task must exist and be enabled, and its data source must exist and be active. A disabled task or inactive/missing source is rejected with HTTP 400; an unknown task returns 404.

Creating a run record does not start network requests or execute a collector.

## Status lifecycle

Only these transitions are allowed:

- `pending -> running`
- `running -> success`
- `running -> failed`

A run cannot skip a state, move backwards, or change after it reaches `success` or `failed`. Invalid transitions return HTTP 409.

### Start a run

```json
{
  "status": "running"
}
```

The API sets `started_at` and updates the parent task's `last_run_at`.

### Complete successfully

```json
{
  "status": "success",
  "records_count": 12
}
```

### Complete with failure

```json
{
  "status": "failed",
  "records_count": 0,
  "error_message": "The remote endpoint returned HTTP 503."
}
```

When a run finishes, the API sets `finished_at` and calculates `duration_ms`. `records_count` is optional and cannot be negative. A non-empty `error_message` is required for `failed` and is only accepted for that status.

## Status and error rules

| Condition | HTTP status |
| --- | --- |
| Run created | 201 |
| Successful list/read/status update | 200 |
| Run ID does not exist | 404 |
| Task ID does not exist | 404 |
| Task disabled or source missing/inactive | 400 |
| Invalid status transition | 409 |
| Database constraint conflict | 409 |
| Invalid request fields | 422 |

There is intentionally no DELETE endpoint: execution history should be retained.

## Local smoke test (PowerShell)

Run the API from the `backend` directory. Replace task ID `1` with an existing enabled task whose data source is active.

```powershell
$body = @{ task_id = 1 } | ConvertTo-Json
$run = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/runs" -ContentType "application/json" -Body $body
$run

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/runs"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/runs/$($run.id)"

$startBody = @{ status = "running" } | ConvertTo-Json
Invoke-RestMethod -Method Patch -Uri "http://127.0.0.1:8000/api/runs/$($run.id)/status" -ContentType "application/json" -Body $startBody

$finishBody = @{ status = "success"; records_count = 12 } | ConvertTo-Json
Invoke-RestMethod -Method Patch -Uri "http://127.0.0.1:8000/api/runs/$($run.id)/status" -ContentType "application/json" -Body $finishBody
```
