import os
from pathlib import Path

import pytest
from anthropic import Anthropic

RECEIPT_IMAGES = [
    ("tesco_1994.jpg", "tesco_1994"),
    ("supermarket_de.jpg", "supermarket_de"),
    ("walmart_us.jpg", "walmart_us"),
]

RECEIPTS_DIR = Path(__file__).parent / "receipts"
RESULTS_DIR = Path(__file__).parent / "results"


@pytest.fixture(scope="session")
def real_anthropic_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return Anthropic(api_key=api_key)


@pytest.fixture(scope="session")
def results_dir():
    RESULTS_DIR.mkdir(exist_ok=True)
    return RESULTS_DIR
