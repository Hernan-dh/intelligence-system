# Intelligence System

A local-first, production-oriented knowledge API built with FastAPI, LangGraph, SQLite, and optional Phoenix tracing. It retrieves internal procedures, keeps conversation state by thread, and returns an answer with its sources and execution trace.

The system runs end-to-end without paid credentials: its local retrieval and deterministic fallback make the API testable offline. Responses are English-first, including the deterministic fallback. An OpenAI key is optional and enables model-generated routing and grounded writing.

## What it demonstrates

- Async FastAPI endpoints with Pydantic request and response contracts.
- Hybrid local retrieval: lexical matching plus deterministic vector similarity, persisted in SQLite.
- LangGraph supervisor, researcher, and writer nodes with SQLite-backed conversation checkpoints.
- Knowledge ingestion through a validated HTTP endpoint rather than source-code edits.
- Optional Arize Phoenix observability that cannot become an API availability dependency.
- A reproducible test suite, secret-aware verification, and a guarded commit-and-push helper.

## Quick start

Requires Python 3.12+. Docker is optional but recommended for the complete API + Phoenix stack.

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to use the API interactively. Do not commit `.env`; it is ignored and `.env.example` contains only placeholders.

To start the API and Phoenix together:

```powershell
docker compose up --build
```

The API is served on port `8000` and Phoenix on port `6006`.

## Example

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/v1/chat `
  -ContentType 'application/json' `
  -Body '{"message":"¿Cómo solicito acceso VPN?","thread_id":"demo-1"}'
```

The response contains `answer`, `sources`, `trace`, and `thread_id`. Add or update knowledge without changing code:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/v1/documents `
  -ContentType 'application/json' `
  -Body '{"document_id":"vacaciones","title":"Licencias","content":"Las licencias se solicitan desde el portal interno con al menos diez días de anticipación.","metadata":{"area":"rrhh"}}'
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | empty | Enables the optional model-backed supervisor and writer. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model used when an OpenAI key is configured. |
| `DATABASE_PATH` | `data/intelligence.db` | Local SQLite document and checkpoint database. |
| `PHOENIX_COLLECTOR_ENDPOINT` | empty | Optional OpenTelemetry collector endpoint. |

See [architecture](docs/ARCHITECTURE.md) for the data flow and trust boundaries, and [operations](docs/OPERATIONS.md) for verification, deployment, and publication.

## Observability

When `PHOENIX_COLLECTOR_ENDPOINT` is configured, each chat request emits an OpenTelemetry span named `intelligence.chat`. Inspect `session.id`, `rag.source_count`, `input.value`, and `output.value` in Phoenix to follow a conversation and compare response behavior. Run `scripts/run_observability_checks.ps1` after starting Docker Compose to send the five repeatable scenarios, including two requests for the same thread.

## Quality and publication

```powershell
python scripts/verify.py
python scripts/publish.py --preview
```

`verify.py` checks public-source hygiene and runs the tests. `publish.py` presents the exact files and proposed Conventional Commit, then requires typing `PUBLISH` before it stages, commits, and pushes. It never force-pushes. This directory must be its own Git repository before publishing; see the operations guide.

## Limitations

The local vector representation is deliberately deterministic and lightweight; it is suited to the included demonstration corpus, not a substitute for a semantic embedding model on a large production corpus. SQLite suits a single-node deployment. Authentication, authorization, rate limiting, and an external document lifecycle are intentionally outside this demonstration's scope.
