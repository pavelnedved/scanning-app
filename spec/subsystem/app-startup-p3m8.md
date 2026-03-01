# Application Startup & Initialization

> **ID**: `app-startup-p3m8`
> **Files**: `app.py`, `scanning_app/__init__.py`
> **Language**: Python 3.14
> **Total Lines**: 27

## Business Capability

This subsystem assembles the Flask application from its components and configures the runtime server. It provides the application factory that test code can call with overrides, and the production entry point that reads server settings from the environment.

## Public Interface

| Name | File | Kind | Signature | Description |
|------|------|------|-----------|-------------|
| `create_app` | `scanning_app/__init__.py:L5` | function | `create_app(config_override: dict \| None = None) -> Flask` | Creates and configures the Flask application instance |
| `app` | `app.py:L4` | module-level variable | `app = create_app()` | The application instance used by gunicorn in production |

## Data Model

None — this subsystem operates on primitive types and function arguments only.

## Internal Logic

### App Factory Pattern

1. `create_app` calls `load_dotenv()` immediately (`scanning_app/__init__.py:L6`) to load `.env` before any config reads
2. Creates a `Flask(__name__)` instance (`scanning_app/__init__.py:L7`)
3. If `config_override` is provided, applies it via `app.config.update(config_override)` (`scanning_app/__init__.py:L9-10`) — used by tests to inject a mock Anthropic client
4. Imports and registers the `bp` Blueprint from [^http-api-r6d3] (`scanning_app/__init__.py:L12-13`)
5. Returns the configured `app`

### Entry Point Configuration

`app.py:L6-11` reads three environment variables to configure the development server:

| Env Var | Default | Behavior |
|---------|---------|----------|
| `FLASK_DEBUG` | `"true"` | Parsed as `.lower() == "true"` — any non-"true" string disables debug mode |
| `FLASK_HOST` | `"127.0.0.1"` | Bind address for `app.run()` |
| `FLASK_PORT` | `"5000"` | Port cast to `int` |

In production (Docker), the entry point is gunicorn (`Dockerfile:L17`) — the `if __name__ == "__main__"` block is not executed; `app.py:L4` is evaluated to create the `app` module attribute that gunicorn imports.

## Implementation Map

| File | Role in this subsystem |
|------|----------------------|
| `scanning_app/__init__.py` | Defines `create_app` factory: loads env, creates Flask instance, applies config overrides, registers blueprint |
| `app.py` | Module-level entry point: calls `create_app()`, runs dev server with env-configured host/port/debug |

## Dependencies

- **Internal** (other subsystems): Imports `bp` Blueprint from [^http-api-r6d3]
- **Cross-project**: None
- **External** (third-party): `flask`, `python-dotenv`
- **Runtime**: `FLASK_DEBUG`, `FLASK_HOST`, `FLASK_PORT` env vars (all optional with defaults); `.env` file (loaded via dotenv)

## Side Effects

- `load_dotenv()` mutates `os.environ` for the process at call time (`scanning_app/__init__.py:L6`)
- `app.run(...)` binds a TCP socket and blocks until the process is killed (development server only)

## Unknowns

### Lexical Unknowns
None.

### Boundary Unknowns
- [BOUNDARY UNKNOWN: `FLASK_PORT` cast — `int()` cast on `os.environ.get("FLASK_PORT", "5000")` will raise `ValueError` if the env var contains a non-integer string] (`app.py:L10`) — Resolution: no validation or try/except guards this cast in the source.

### Goal Unknowns
None.
