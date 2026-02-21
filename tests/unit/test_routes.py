import io
import json


def test_no_file_in_request(client):
    response = client.post("/parse-receipt")
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "no_file"


def test_empty_filename(client):
    response = client.post(
        "/parse-receipt",
        data={"file": (io.BytesIO(b"data"), "")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "no_file"


def test_invalid_extension_pdf(client):
    response = client.post(
        "/parse-receipt",
        data={"file": (io.BytesIO(b"data"), "receipt.pdf")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "invalid_file_type"
    assert "pdf" in data["message"]


def test_invalid_extension_txt(client):
    response = client.post(
        "/parse-receipt",
        data={"file": (io.BytesIO(b"data"), "receipt.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "invalid_file_type"


def test_no_extension_filename(client):
    response = client.post(
        "/parse-receipt",
        data={"file": (io.BytesIO(b"data"), "receipt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "invalid_file_type"


def test_empty_file_bytes(client):
    response = client.post(
        "/parse-receipt",
        data={"file": (io.BytesIO(b""), "receipt.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "empty_file"


def test_successful_parse_returns_200(client):
    response = client.post(
        "/parse-receipt",
        data={"file": (io.BytesIO(b"fake image data"), "receipt.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "items" in data
    assert "metadata" in data
    assert "item_count" in data


def test_successful_parse_includes_success_true(client):
    response = client.post(
        "/parse-receipt",
        data={"file": (io.BytesIO(b"fake image data"), "receipt.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_not_a_receipt_returns_422(client, mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value.content[0].text = json.dumps(
        {"error": "not_a_receipt"}
    )
    response = client.post(
        "/parse-receipt",
        data={"file": (io.BytesIO(b"fake image data"), "receipt.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 422
    data = response.get_json()
    assert data["error"] == "not_a_receipt"


def test_claude_api_exception_returns_500(client, mock_anthropic_client):
    mock_anthropic_client.messages.create.side_effect = Exception("API error")
    response = client.post(
        "/parse-receipt",
        data={"file": (io.BytesIO(b"fake image data"), "receipt.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "api_error"


def test_claude_returns_invalid_json_500(client, mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value.content[0].text = "NOT JSON"
    response = client.post(
        "/parse-receipt",
        data={"file": (io.BytesIO(b"fake image data"), "receipt.jpg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "parse_error"


def test_hello_world_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello World" in response.data


def test_parse_receipt_get_not_allowed(client):
    response = client.get("/parse-receipt")
    assert response.status_code == 405
