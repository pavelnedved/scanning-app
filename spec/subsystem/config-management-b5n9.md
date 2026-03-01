# Configuration Management

> **ID**: `config-management-b5n9`
> **Files**: `scanning_app/config.py`
> **Language**: Python 3.14
> **Total Lines**: 34

## Business Capability

This subsystem centralizes all runtime configuration for the application: the set of accepted image file types, their MIME type mappings, the Claude AI model settings, and the full system prompt that instructs Claude how to parse a grocery receipt. Other subsystems import constants from here rather than hardcoding values.

## Public Interface

| Name | File | Kind | Signature | Description |
|------|------|------|-----------|-------------|
| `ALLOWED_EXTENSIONS` | `config.py:L6` | const | `set[str]` | Set of accepted image file extensions |
| `MIME_TYPES` | `config.py:L8` | const | `dict[str, str]` | Maps file extension → MIME type string |
| `CLAUDE_MODEL` | `config.py:L16` | const | `str` | Claude model identifier, overridable via env |
| `CLAUDE_MAX_TOKENS` | `config.py:L17` | const | `int` | Token ceiling for Claude responses, overridable via env |
| `SYSTEM_PROMPT` | `config.py:L19` | const | `str` | Multi-line prompt defining the receipt parsing contract |

## Data Model

### Owned Types (defined in this subsystem)

This subsystem defines no classes. It owns the following configuration shapes:

#### `ALLOWED_EXTENSIONS` value set

`{"png", "jpg", "jpeg", "webp", "gif"}` (`config.py:L6`)

#### `MIME_TYPES` mapping

| Extension | MIME Type |
|-----------|-----------|
| `png` | `image/png` |
| `jpg` | `image/jpeg` |
| `jpeg` | `image/jpeg` |
| `webp` | `image/webp` |
| `gif` | `image/gif` |

Defined at: `config.py:L8-14`

#### Receipt JSON Schema (implicit — embedded in `SYSTEM_PROMPT`)

The `SYSTEM_PROMPT` (`config.py:L19-33`) defines the expected Claude output structure:

| Field | Type | Description |
|-------|------|-------------|
| `metadata.store_name` | string or null | Name of the store |
| `metadata.store_address` | string or null | Address |
| `metadata.date` | string (YYYY-MM-DD) or null | Transaction date |
| `metadata.time` | string (HH:MM) or null | Transaction time |
| `metadata.receipt_number` | string or null | Receipt identifier |
| `metadata.cashier` | string or null | Cashier name |
| `metadata.payment_method` | string or null | Payment method |
| `metadata.subtotal` | number or null | Pre-tax total |
| `metadata.tax` | number or null | Tax amount |
| `metadata.total` | number or null | Grand total |
| `metadata.amount_tendered` | number or null | Amount paid |
| `metadata.change` | number or null | Change returned |
| `metadata.currency` | string or null | Currency code |
| `items[].name` | string | Line item name |
| `items[].quantity` | number | Quantity |
| `items[].unit` | string | "each" or weight/volume string |
| `items[].unit_price` | number or null | Per-unit price |
| `items[].total_price` | number or null | Line total |
| `items[].category` | string or null | Item category |
| `items[].on_sale` | boolean | Whether item was on sale |
| `items[].discount` | number or null | Discount amount |
| `item_count` | integer | Count of items in `items` array |
| `error` | string | Present only when not a receipt: `"not_a_receipt"` |

Source: `config.py:L19-33` (system prompt text, not a formal type definition)

## Internal Logic

### Configuration Loading

`config.py:L4` calls `load_dotenv()` at module import time, before reading env vars. `CLAUDE_MODEL` and `CLAUDE_MAX_TOKENS` are read via `os.environ.get(...)` with defaults at module load (`config.py:L16-17`). All other constants (`ALLOWED_EXTENSIONS`, `MIME_TYPES`, `SYSTEM_PROMPT`) are hardcoded literals.

### System Prompt Contract

`SYSTEM_PROMPT` instructs Claude to:
1. Return ONLY valid JSON with no surrounding text, markdown, or explanation (`config.py:L19-20`)
2. Return `{"error": "not_a_receipt"}` if the image is not a grocery receipt (`config.py:L22-23`)
3. Otherwise return the structured receipt object with `metadata`, `items`, and `item_count` keys (`config.py:L25-33`)
4. All unknown/unreadable fields must be null; all monetary values must be numbers, not strings (`config.py:L33`)

## Implementation Map

| File | Role in this subsystem |
|------|----------------------|
| `scanning_app/config.py` | Defines all constants; loads dotenv and reads env vars at module import time |

## Dependencies

- **Internal** (other subsystems): None
- **Cross-project**: None
- **External** (third-party): `python-dotenv`
- **Runtime**: `CLAUDE_MODEL` env var (default: `"claude-sonnet-4-6"`), `CLAUDE_MAX_TOKENS` env var (default: `"8000"`)

## Side Effects

- `load_dotenv()` mutates `os.environ` at module import time (`config.py:L4`)

## Unknowns

### Lexical Unknowns
None.

### Boundary Unknowns
- [BOUNDARY UNKNOWN: `CLAUDE_MAX_TOKENS` — no minimum or maximum enforced; any integer from env is accepted] (`config.py:L17`) — Resolution: no validation in source or tests; the Anthropic API may reject values outside its allowed range but no guard exists here.

### Goal Unknowns
- [GOAL UNKNOWN: `gif` is included in `ALLOWED_EXTENSIONS` and `MIME_TYPES` — purpose of supporting animated GIF format for receipt images is undetermined] (`config.py:L6,L14`)
