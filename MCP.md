# MCP Server — Operator Guide

This is your guide to the MCP (Model Context Protocol) server in `mcp_server/`. It's written for **you, the operator** — the person starting/stopping things, running scenarios, and debugging when something goes wrong. (The agent-facing operational doc is still `docs/api_reference.md`; that one is for the LLM.)

---

## What this is, in plain terms

You have a FastAPI service (`app/`) with endpoints for todos, calendar, emails, and scenarios. The MCP server is a **thin translator** that lets any LLM harness call those endpoints through the MCP standard, without you having to hand-roll tool definitions per harness.

```
┌──────────────────┐  stdio   ┌──────────────────┐   HTTP    ┌──────────────────┐
│   MCP client     │ ───────► │   MCP server     │ ────────► │   FastAPI        │
│ (Claude Code,    │ ◄─────── │   (mcp_server/)  │ ◄──────── │   (uvicorn 8000) │
│  Inspector, etc.)│          │   thin wrapper   │           │   real logic     │
└──────────────────┘          └──────────────────┘           └──────────────────┘
```

**Two protocols, two layers:**
- The **left arrow** (stdio): standard MCP. The harness launches `mcp_server` as a subprocess and talks to it through pipes. You don't configure this.
- The **right arrow** (HTTP via `httpx`): the MCP server hits your FastAPI like any external client would. This is the choice that keeps the benchmark honest — there's only one place where API behavior lives.

**What lives in the MCP server itself:** nothing important. Each tool is ~3 lines: build a JSON body, call FastAPI, return the response. If you're hunting a bug in benchmark behavior, the bug is in `app/`, not in `mcp_server/`.

---

## Running it

You always need **two processes** running:

**Terminal 1 — FastAPI:**
```bash
uv run uvicorn app.main:app --reload
```

**Terminal 2 — depends on the client:**

| Client | How to launch |
|---|---|
| MCP Inspector (browser UI) | `npx @modelcontextprotocol/inspector uv run python -m mcp_server` |
| Claude Code | Register via `claude mcp add aisa "uv run python -m mcp_server"` (or add to `.mcp.json`) |
| Claude Desktop | Add to its `claude_desktop_config.json` with `"command": "uv", "args": ["run", "python", "-m", "mcp_server"]` |
| Custom Python harness | `from mcp.client.stdio import stdio_client` — see `/tmp/mcp_smoke_test.py` for a worked example |

The MCP server itself never has a port — clients always launch it as a subprocess.

---

## Configuration

Only one knob:

| Env var | Default | What it does |
|---|---|---|
| `AISA_API_BASE_URL` | `http://localhost:8000` | Where the MCP server expects to find the FastAPI service. Change if you ever run FastAPI on a non-default port or remote host. |

---

## What the server exposes

**1 resource** at URI `aisa://api-reference` — the contents of `docs/api_reference.md`. Any MCP-aware harness can fetch this on demand. Treat this as the agent's system manual: workflows, the `scenario_id` rule, todo↔event linking, ID conventions.

**22 tools**, one per FastAPI route. Names mirror the action:
- Todos: `list_todos`, `get_todo`, `create_todo`, `update_todo`, `delete_todo`
- Calendars: `create_calendar`, `get_calendar`, `delete_calendar`
- Events: `list_events`, `get_event`, `create_event`, `update_event`, `delete_event`
- Emails: `list_emails`, `get_email`, `send_email`
- Scenarios: `list_scenarios`, `get_scenario`, `create_scenario`, `delete_scenario`, `add_scenario_email`
- Health: `health_check`

Each tool's docstring is its description in the MCP protocol. If you want to expand a description, edit it in `mcp_server/server.py` and reconnect — clients re-fetch the tool list on connect.

---

## Things to worry about

**Forgot to start FastAPI.** Every tool will fail with a connection-refused error. The MCP server is just a wrapper — it has nothing to serve if FastAPI isn't running.

**Empty store.** When uvicorn starts, the in-memory store is empty. Before an agent can do anything useful, you (or your harness) must `POST /scenarios/` to seed at least one scenario. Tools like `create_todo` will return 404 (`Scenario X not found`) if the scenario hasn't been seeded.

**Agent passes a bad `scenario_id`.** Surfaces as a tool error with FastAPI's exact detail message. The smoke test confirmed `"Scenario 999 not found"` reaches the LLM. This is a feature — the LLM can self-correct.

**Datetime formats.** All `due_date`, `start`, `end`, `created_at` fields go through as ISO 8601 strings. Pydantic v2 is fairly permissive (accepts `Z` suffix, offset suffix, naive datetimes), but if you ever see weird 422 errors, a malformed datetime is the first thing to check.

**Tool surface is unfiltered.** The agent currently sees admin tools like `create_scenario` and `delete_scenario`. That's deliberate (it's a research surface), but for a real benchmark run you may want to hide those. Future work — see plan file `/Users/miguelpimienta/.claude/plans/dreamy-swinging-hedgehog.md`.

**`/tmp/mcp_smoke_test.py` will vanish on reboot.** macOS clears `/tmp`. If you want to keep the smoke test, move it: `mv /tmp/mcp_smoke_test.py scripts/smoke_test.py`.

**FastMCP's list serialization.** When a tool returns `list[dict]` (e.g. `list_emails`), FastMCP emits **one TextContent block per item**, not a single block containing the list. Most LLM harnesses handle this transparently, but if you ever write a custom client, parse each block individually rather than joining them.

---

## How to verify it's working

The smoke test is at `/tmp/mcp_smoke_test.py`. Run it:

```bash
# in one terminal
uv run uvicorn app.main:app --reload

# in another
curl -X POST http://127.0.0.1:8000/scenarios/ \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id": 1, "emails": []}'
uv run python /tmp/mcp_smoke_test.py
```

Expected output ends with `ALL CHECKS PASSED`. The test verifies tool discovery, resource discovery, resource fetch, a happy-path tool call, the `email_id` global-counter rule, and that a deliberate 404 surfaces correctly.

---

## When something breaks, debug in this order

1. **Is FastAPI up?** `curl http://localhost:8000/` should return `{"status": "ok", ...}`.
2. **Is a scenario seeded?** `curl http://localhost:8000/scenarios/` should not be `[]`.
3. **Does the MCP server start?** `uv run python -m mcp_server` should print nothing and wait for stdio input. Ctrl+C to exit. If it crashes on import, the traceback tells you what's wrong.
4. **Does FastAPI receive the call?** Check the uvicorn terminal — every tool call prints an HTTP access log line. Missing log line = the MCP server never made the request.
5. **Is the request shape right?** Compare what FastMCP sent (in uvicorn logs as a 422) against the Pydantic model in `app/models/`.
