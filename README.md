# AISA Spring 26 — Todo API

Internal FastAPI service for the AISA Spring 26 benchmark system. Provides a Todo API that an AI model can call to create, read, update, and delete todo items during simulated benchmark runs.

---

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point, error handlers, health check
│   ├── store.py         # In-memory data store (dict keyed by todo ID)
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py      # Pydantic schemas: TodoCreate, TodoUpdate, TodoResponse
│   └── routers/
│       ├── __init__.py
│       └── todos.py     # All CRUD endpoints for /todos
├── tests/
│   ├── __init__.py
│   └── test_todos.py    # 18 automated tests covering all endpoints and error cases
├── requirements.txt     # Python dependencies
├── .gitignore
└── README.md
```

---

## Setup

**1. Create and activate a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Running the Server

```bash
uvicorn app.main:app --reload
```

The server starts at **http://127.0.0.1:8000**

`--reload` automatically restarts the server when you save a file — useful during development.

---

## Interactive API Docs

FastAPI auto-generates a browser UI for testing all endpoints:

- **http://127.0.0.1:8000/docs** — Swagger UI (recommended)
- **http://127.0.0.1:8000/redoc** — ReDoc

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/todos/` | Create a new todo |
| `GET` | `/todos/` | List all todos |
| `GET` | `/todos/{id}` | Get a single todo by ID |
| `PUT` | `/todos/{id}` | Update a todo's fields |
| `DELETE` | `/todos/{id}` | Delete a todo |

### Todo fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | Auto-generated unique identifier |
| `title` | string | Required. The todo title |
| `description` | string | Optional. Extra detail |
| `due_date` | datetime (ISO 8601) | Required. When the task is due |
| `created_at` | datetime | Auto-set to the time of creation |
| `completed` | boolean | Defaults to `false` |

### Example requests

**Create a todo**
```bash
curl -X POST http://127.0.0.1:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Write report", "due_date": "2026-05-01T12:00:00Z"}'
```

**List all todos**
```bash
curl http://127.0.0.1:8000/todos/
```

**Get a specific todo**
```bash
curl http://127.0.0.1:8000/todos/<id>
```

**Mark a todo as completed**
```bash
curl -X PUT http://127.0.0.1:8000/todos/<id> \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Delete a todo**
```bash
curl -X DELETE http://127.0.0.1:8000/todos/<id>
```

---

## Error Handling

All errors return structured JSON so the model always gets a parseable response:

| Status | Meaning |
|--------|---------|
| `404` | Todo ID not found |
| `422` | Invalid request payload (missing field, wrong type, etc.) |
| `500` | Unexpected server error |

Example 404 response:
```json
{
  "detail": "Todo 'abc-123' not found."
}
```

Example 422 response:
```json
{
  "error": "Validation error",
  "detail": [...]
}
```

---

## Running Tests

```bash
pytest tests/test_todos.py -v
```

Expected output: **18 passed**. Tests cover:
- Creating todos (valid and invalid payloads)
- Listing and fetching todos
- Updating individual fields
- Deleting todos
- All 404 and 422 error cases

---

## Data Persistence

The store is **in-memory only** — data resets every time the server restarts. This is intentional for the benchmark use case where each run starts from a clean state.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `pydantic` | Data validation and schemas |
| `pytest` | Test runner |
| `httpx` | HTTP client used by FastAPI's TestClient |

---

## Integration (Upcoming — Sprint 1 Deferred)

This service will eventually be merged with the **Calendar API** (Anthony) and **Email API** (Miguel) into a single unified FastAPI app. The integration tasks are tracked separately and will be completed once all three APIs are ready.
