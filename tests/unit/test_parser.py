import json
from unittest.mock import MagicMock

import pytest

from scanning_app.parser import (
    NotAReceiptError,
    ReceiptParseError,
    get_extension,
    parse_receipt_image,
)
from scanning_app.config import CLAUDE_MODEL

SAMPLE_RECEIPT = {
    "metadata": {"store_name": "Test Mart"},
    "items": [{"name": "Apple"}],
    "item_count": 1,
}


def make_mock_client(text: str) -> MagicMock:
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=text)]
    mock_client.messages.create.return_value = mock_response
    return mock_client


# --- get_extension tests ---

def test_get_extension_jpg():
    assert get_extension("receipt.jpg") == "jpg"


def test_get_extension_jpeg_uppercase():
    assert get_extension("RECEIPT.JPEG") == "jpeg"


def test_get_extension_no_extension():
    assert get_extension("receipt") == ""


def test_get_extension_multiple_dots():
    assert get_extension("my.receipt.png") == "png"


# --- parse_receipt_image tests ---

def test_parse_receipt_image_success():
    client = make_mock_client(json.dumps(SAMPLE_RECEIPT))
    result = parse_receipt_image(b"fake bytes", "jpg", client)
    assert result == SAMPLE_RECEIPT


def test_parse_receipt_image_not_a_receipt_raises():
    client = make_mock_client(json.dumps({"error": "not_a_receipt"}))
    with pytest.raises(NotAReceiptError):
        parse_receipt_image(b"fake bytes", "jpg", client)


def test_parse_receipt_image_api_error_raises():
    client = MagicMock()
    client.messages.create.side_effect = Exception("API down")
    with pytest.raises(ReceiptParseError) as exc_info:
        parse_receipt_image(b"fake bytes", "jpg", client)
    assert exc_info.value.error_code == "api_error"
    assert exc_info.value.http_status == 500


def test_parse_receipt_image_bad_json_raises():
    client = make_mock_client("NOT VALID JSON")
    with pytest.raises(ReceiptParseError) as exc_info:
        parse_receipt_image(b"fake bytes", "jpg", client)
    assert exc_info.value.error_code == "parse_error"
    assert exc_info.value.http_status == 500


def test_parse_receipt_image_uses_correct_model():
    client = make_mock_client(json.dumps(SAMPLE_RECEIPT))
    parse_receipt_image(b"fake bytes", "jpg", client)
    call_kwargs = client.messages.create.call_args
    assert call_kwargs.kwargs["model"] == CLAUDE_MODEL


def test_parse_receipt_image_encodes_bytes_correctly():
    import base64
    image_bytes = b"test image content"
    expected_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    client = make_mock_client(json.dumps(SAMPLE_RECEIPT))
    parse_receipt_image(image_bytes, "jpg", client)
    call_kwargs = client.messages.create.call_args
    messages = call_kwargs.kwargs["messages"]
    image_block = messages[0]["content"][0]
    assert image_block["source"]["data"] == expected_b64


def test_parse_receipt_image_correct_mime_png():
    client = make_mock_client(json.dumps(SAMPLE_RECEIPT))
    parse_receipt_image(b"fake bytes", "png", client)
    call_kwargs = client.messages.create.call_args
    messages = call_kwargs.kwargs["messages"]
    image_block = messages[0]["content"][0]
    assert image_block["source"]["media_type"] == "image/png"


def test_parse_receipt_image_correct_mime_jpg():
    client = make_mock_client(json.dumps(SAMPLE_RECEIPT))
    parse_receipt_image(b"fake bytes", "jpg", client)
    call_kwargs = client.messages.create.call_args
    messages = call_kwargs.kwargs["messages"]
    image_block = messages[0]["content"][0]
    assert image_block["source"]["media_type"] == "image/jpeg"
