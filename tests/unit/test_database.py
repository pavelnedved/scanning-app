import time

import pytest

import scanning_app.database as db


@pytest.fixture(autouse=True)
def reset_db():
    db._receipts.clear()
    yield
    db._receipts.clear()


SAMPLE = {
    "metadata": {"store_name": "Test Mart", "total": 10.0},
    "items": [],
    "item_count": 0,
}


def test_save_receipt_returns_string_id():
    receipt_id = db.save_receipt(SAMPLE.copy())
    assert isinstance(receipt_id, str)
    assert len(receipt_id) > 0


def test_save_receipt_injects_receipt_id():
    receipt_id = db.save_receipt(SAMPLE.copy())
    stored = db.get_receipt(receipt_id)
    assert stored["receipt_id"] == receipt_id


def test_save_receipt_injects_saved_at():
    receipt_id = db.save_receipt(SAMPLE.copy())
    stored = db.get_receipt(receipt_id)
    assert "saved_at" in stored
    assert stored["saved_at"]  # not empty


def test_get_receipt_returns_stored_data():
    receipt_id = db.save_receipt({"metadata": {"store_name": "My Store"}, "items": [], "item_count": 0})
    stored = db.get_receipt(receipt_id)
    assert stored["metadata"]["store_name"] == "My Store"


def test_get_receipt_unknown_id_returns_none():
    result = db.get_receipt("00000000-0000-0000-0000-000000000000")
    assert result is None


def test_get_all_receipts_empty():
    assert db.get_all_receipts() == []


def test_get_all_receipts_returns_all():
    id1 = db.save_receipt(SAMPLE.copy())
    id2 = db.save_receipt(SAMPLE.copy())
    all_receipts = db.get_all_receipts()
    ids = [r["receipt_id"] for r in all_receipts]
    assert id1 in ids
    assert id2 in ids


def test_get_all_receipts_sorted_newest_first():
    id1 = db.save_receipt(SAMPLE.copy())
    time.sleep(0.01)  # ensure distinct timestamps
    id2 = db.save_receipt(SAMPLE.copy())
    all_receipts = db.get_all_receipts()
    # Most recent (id2) should be first
    assert all_receipts[0]["receipt_id"] == id2
    assert all_receipts[1]["receipt_id"] == id1


def test_save_does_not_mutate_original():
    original = SAMPLE.copy()
    db.save_receipt(original)
    assert "receipt_id" not in original
    assert "saved_at" not in original
