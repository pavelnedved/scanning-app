import json
from unittest.mock import MagicMock

import pytest

import scanning_app.database as db
from scanning_app import create_app

SAMPLE_RECEIPT = {
    "metadata": {
        "store_name": "Test Mart",
        "store_address": "123 Main St",
        "date": "2024-01-15",
        "time": "14:30",
        "receipt_number": "001",
        "cashier": None,
        "payment_method": "CASH",
        "subtotal": 10.00,
        "tax": 0.80,
        "total": 10.80,
        "amount_tendered": 20.00,
        "change": 9.20,
        "currency": "USD",
    },
    "items": [
        {
            "name": "Apple",
            "quantity": 2,
            "unit": "each",
            "unit_price": 5.00,
            "total_price": 10.00,
            "category": "produce",
            "on_sale": False,
            "discount": None,
        }
    ],
    "item_count": 1,
}


@pytest.fixture
def mock_anthropic_client():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(SAMPLE_RECEIPT))]
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def app(mock_anthropic_client):
    return create_app({"TESTING": True, "ANTHROPIC_CLIENT": mock_anthropic_client})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_db():
    db._receipts.clear()
    yield
    db._receipts.clear()
