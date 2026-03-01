# Receipt Image Parsing

> **ID**: `receipt-parsing-w4j1`
> **Files**: `scanning_app/parser.py`
> **Language**: Python 3.14
> **Total Lines**: 78

## Business Capability

This subsystem handles the core intelligence of the application: it takes raw image bytes of a grocery receipt, sends them to the Claude AI vision model with a structured prompt, and returns a Python dict representing the extracted receipt data. It also defines the exception types that communicate parse failures back to callers.

## Public Interface

| Name | File | Kind | Signature | Description |
|------|------|------|-----------|-------------|
| `ReceiptParseError` | `parser.py:L8` | class | `ReceiptParseError(error_code, message, http_status)` | Exception carrying HTTP error context for caller |
| `NotAReceiptError` | `parser.py:L16` | class | `NotAReceiptError(message)` | Exception raised when image is not a grocery receipt |
| `get_extension` | `parser.py:L20` | function | `get_extension(filename: str) -> str` | Extracts lowercase file extension from filename |
| `parse_receipt_image` | `parser.py:L24` | function | `parse_receipt_image(image_bytes: bytes, ext: str, client) -> dict` | Main parsing function; returns structured receipt dict |

## Data Model

### Owned Types (defined in this subsystem)

| Type | File | Kind | Description |
|------|------|------|-------------|
| `ReceiptParseError` | `parser.py:L8` | exception class | Structured parse failure with HTTP error metadata |
| `NotAReceiptError` | `parser.py:L16` | exception class | Sentinel for non-receipt images |

#### `ReceiptParseError`

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `error_code` | `str` | Machine-readable error code (e.g. `"api_error"`, `"parse_error"`) | Set in constructor; no validation |
| `message` | `str` | Human-readable error message | Set in constructor |
| `http_status` | `int` | HTTP status code for the HTTP layer | Set in constructor; no validation |

Defined at: `parser.py:L8-13`
Used by: [^http-api-r6d3] (maps `error_code` → JSON `error` field, `http_status` → HTTP response code)

#### `NotAReceiptError`

Extends `Exception` with no additional fields (`parser.py:L16-17`). Used as a sentinel — callers check its type, not its message.
Used by: [^http-api-r6d3] (maps to 422 response)

### Consumed Types (external — owned elsewhere)

| Type | Source | SOT Owner | Description |
|------|--------|-----------|-------------|
| `Anthropic` client | injected via `client` parameter | External: Anthropic SDK | The messages API client; must have `.messages.create(...)` method |

The return type of `parse_receipt_image` is an untyped `dict` whose schema is governed by [^config-management-b5n9]'s `SYSTEM_PROMPT`. See the Receipt JSON Schema in [^config-management-b5n9] for the expected fields.

## Internal Logic

### Image Encoding

`parse_receipt_image` base64-encodes `image_bytes` using `base64.standard_b64encode` and decodes to UTF-8 string (`parser.py:L25`). The MIME type is looked up from [^config-management-b5n9]'s `MIME_TYPES` dict using the provided `ext` (`parser.py:L26`).

### Claude API Call

Constructs and sends a multipart message to Claude (`parser.py:L29-52`):
- `model`: from [^config-management-b5n9] `CLAUDE_MODEL`
- `max_tokens`: from [^config-management-b5n9] `CLAUDE_MAX_TOKENS`
- `system`: the full `SYSTEM_PROMPT` from [^config-management-b5n9]
- `messages`: single user message with two content blocks:
  1. `type: "image"` with `source.type: "base64"`, `source.media_type`, and `source.data` (the encoded bytes)
  2. `type: "text"` with the literal string `"Parse this grocery receipt and return the JSON."`

Any exception from `client.messages.create(...)` is caught, printed to stdout (`parser.py:L54`), and re-raised as `ReceiptParseError(error_code="api_error", ..., http_status=500)` (`parser.py:L53-59`).

### Response Cleaning & JSON Parsing

The raw response text is extracted from `response.content[0].text` and stripped (`parser.py:L61`):
```python
raw_text = response.content[0].text.strip().strip("```json").strip("```")
```

> **Note**: `str.strip(chars)` strips any character in the `chars` set from both ends — it does NOT strip the literal substring `"```json"`. This call strips any character in the set `{'\`', 'j', 's', 'o', 'n'}` from the ends of the string. See [tech_finding/improvements.md](../tech_finding/improvements.md) for details.

The cleaned text is logged at INFO level and parsed with `json.loads` (`parser.py:L64-65`). `json.JSONDecodeError` is caught, logged at ERROR level, and re-raised as `ReceiptParseError(error_code="parse_error", ..., http_status=500)` (`parser.py:L66-72`).

### Receipt vs Non-Receipt Detection

If the parsed dict contains `{"error": "not_a_receipt"}` (matching the `SYSTEM_PROMPT`'s sentinel), `NotAReceiptError` is raised (`parser.py:L74-75`). Otherwise the dict is returned as-is (`parser.py:L77`).

### Extension Extraction

`get_extension(filename)` splits on `"."` from the right (`rsplit(".", 1)`), returns the last segment lowercased, or `""` if no dot exists (`parser.py:L20-21`). Multi-dot filenames (e.g. `my.receipt.png`) return only the final extension.

## Implementation Map

| File | Role in this subsystem |
|------|----------------------|
| `scanning_app/parser.py` | Defines error types, image encoding, Claude API call, response cleaning, JSON parsing, and receipt/non-receipt detection |

## Dependencies

- **Internal** (other subsystems): Imports `ALLOWED_EXTENSIONS`, `MIME_TYPES`, `CLAUDE_MODEL`, `CLAUDE_MAX_TOKENS`, `SYSTEM_PROMPT` from [^config-management-b5n9]
- **Cross-project**: None
- **External** (third-party): `anthropic` (SDK, passed in as `client`); `base64`, `json`, `logging` (stdlib)
- **Runtime**: None directly; inherits Claude settings through imported constants

## Side Effects

- Prints exception to stdout on API error (`parser.py:L54`) — mixes `print` with `logging`
- Writes log lines via `logging.info` and `logging.error` (`parser.py:L64`, `parser.py:L67`)
- Makes a network call to the Anthropic API (`parser.py:L29-52`)

## Unknowns

### Lexical Unknowns
None.

### Boundary Unknowns
- [BOUNDARY UNKNOWN: `response.content[0]` — no check that `response.content` is non-empty or that `content[0]` has a `.text` attribute] (`parser.py:L61`) — Resolution: no guard or assertion found; an unexpected Claude response shape (e.g. empty content list) would raise `IndexError` or `AttributeError`, not a `ReceiptParseError`.

### Goal Unknowns
- [GOAL UNKNOWN: `print(e)` used at `parser.py:L54` instead of `logging.error` or `logging.exception` — purpose of using `print` rather than the logging framework already used elsewhere in the same file is undetermined] (`parser.py:L54`)
