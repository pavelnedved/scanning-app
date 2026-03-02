import pytest

from scanning_app.calories import add_calorie_estimates


def _make_receipt(items):
    return {
        "metadata": {"store_name": "Test Mart", "total": 10.0},
        "items": items,
        "item_count": len(items),
    }


def test_known_category_produce():
    receipt = _make_receipt([
        {"name": "Mystery Vegetable", "quantity": 1, "category": "produce"},
    ])
    result = add_calorie_estimates(receipt)
    assert result["items"][0]["estimated_calories_kcal"] is not None
    assert result["items"][0]["estimated_calories_kcal"] > 0


def test_known_keyword_apple():
    receipt = _make_receipt([
        {"name": "Gala Apple", "quantity": 1, "category": "produce"},
    ])
    result = add_calorie_estimates(receipt)
    # Apple keyword match should be more specific than category
    kcal = result["items"][0]["estimated_calories_kcal"]
    assert kcal == 95.0


def test_unknown_item_returns_none():
    receipt = _make_receipt([
        {"name": "Widget 5000", "quantity": 1, "category": "household"},
    ])
    result = add_calorie_estimates(receipt)
    assert result["items"][0]["estimated_calories_kcal"] is None


def test_unknown_total_is_none_when_all_items_unknown():
    receipt = _make_receipt([
        {"name": "Bleach", "quantity": 1, "category": "cleaning"},
    ])
    result = add_calorie_estimates(receipt)
    assert result["total_estimated_calories_kcal"] is None


def test_quantity_scaling():
    receipt = _make_receipt([
        {"name": "Banana", "quantity": 3, "category": "produce"},
    ])
    result = add_calorie_estimates(receipt)
    single = add_calorie_estimates(_make_receipt([
        {"name": "Banana", "quantity": 1, "category": "produce"},
    ]))
    assert result["items"][0]["estimated_calories_kcal"] == pytest.approx(
        single["items"][0]["estimated_calories_kcal"] * 3
    )


def test_total_estimated_calories_sums_items():
    receipt = _make_receipt([
        {"name": "Apple", "quantity": 1, "category": "produce"},
        {"name": "Banana", "quantity": 1, "category": "produce"},
    ])
    result = add_calorie_estimates(receipt)
    expected = (
        result["items"][0]["estimated_calories_kcal"]
        + result["items"][1]["estimated_calories_kcal"]
    )
    assert result["total_estimated_calories_kcal"] == pytest.approx(expected)


def test_null_name_falls_back_to_category():
    receipt = _make_receipt([
        {"name": None, "quantity": 1, "category": "dairy"},
    ])
    result = add_calorie_estimates(receipt)
    assert result["items"][0]["estimated_calories_kcal"] is not None


def test_null_category_falls_back_to_keyword():
    receipt = _make_receipt([
        {"name": "Whole Milk", "quantity": 1, "category": None},
    ])
    result = add_calorie_estimates(receipt)
    assert result["items"][0]["estimated_calories_kcal"] == 150.0


def test_original_receipt_not_mutated():
    receipt = _make_receipt([
        {"name": "Apple", "quantity": 1, "category": "produce"},
    ])
    original_item = receipt["items"][0].copy()
    add_calorie_estimates(receipt)
    assert receipt["items"][0] == original_item


def test_empty_items_list():
    receipt = _make_receipt([])
    result = add_calorie_estimates(receipt)
    assert result["total_estimated_calories_kcal"] is None
    assert result["items"] == []


def test_mixed_known_and_unknown_items():
    receipt = _make_receipt([
        {"name": "Apple", "quantity": 1, "category": "produce"},
        {"name": "Sponge", "quantity": 1, "category": "household"},
    ])
    result = add_calorie_estimates(receipt)
    assert result["items"][0]["estimated_calories_kcal"] == 95.0
    assert result["items"][1]["estimated_calories_kcal"] is None
    # Total should count only the known item
    assert result["total_estimated_calories_kcal"] == 95.0
