# HTTP API

> **ID**: `http-api-r6d3`
> **Files**: `scanning_app/routes.py`
> **Language**: Python 3.14
> **Total Lines**: 70

## Business Capability

This subsystem exposes the application's HTTP interface. It validates incoming file uploads, coordinates with the receipt parser, and maps parsing outcomes (success, non-receipt, API error, parse error) to structured JSON HTTP responses. It is the single entry point for all external clients.

## Public Interface

| Name | File | Kind | Signature | Description |
|------|------|------|-----------|-------------|
| `bp` | `routes.py:L7` | Blueprint | `Blueprint("main", __name__)` | Flask Blueprint registered in the app factory |
| `parse_receipt` | `routes.py:L15` | route handler | `POST /parse-receipt` | Validates upload and returns parsed receipt JSON |
| `hello_world` | `routes.py:L67` | route handler | `GET /` | Returns literal "Hello World" |
| `_get_client` | `routes.py:L10` | private function | `_get_client() -> Anthropic` | Returns Anthropic client from app config or creates new instance |

## Data Model

### Owned Types (defined in this subsystem)

None — responses are plain dicts serialized by Flask's `jsonify`.

### Response Shapes

#### Success response — `POST /parse-receipt` → 200

The parsed receipt dict from [^receipt-parsing-w4j1] with `"success": True` injected (`routes.py:L63`). Schema follows the Receipt JSON Schema in [^config-management-b5n9].

#### Error response — all failure cases

```json
{
  "success": false,
  "error": "<error_code>",
  "message": "<human-readable message>"
}
```

| Error Code | HTTP Status | Trigger |
|------------|-------------|---------|
| `"no_file"` | 400 | `"file"` key absent from request, or filename is empty string |
| `"invalid_file_type"` | 400 | File extension not in `ALLOWED_EXTENSIONS` |
| `"empty_file"` | 400 | File uploaded but contains 0 bytes |
| `"not_a_receipt"` | 422 | Claude determined the image is not a grocery receipt |
| `"api_error"` | 500 | Anthropic API call raised an exception |
| `"parse_error"` | 500 | Claude response could not be decoded as JSON |

## Internal Logic

### Client Resolution

`_get_client()` (`routes.py:L10-11`) checks `current_app.config.get("ANTHROPIC_CLIENT")` first. If present (as injected by tests), it is returned. Otherwise a new `Anthropic()` instance is created using the `ANTHROPIC_API_KEY` environment variable (resolved by the Anthropic SDK from env).

### Request Validation Pipeline

For `POST /parse-receipt`, validation proceeds in this order, stopping at the first failure:

1. Check `"file" in request.files` — if absent, return 400 `"no_file"` (`routes.py:L16-21`)
2. Check `file.filename` is truthy — if empty string, return 400 `"no_file"` (`routes.py:L23-30`)
3. Extract extension via `get_extension(file.filename)` from [^receipt-parsing-w4j1] and check against `ALLOWED_EXTENSIONS` from [^config-management-b5n9] — if not allowed, return 400 `"invalid_file_type"` with accepted types listed in the message (`routes.py:L32-38`)
4. Read `image_bytes = file.read()` (`routes.py:L40`)
5. Check `image_bytes` is non-empty — if empty, return 400 `"empty_file"` (`routes.py:L41-46`)

### Parse Dispatch & Error Mapping

After validation, calls `parse_receipt_image(image_bytes, ext, _get_client())` from [^receipt-parsing-w4j1] (`routes.py:L49`):

- `NotAReceiptError` → 422 response with `error: "not_a_receipt"` (`routes.py:L50-55`)
- `ReceiptParseError` → `e.http_status` response with `error: e.error_code`, `message: e.message` (`routes.py:L56-61`)
- Success → injects `parsed["success"] = True` and returns 200 (`routes.py:L63-64`)

### `GET /` Route

Returns the string `"Hello World"` with 200 status (`routes.py:L67-69`).

## Implementation Map

| File | Role in this subsystem |
|------|----------------------|
| `scanning_app/routes.py` | Defines Blueprint, client helper, validation pipeline, error-to-HTTP mapping, and route handlers |

## Dependencies

- **Internal** (other subsystems):
  - Imports `ALLOWED_EXTENSIONS` from [^config-management-b5n9]
  - Imports `NotAReceiptError`, `ReceiptParseError`, `get_extension`, `parse_receipt_image` from [^receipt-parsing-w4j1]
- **Cross-project**: None
- **External** (third-party): `anthropic` (SDK for `Anthropic()` instantiation), `flask` (`Blueprint`, `current_app`, `jsonify`, `request`)
- **Runtime**: `ANTHROPIC_API_KEY` env var (consumed by Anthropic SDK when `_get_client()` creates a new instance)

## Side Effects

- Reads entire file into memory via `file.read()` with no size limit (`routes.py:L40`)
- Makes a network call to Anthropic API (indirectly, via [^receipt-parsing-w4j1])
- May create a new `Anthropic()` SDK instance per request if `ANTHROPIC_CLIENT` is not in `app.config` (`routes.py:L11`)

## Unknowns

### Lexical Unknowns
None.

### Boundary Unknowns
- [BOUNDARY UNKNOWN: `file.read()` has no maximum size constraint] (`routes.py:L40`) — Resolution: traced full validation pipeline; no `content_length` check or `MAX_CONTENT_LENGTH` Flask config applied before read. Memory consumption is unbounded for large uploads.

### Goal Unknowns
- [GOAL UNKNOWN: `GET /` route returns "Hello World" — whether this serves as a health check endpoint, a placeholder, or has another purpose is undetermined] (`routes.py:L67-69`)
