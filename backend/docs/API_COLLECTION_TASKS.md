# Collection Tasks API

Base path: `/api/tasks`

This API manages collection-task definitions. It does not execute tasks or start a scheduler.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/tasks` | List tasks with pagination and filters |
| POST | `/api/tasks` | Create a task |
| GET | `/api/tasks/{id}` | Read one task |
| PUT | `/api/tasks/{id}` | Replace all editable task fields |
| DELETE | `/api/tasks/{id}` | Delete a task without execution history |

List filters: `source_id`, `schedule_type=manual|interval|cron`, and `is_enabled=true|false`. Pagination uses `limit` (1–100, default 50) and `offset` (default 0). The response envelope contains `items`, `total`, `limit`, and `offset`.

## Create / replace request

```json
{
  "source_id": 1,
  "name": "Example API collection",
  "schedule_type": "manual",
  "schedule_config": {},
  "is_enabled": true
}
```

- `source_id` must refer to an existing, active data source.
- Inactive data sources (`is_active=false`) cannot be selected when creating or updating a task. Existing tasks remain stored if their source is later deactivated.
- `schedule_type` must be `manual`, `interval`, or `cron`.
- `schedule_config` is stored as JSON. Its execution semantics will be defined when scheduling is implemented.
- PUT is a full replacement: send all editable fields.

## Status and relationship rules

| Condition | HTTP status |
| --- | --- |
| Task created | 201 |
| Successful list/read/update | 200 |
| Task deleted | 204 |
| Task ID does not exist | 404 |
| Source does not exist or is inactive | 400 |
| Task has execution history and cannot be deleted | 409 |
| Database constraint conflict | 409 |
| Invalid request fields | 422 |

A task with one or more rows in `collection_runs` cannot be deleted, preserving execution history. Disable the task instead by setting `is_enabled=false`.

## Local smoke test (PowerShell)

Run FastAPI from the `backend` directory. Replace `1` with the ID of an existing active data source.

```powershell
$body = @{
  source_id = 1
  name = "Example API collection"
  schedule_type = "manual"
  schedule_config = @{}
  is_enabled = $true
} | ConvertTo-Json -Depth 10

$created = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/tasks" -ContentType "application/json" -Body $body
$created
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/tasks"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/tasks/$($created.id)"
```

For replacement, send a complete JSON body with PUT. For deletion, use `Invoke-WebRequest -Method Delete` and expect HTTP 204. Test deletion protection only after creating a collection run linked to the task; do not remove production history.
