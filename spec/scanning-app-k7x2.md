# scanning-app — System Summary

> **ID**: `scanning-app-k7x2`
> Auto-generated from source analysis. Grounded in code — not assumptions.
> Last generated: 2026-03-01

## Project Identity

- **Name**: scanning-app (from git remote: `git@github.com:pavelnedved/scanning-app.git`)
- **Language**: Python 3.14
- **Framework**: Flask 3.x (gunicorn for production)
- **Entry point(s)**: `app.py` (development: `python app.py`; production: `gunicorn --bind 0.0.0.0:8080 --workers 2 app:app`)

## What This System Does

The scanning-app is a Flask web API that accepts grocery receipt images via HTTP POST and returns structured JSON representing the receipt's contents. It delegates all image understanding to the Anthropic Claude vision model, which is instructed via a hardcoded system prompt to extract store metadata, line items, quantities, and prices. The system performs file validation (type, presence, non-empty), handles Claude API failures with typed exceptions, and maps all outcomes to structured JSON HTTP responses. It is containerized via Docker for production deployment on port 8080.

## Source of Truth

_No source of truth declared. Add SOT declarations to spec/changelog/concept.txt to establish this service's authoritative domains._

_To declare SOT, add entries to concept.txt using the format:_
_`[SOT] <topic> — <description of what this service authoritatively owns>`_

## Subsystems (Business Capabilities)

| Business Capability | Files | What it does | Ref |
|---------------------|-------|-------------|-----|
| Application Startup & Initialization | `app.py`, `scanning_app/__init__.py` | Assembles the Flask app via factory pattern, loads env, registers blueprint, configures dev server | [^app-startup-p3m8] |
| Configuration Management | `scanning_app/config.py` | Centralizes allowed file types, MIME maps, Claude model settings, and the receipt-parsing system prompt | [^config-management-b5n9] |
| Receipt Image Parsing | `scanning_app/parser.py` | Base64-encodes images, calls Claude AI API, strips/parses JSON response, raises typed exceptions on failure | [^receipt-parsing-w4j1] |
| HTTP API | `scanning_app/routes.py` | Validates file uploads, coordinates with parser, maps outcomes to structured JSON HTTP responses | [^http-api-r6d3] |

## Workflows

| Workflow | Trigger | Subsystems | Ref |
|----------|---------|------------|-----|
| Receipt Parse Request | `POST /parse-receipt` multipart upload | [^http-api-r6d3], [^receipt-parsing-w4j1], [^config-management-b5n9] | [^parse-receipt-flow-q8v5] |

## Module Dependency Graph

```
[^app-startup-p3m8] → [^http-api-r6d3] (imports bp Blueprint)
[^http-api-r6d3] → [^receipt-parsing-w4j1] (imports NotAReceiptError, ReceiptParseError, get_extension, parse_receipt_image)
[^http-api-r6d3] → [^config-management-b5n9] (imports ALLOWED_EXTENSIONS)
[^receipt-parsing-w4j1] → [^config-management-b5n9] (imports ALLOWED_EXTENSIONS, MIME_TYPES, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, SYSTEM_PROMPT)
```

## Shared Data Model

None — all data types are subsystem-local. The receipt JSON schema is defined as a prose description inside `SYSTEM_PROMPT` in [^config-management-b5n9] and is not shared as a formal type across subsystems.

## Cross-Cutting Concerns

- **Error handling**: Two-level strategy — [^receipt-parsing-w4j1] raises typed exceptions (`ReceiptParseError`, `NotAReceiptError`) that [^http-api-r6d3] catches and maps to HTTP responses. Anthropic exceptions are caught broadly with `except Exception` and re-raised as `ReceiptParseError`.
- **Configuration**: Module-level constants in [^config-management-b5n9], read at import time via `os.environ.get`. `load_dotenv()` called both in `config.py:L4` and `__init__.py:L6` — both calls are safe (dotenv is idempotent).
- **Logging**: `logging` module used in [^receipt-parsing-w4j1] (`logging.info`, `logging.error`); `print(e)` also used in one error path (`parser.py:L54`).
- **Testing**: pytest with `pytest-mock` and `pytest-cov`; unit tests mock the Anthropic client via `app.config`; regression tests run against the real API and require image fixture files. No coverage configuration observed in source.
- **Containerization**: `Dockerfile` builds from `python:3.14-slim`, installs dependencies, copies `app.py` and `scanning_app/`, sets production env vars (`FLASK_HOST=0.0.0.0`, `FLASK_PORT=8080`, `FLASK_DEBUG=false`), and runs gunicorn with 2 workers.

## Unknowns Summary

| Type | Count | Action Required |
|------|-------|----------------|
| Lexical | 0 | — |
| Boundary | 4 | Add validation, assertions, or doc comments |
| Goal | 3 | Human must explain WHY — add comment |
| **Total** | **7** | |

### Top Unknowns

- [BOUNDARY] `str.strip("```json")` strips characters not substrings — may corrupt valid JSON responses — see [^receipt-parsing-w4j1]
- [BOUNDARY] No upload size limit on `file.read()` — unbounded memory on large uploads — see [^http-api-r6d3]
- [BOUNDARY] No guard on `response.content[0]` — unexpected Claude response shape raises unhandled exception — see [^receipt-parsing-w4j1]
- [BOUNDARY] `CLAUDE_MAX_TOKENS` has no min/max enforcement — any integer accepted from env — see [^config-management-b5n9]
- [GOAL] `print(e)` used instead of `logging` in `parser.py:L54` — purpose undetermined — see [^receipt-parsing-w4j1]
- [GOAL] `GET /` returns "Hello World" — purpose undetermined (health check? placeholder?) — see [^http-api-r6d3]
- [GOAL] `gif` format included in `ALLOWED_EXTENSIONS` — purpose of animated GIF support for receipts undetermined — see [^config-management-b5n9]

## Tech Findings

- **Patterns observed**: 5 — see [tech_finding/tech_pattern.md](tech_finding/tech_pattern.md)
- **Improvements found**: 5 — see [tech_finding/improvements.md](tech_finding/improvements.md)

## External Spec References

_No sibling project specs found. Cross-project references are not available._

### SOT Collisions

_None detected._

### Cross-SOT Divergences

_None detected._

## Changelog

_Human-maintained context — see [changelog/](changelog/) for feature notes, decisions, and context provided by the team._
