# Receipt Parse Request Workflow

> **ID**: `parse-receipt-flow-q8v5`
> **Trigger**: HTTP POST to `/parse-receipt` with a multipart form upload containing a `file` field
> **Subsystems involved**: [^http-api-r6d3], [^receipt-parsing-w4j1], [^config-management-b5n9]

## Overview

A client submits a receipt image file. The HTTP layer validates the upload, the parsing subsystem encodes and sends it to Claude AI, and the structured receipt data (or an error) is returned as JSON.

## Sequence

1. **[^http-api-r6d3]** — receives `POST /parse-receipt`; checks that `"file"` key is present in `request.files` (`routes.py:L16`)
2. **[^http-api-r6d3]** — checks that `file.filename` is non-empty (`routes.py:L25`)
3. **[^http-api-r6d3]** — calls `get_extension(file.filename)` from [^receipt-parsing-w4j1] and validates against `ALLOWED_EXTENSIONS` from [^config-management-b5n9] (`routes.py:L32-38`)
4. **[^http-api-r6d3]** — reads all file bytes into memory; checks non-empty (`routes.py:L40-46`)
5. **[^http-api-r6d3]** — calls `_get_client()` to resolve the Anthropic client, then calls `parse_receipt_image(image_bytes, ext, client)` (`routes.py:L49`)
6. **[^receipt-parsing-w4j1]** — base64-encodes the image bytes; looks up MIME type from [^config-management-b5n9] `MIME_TYPES` (`parser.py:L25-26`)
7. **[^receipt-parsing-w4j1]** — sends multipart message to Anthropic API using model and token settings from [^config-management-b5n9] (`parser.py:L29-52`)
8. **[^receipt-parsing-w4j1]** — strips response text and parses JSON (`parser.py:L61-65`)
9. **[^receipt-parsing-w4j1]** — checks for `{"error": "not_a_receipt"}` sentinel; if absent, returns parsed dict (`parser.py:L74-77`)
10. **[^http-api-r6d3]** — injects `"success": True` into the dict and returns 200 JSON response (`routes.py:L63-64`)

## Data Flow

```
Input: multipart/form-data POST with "file" field (image/png, image/jpeg, image/webp, image/gif)
  → [^http-api-r6d3] validates: presence, filename, extension, non-empty bytes
  → raw bytes (bytes object)
  → [^receipt-parsing-w4j1] encodes to base64 string, wraps in Claude API message
  → Anthropic API call (network) with SYSTEM_PROMPT from [^config-management-b5n9]
  → raw JSON text from Claude response
  → [^receipt-parsing-w4j1] strips markdown fences (via character-strip), parses JSON
  → Python dict matching Receipt JSON Schema (see [^config-management-b5n9])
  → [^http-api-r6d3] adds "success": true
  → Output: 200 JSON response body with metadata, items, item_count, success fields
```

## Error Paths

| Stage | Failure | Handler | Response |
|-------|---------|---------|----------|
| Step 1 | `"file"` not in request | [^http-api-r6d3] `routes.py:L16-21` | 400 `{"error": "no_file"}` |
| Step 2 | Empty filename | [^http-api-r6d3] `routes.py:L23-30` | 400 `{"error": "no_file"}` |
| Step 3 | Extension not in ALLOWED_EXTENSIONS | [^http-api-r6d3] `routes.py:L32-38` | 400 `{"error": "invalid_file_type"}` |
| Step 4 | Zero bytes read | [^http-api-r6d3] `routes.py:L41-46` | 400 `{"error": "empty_file"}` |
| Step 7 | Anthropic API exception | [^receipt-parsing-w4j1] `parser.py:L53-59` raises `ReceiptParseError("api_error", ..., 500)` → [^http-api-r6d3] `routes.py:L56-61` | 500 `{"error": "api_error"}` |
| Step 8 | `json.JSONDecodeError` | [^receipt-parsing-w4j1] `parser.py:L66-72` raises `ReceiptParseError("parse_error", ..., 500)` → [^http-api-r6d3] `routes.py:L56-61` | 500 `{"error": "parse_error"}` |
| Step 9 | `{"error": "not_a_receipt"}` in response | [^receipt-parsing-w4j1] `parser.py:L74-75` raises `NotAReceiptError` → [^http-api-r6d3] `routes.py:L50-55` | 422 `{"error": "not_a_receipt"}` |

## Unknowns

### Boundary Unknowns
- [BOUNDARY UNKNOWN: no maximum upload size enforced — `file.read()` at `routes.py:L40` reads the entire multipart body into memory with no `MAX_CONTENT_LENGTH` guard] — Resolution: traced all validation steps; no size check exists before or during read.

### Goal Unknowns
None.
