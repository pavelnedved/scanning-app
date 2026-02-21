import json
from pathlib import Path

import pytest

from scanning_app.parser import get_extension, parse_receipt_image
from tests.regression.conftest import RECEIPT_IMAGES, RECEIPTS_DIR


@pytest.mark.parametrize("filename,result_stem", RECEIPT_IMAGES)
def test_parse_real_receipt(filename, result_stem, real_anthropic_client, results_dir):
    receipt_path = RECEIPTS_DIR / filename
    if not receipt_path.exists():
        pytest.skip(f"Receipt image not found: {receipt_path}")

    image_bytes = receipt_path.read_bytes()
    ext = get_extension(filename)

    result = parse_receipt_image(image_bytes, ext, real_anthropic_client)

    # Structural assertions
    assert "metadata" in result, "Result must have 'metadata' key"
    assert "items" in result, "Result must have 'items' key"
    assert "item_count" in result, "Result must have 'item_count' key"
    assert isinstance(result["items"], list), "'items' must be a list"
    assert result["item_count"] == len(result["items"]), (
        f"item_count ({result['item_count']}) must equal len(items) ({len(result['items'])})"
    )

    # Save result for human review
    output_path = results_dir / f"{result_stem}.json"
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
