# API Usage Examples

> Extracted from source code. All examples are grounded in actual code or tests.

## POST /parse-receipt — Successful Upload

**Source**: `tests/unit/test_routes.py:L68-78`, `tests/conftest.py:L8-37`

```python
import io
import json
import requests

# Upload a receipt image
with open("receipt.jpg", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:5000/parse-receipt",
        files={"file": ("receipt.jpg", f, "image/jpeg")},
    )

data = response.json()
# data["success"] is True on success
# data["metadata"] contains store info
# data["items"] is a list of line items
# data["item_count"] is the integer count of items
```

**What it does**: Sends a multipart POST with the receipt image. On success, returns HTTP 200 with structured JSON containing store metadata, line items, and item count.
**Preconditions**: Server running at 127.0.0.1:5000; `ANTHROPIC_API_KEY` set in environment; file is a non-empty image with extension png, jpg, jpeg, webp, or gif.
**Expected result**: HTTP 200 JSON body with keys `success`, `metadata`, `items`, `item_count`.

---

## POST /parse-receipt — Error: No File

**Source**: `tests/unit/test_routes.py:L5-9`

```python
import requests
response = requests.post("http://127.0.0.1:5000/parse-receipt")
# response.status_code == 400
# response.json() == {"success": False, "error": "no_file", "message": "No file was included in the request."}
```

**What it does**: POST with no multipart body returns a 400 with `error: "no_file"`.
**Preconditions**: Server running.
**Expected result**: HTTP 400, `{"success": false, "error": "no_file", "message": "No file was included in the request."}`.

---

## POST /parse-receipt — Error: Invalid File Type

**Source**: `tests/unit/test_routes.py:L23-32`

```python
import io, requests
response = requests.post(
    "http://127.0.0.1:5000/parse-receipt",
    files={"file": ("receipt.pdf", io.BytesIO(b"data"), "application/pdf")},
)
# response.status_code == 400
# response.json()["error"] == "invalid_file_type"
# response.json()["message"] contains "pdf" and lists accepted types
```

**What it does**: A file with a non-image extension (e.g., .pdf, .txt) is rejected before any API call is made.
**Preconditions**: Server running.
**Expected result**: HTTP 400, `{"success": false, "error": "invalid_file_type", "message": "Unsupported file type 'pdf'. Accepted: gif, jpeg, jpg, png, webp."}`.

---

## POST /parse-receipt — Error: Not a Receipt

**Source**: `tests/unit/test_routes.py:L92-103`

```python
import io, requests
# Server will call Claude, which responds {"error": "not_a_receipt"}
response = requests.post(
    "http://127.0.0.1:5000/parse-receipt",
    files={"file": ("photo.jpg", io.BytesIO(b"image data"), "image/jpeg")},
)
# response.status_code == 422
# response.json()["error"] == "not_a_receipt"
```

**What it does**: When Claude determines the image is not a grocery receipt, the endpoint returns 422 Unprocessable Entity.
**Preconditions**: Server running; image is a valid JPEG but does not depict a grocery receipt.
**Expected result**: HTTP 422, `{"success": false, "error": "not_a_receipt", "message": "Could not identify a grocery receipt in the provided image."}`.

---

## Flask Test Client — Injecting a Mock Anthropic Client

**Source**: `tests/conftest.py:L40-56`

```python
import json
from unittest.mock import MagicMock
from scanning_app import create_app

SAMPLE_RECEIPT = {
    "metadata": {"store_name": "Test Mart", ...},
    "items": [{"name": "Apple", ...}],
    "item_count": 1,
}

mock_client = MagicMock()
mock_response = MagicMock()
mock_response.content = [MagicMock(text=json.dumps(SAMPLE_RECEIPT))]
mock_client.messages.create.return_value = mock_response

app = create_app({"TESTING": True, "ANTHROPIC_CLIENT": mock_client})
test_client = app.test_client()
```

**What it does**: Demonstrates the dependency injection pattern: `create_app({"ANTHROPIC_CLIENT": mock_client})` replaces the real Anthropic API client with a mock for unit testing without network calls.
**Preconditions**: `scanning_app` package importable.
**Expected result**: A Flask test client that returns controlled receipt data without hitting the Anthropic API.

---

## Running Regression Tests Against Real Receipts

**Source**: `tests/regression/conftest.py:L7-28`, `tests/regression/test_regression.py:L10-32`

```bash
# 1. Place receipt images in tests/regression/receipts/
#    Expected filenames: tesco_1994.jpg, supermarket_de.jpg, walmart_us.jpg

# 2. Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Run only regression tests
pytest tests/regression/ -v

# Results are written to tests/regression/results/<stem>.json for human review
```

**What it does**: Sends real receipt images to the actual Anthropic API and validates that the response contains `metadata`, `items`, `item_count`, and that `item_count == len(items)`. Results are saved as JSON files for human inspection.
**Preconditions**: `ANTHROPIC_API_KEY` env var set; receipt image files present in `tests/regression/receipts/`; if images are absent, tests are skipped.
**Expected result**: JSON files written to `tests/regression/results/`; all structural assertions pass.
