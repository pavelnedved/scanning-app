# Tech Patterns

> Observed patterns in the codebase. These are neutral descriptions of how the code is structured — not recommendations.

## Pattern: App Factory with Dependency Injection via Config

**What**: The Flask application is created through a factory function `create_app(config_override)` that accepts an optional dict to override `app.config` entries. This is used to inject a mock Anthropic client during testing.
**Where**: `scanning_app/__init__.py:L5-15`; consumed in `tests/conftest.py:L50-51`
**How it works**: `create_app({"TESTING": True, "ANTHROPIC_CLIENT": mock_client})` calls `app.config.update(config_override)` before registering routes. The route handler `_get_client()` checks `current_app.config.get("ANTHROPIC_CLIENT")` first, falling back to `Anthropic()` in production (`routes.py:L10-11`). This allows unit tests to run without real network calls.

---

## Pattern: Exception-as-Error-Code for HTTP Context Propagation

**What**: `ReceiptParseError` carries `error_code`, `message`, and `http_status` fields. This bundles the HTTP response semantics with the parsing error, so the route handler can map them directly without a separate lookup table.
**Where**: `scanning_app/parser.py:L8-13`; consumed in `scanning_app/routes.py:L56-61`
**How it works**: The parser raises `ReceiptParseError(error_code="api_error", message="...", http_status=500)`. The route handler catches it and uses `e.error_code`, `e.message`, `e.http_status` to build the JSON response. This keeps error definitions co-located with the code that detects them.

---

## Pattern: Sentinel Exception for Non-Receipt Images

**What**: `NotAReceiptError` (an empty `Exception` subclass) is used as a typed sentinel rather than returning an error dict from the parsing function.
**Where**: `scanning_app/parser.py:L16-17`, `parser.py:L74-75`; caught in `scanning_app/routes.py:L50-55`
**How it works**: When Claude returns `{"error": "not_a_receipt"}`, the parser raises `NotAReceiptError` rather than returning it. The route handler catches the exception type to decide on a 422 response. Callers distinguish this condition by exception type, not by inspecting return values.

---

## Pattern: Module-Level Constants with Environment Override

**What**: Configuration constants are module-level variables in `config.py`, with selected values overridable via environment variables. Non-overridable constants are plain literals.
**Where**: `scanning_app/config.py:L6-33`
**How it works**: `CLAUDE_MODEL` and `CLAUDE_MAX_TOKENS` are set via `os.environ.get(key, default)` at module import time. `ALLOWED_EXTENSIONS`, `MIME_TYPES`, and `SYSTEM_PROMPT` are hardcoded literals. `load_dotenv()` is called at the top of `config.py:L4` to populate env vars from `.env` before the reads happen.

---

## Pattern: Blueprint-Based Route Registration

**What**: All application routes are defined in a single `Blueprint` (`bp = Blueprint("main", __name__)`) and registered in the app factory via `app.register_blueprint(bp)`.
**Where**: `scanning_app/routes.py:L7`; `scanning_app/__init__.py:L12-13`
**How it works**: The Blueprint is imported inside `create_app` (deferred import at `__init__.py:L12`) to avoid circular imports. All route definitions live in `routes.py` and are bundled under the `"main"` blueprint with no URL prefix.

---

## Pattern: Multi-Tier Test Structure (Unit + Regression)

**What**: Tests are split into `tests/unit/` (mocked, fast) and `tests/regression/` (real API, requires image files and API key). Shared fixtures are in `tests/conftest.py`; regression-specific fixtures are in `tests/regression/conftest.py`.
**Where**: `tests/conftest.py`, `tests/unit/test_parser.py`, `tests/unit/test_routes.py`, `tests/regression/conftest.py`, `tests/regression/test_regression.py`
**How it works**: Regression tests use `@pytest.mark.parametrize` over `RECEIPT_IMAGES` list and skip if images are missing or `ANTHROPIC_API_KEY` is unset. Results are written to `tests/regression/results/` as JSON for human review. Unit tests use `MagicMock` to control Anthropic responses.
