# AISA Internal System — API Reference

Base URL: `http://localhost:8000`

All request and response bodies are JSON. Datetime fields use ISO 8601 format (e.g. `"2026-04-22T10:00:00Z"`). All data is in-memory and resets on server restart.

---

## Health

### GET /
Returns service status.

**Response 200**
```json
{ "status": "ok", "service": "AISA Internal System" }
```

---

## Todos

### POST /todos/
Create a new todo. The server assigns a UUID.

**Request body**
| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | |
| `description` | string | no | |
| `due_date` | datetime | yes | ISO 8601 |

**Example**
```json
{ "title": "Write tests", "description": "Cover all routes", "due_date": "2026-05-01T09:00:00Z" }
```

**Response 201** — `TodoResponse`
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Write tests",
  "description": "Cover all routes",
  "due_date": "2026-05-01T09:00:00Z",
  "created_at": "2026-04-22T08:00:00Z",
  "completed": false
}
```

---

### GET /todos/
List all todos.

**Response 200** — array of `TodoResponse`

---

### GET /todos/{todo_id}
Get a single todo by its UUID string.

**Response 200** — `TodoResponse`
**Response 404** — `{ "detail": "Todo '<id>' not found." }`

---

### PUT /todos/{todo_id}
Partially update a todo. Only fields provided in the body are changed.

**Request body** (all fields optional)
| Field | Type | Notes |
|---|---|---|
| `title` | string | |
| `description` | string | |
| `due_date` | datetime | ISO 8601 |
| `completed` | boolean | |

**Example**
```json
{ "completed": true }
```

**Response 200** — updated `TodoResponse`
**Response 404** — `{ "detail": "Todo '<id>' not found." }`

---

### DELETE /todos/{todo_id}
Delete a todo.

**Response 204** — no body
**Response 404** — `{ "detail": "Todo '<id>' not found." }`

---

## Calendars

A calendar has a `start_date` and a 100-day window. All events must fall entirely within that window.

### POST /calendars/
Create a new calendar. The server assigns a UUID.

**Request body**
| Field | Type | Required |
|---|---|---|
| `start_date` | datetime | yes |

**Example**
```json
{ "start_date": "2026-04-22T00:00:00Z" }
```

**Response 201** — `CalendarResponse`
```json
{
  "calendar_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "start_date": "2026-04-22T00:00:00Z",
  "events": []
}
```

---

### GET /calendars/{calendar_id}
Get a calendar and all its events.

**Response 200** — `CalendarResponse`
**Response 404** — `{ "detail": "Calendar not found" }`

---

### DELETE /calendars/{calendar_id}
Delete a calendar and all its events.

**Response 204** — no body
**Response 404** — `{ "detail": "Calendar not found" }`

---

### POST /calendars/{calendar_id}/events
Add an event to a calendar.

**Constraints:**
- `start` must be before `end`
- Both `start` and `end` must fall within the calendar's 100-day window (`start_date` to `start_date + 100 days`)

**Request body**
| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | |
| `description` | string | no | |
| `start` | datetime | yes | ISO 8601 |
| `end` | datetime | yes | ISO 8601 |

**Example**
```json
{
  "title": "Team standup",
  "description": "Daily sync",
  "start": "2026-04-23T09:00:00Z",
  "end": "2026-04-23T09:30:00Z"
}
```

**Response 201** — `EventResponse`
```json
{
  "event_id": "8d4e9c20-1234-4abc-b3fc-9f8e7d6c5b4a",
  "title": "Team standup",
  "description": "Daily sync",
  "start": "2026-04-23T09:00:00Z",
  "end": "2026-04-23T09:30:00Z"
}
```

**Response 400** — start >= end, or event falls outside the 100-day window
**Response 404** — calendar not found

---

### GET /calendars/{calendar_id}/events
List all events in a calendar.

**Response 200** — array of `EventResponse`
**Response 404** — `{ "detail": "Calendar not found" }`

---

### GET /calendars/{calendar_id}/events/{event_id}
Get a single event.

**Response 200** — `EventResponse`
**Response 404** — calendar not found or event not found

---

### PUT /calendars/{calendar_id}/events/{event_id}
Replace an event entirely. All fields must be provided.

**Request body** — same as `POST /calendars/{calendar_id}/events`

**Response 200** — updated `EventResponse`
**Response 400** — validation failure (same rules as create)
**Response 404** — calendar or event not found

---

### DELETE /calendars/{calendar_id}/events/{event_id}
Delete a single event.

**Response 204** — no body
**Response 404** — calendar or event not found

---

## Emails

Emails are created through the Scenarios API. The `/emails` routes are read and delete only.

> **Note:** `email_id` is an **integer** provided by the caller at creation time.

### GET /emails/
List all emails across all scenarios.

**Response 200** — array of `Email`
```json
[
  {
    "email_id": 1,
    "subject": "Welcome",
    "sender": "admin@example.com",
    "recipients": ["user@example.com"],
    "body": "Hello there.",
    "created_at": "2026-04-22T08:00:00Z"
  }
]
```

---

### GET /emails/{email_id}
Get a single email by its integer ID.

**Response 200** — `Email`
**Response 404** — `{ "detail": "Email <id> not found" }`

---

### DELETE /emails/{email_id}
Delete an email. Also removes the email from any scenario it belongs to.

**Response 204** — no body
**Response 404** — `{ "detail": "Email <id> not found" }`

---

## Scenarios

A scenario groups emails together with optional metadata. Both `scenario_id` and `email_id` are **integers provided by the caller**.

### GET /scenarios/
List all scenarios.

**Response 200** — array of `Scenario`

---

### POST /scenarios/
Create a new scenario. The caller must supply `scenario_id`. Any emails included in the payload are also registered in the global email store.

**Request body**
| Field | Type | Required | Notes |
|---|---|---|---|
| `scenario_id` | integer | yes | Must be unique; caller-assigned |
| `emails` | array of `Email` | no | Defaults to `[]` |
| `success_criteria` | string | no | |
| `puzzle_summary` | string | no | |

Each `Email` object in the `emails` array:
| Field | Type | Required |
|---|---|---|
| `email_id` | integer | yes |
| `subject` | string | yes |
| `sender` | string | yes |
| `recipients` | array of string | yes |
| `body` | string | yes |
| `created_at` | datetime | yes |

**Example**
```json
{
  "scenario_id": 1,
  "success_criteria": "User replies within 1 hour",
  "puzzle_summary": "Phishing simulation",
  "emails": [
    {
      "email_id": 101,
      "subject": "Urgent: password reset",
      "sender": "attacker@evil.com",
      "recipients": ["victim@company.com"],
      "body": "Click here to reset your password.",
      "created_at": "2026-04-22T08:00:00Z"
    }
  ]
}
```

**Response 201** — `Scenario`
**Response 409** — `{ "detail": "Scenario <id> already exists" }`

---

### GET /scenarios/{scenario_id}
Get a scenario by its integer ID.

**Response 200** — `Scenario`
**Response 404** — `{ "detail": "Scenario <id> not found" }`

---

### DELETE /scenarios/{scenario_id}
Delete a scenario. Also deletes all emails that belong to it from the global email store.

**Response 204** — no body
**Response 404** — `{ "detail": "Scenario <id> not found" }`

---

### POST /scenarios/{scenario_id}/emails
Add a single email to an existing scenario. The email is also registered in the global email store. The caller must supply a unique `email_id`.

**Request body** — full `Email` object (same schema as above)

**Example**
```json
{
  "email_id": 102,
  "subject": "Follow-up",
  "sender": "attacker@evil.com",
  "recipients": ["victim@company.com"],
  "body": "Did you reset your password?",
  "created_at": "2026-04-22T09:00:00Z"
}
```

**Response 201** — `Email`
**Response 404** — scenario not found
**Response 409** — `{ "detail": "Email <id> already exists" }`

---

## Error Responses

| Status | Meaning |
|---|---|
| 400 | Bad request — invalid field values or constraint violation |
| 404 | Resource not found |
| 409 | Conflict — ID already exists |
| 422 | Validation error — missing or wrong-type fields |
| 500 | Internal server error |

**422 body shape**
```json
{
  "error": "Validation error",
  "detail": [{ "loc": ["body", "field"], "msg": "...", "type": "..." }]
}
```

**500 body shape**
```json
{ "error": "Internal server error", "detail": "..." }
```
