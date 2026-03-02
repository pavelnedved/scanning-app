import threading
import uuid
from datetime import datetime, timezone

_receipts: dict[str, dict] = {}
_lock = threading.Lock()


def save_receipt(receipt: dict) -> str:
    """Persist a receipt, injecting receipt_id and saved_at. Returns the new ID."""
    receipt_id = str(uuid.uuid4())
    saved_at = datetime.now(timezone.utc).isoformat()
    stored = {**receipt, "receipt_id": receipt_id, "saved_at": saved_at}
    with _lock:
        _receipts[receipt_id] = stored
    return receipt_id


def get_receipt(receipt_id: str) -> dict | None:
    """Return receipt by ID, or None if not found."""
    with _lock:
        return _receipts.get(receipt_id)


def get_all_receipts() -> list[dict]:
    """Return all receipts sorted by saved_at descending (newest first)."""
    with _lock:
        items = list(_receipts.values())
    return sorted(items, key=lambda r: r.get("saved_at", ""), reverse=True)
