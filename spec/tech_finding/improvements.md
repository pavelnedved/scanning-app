# Improvements & Potential Issues

> Observations about possible bugs, missing validations, and improvement opportunities.
> Grounded in actual code — not speculative best-practice wishlists.

## Potential Bugs

### `str.strip()` Strips Characters, Not Substrings

**Location**: `scanning_app/parser.py:L61`
**What**: The code strips markdown fences from Claude's response text using:
```python
raw_text = response.content[0].text.strip().strip("```json").strip("```")
```
**Risk**: `str.strip(chars)` removes any character in the `chars` argument from both ends of the string — it does NOT strip the literal substring `"```json"`. The call `.strip("```json")` strips any character in the set `{'\`', 'j', 's', 'o', 'n'}` from both ends. A valid JSON response that starts or ends with 'n' (e.g., `null`) or 'j' would have those characters silently removed, producing invalid JSON or a subtly wrong result.
**Evidence**: Python docs for `str.strip([chars])`: "The chars argument is not a prefix or suffix; rather, all combinations of its values are stripped." A response of `{"key": "json"}` ending with `}` is fine, but a response ending with a valid JSON field name containing {j, s, o, n} characters could be truncated.

---

## Missing Validations

### No Upload Size Limit

**Location**: `scanning_app/routes.py:L40`
**What's missing**: `file.read()` is called with no maximum content length check. Flask's `MAX_CONTENT_LENGTH` config key is not set in `create_app` (`scanning_app/__init__.py:L5-15`).
**Impact**: A client can upload an arbitrarily large file, causing the server to read all bytes into memory before rejecting or processing the request. Under gunicorn with 2 workers (`Dockerfile:L17`), a large upload will consume significant memory per worker.

---

### No Guard on `response.content[0]`

**Location**: `scanning_app/parser.py:L61`
**What's missing**: No check that `response.content` is non-empty and that `response.content[0]` has a `.text` attribute before accessing it.
**Impact**: An unexpected Claude API response (e.g., an empty `content` list, a tool-use block, or a content block without `.text`) will raise `IndexError` or `AttributeError` rather than a `ReceiptParseError`. The unhandled exception propagates to Flask's default error handler, returning a 500 with no structured JSON body matching the API's error schema.

---

## Improvement Opportunities

### Mixed Logging: `print` and `logging` in the Same Function

**Location**: `scanning_app/parser.py:L54`
**Current**: On Anthropic API exception, the error is output via `print(e)` (`parser.py:L54`). Other exception handling in the same file uses `logging.error(e)` (`parser.py:L67`) and `logging.info(...)` (`parser.py:L64`).
**Opportunity**: Replace `print(e)` with `logging.exception(e)` or `logging.error(e)` to route all output through the logging framework. `logging.exception` would also capture the traceback.
**Effort**: low

---

### Anthropic Client Created Per Request

**Location**: `scanning_app/routes.py:L10-11`
**Current**: `_get_client()` returns `current_app.config.get("ANTHROPIC_CLIENT") or Anthropic()`. In production (no `ANTHROPIC_CLIENT` in config), a new `Anthropic()` SDK instance is constructed on every request.
**Opportunity**: The Anthropic SDK client manages an `httpx` connection pool internally. Creating a new instance per request bypasses any connection reuse the pool provides. Storing a single `Anthropic()` instance in `app.config` at startup (in `create_app`) would allow connection pooling.
**Effort**: low

---

### `FLASK_PORT` Cast Without Error Handling

**Location**: `app.py:L10`
**Current**: `port=int(os.environ.get("FLASK_PORT", "5000"))` — `int()` raises `ValueError` if `FLASK_PORT` is set to a non-integer string.
**Opportunity**: Wrap in a try/except or validate with a more informative error message at startup.
**Effort**: low

---

### No Type Annotations on Route Functions

**Location**: `scanning_app/routes.py:L10`, `routes.py:L15`, `routes.py:L67`
**Current**: `_get_client`, `parse_receipt`, and `hello_world` have no return type annotations. `_get_client` has no parameter type annotations.
**Opportunity**: Consistent with the existing annotations in `parser.py` (which annotates `get_extension` and `parse_receipt_image` fully) and `__init__.py` (`create_app` is fully annotated), adding return types to the route functions and `_get_client` would complete the type coverage.
**Effort**: low
