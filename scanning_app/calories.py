import copy

# Estimated kcal per single unit/serving for known categories
_CATEGORY_KCAL: dict[str, float] = {
    "produce": 60,
    "dairy": 150,
    "meat": 220,
    "poultry": 200,
    "seafood": 150,
    "bakery": 250,
    "beverages": 50,
    "snacks": 180,
    "frozen": 280,
    "canned": 150,
    "condiments": 60,
    "deli": 250,
    "grains": 200,
    "cereal": 200,
    "spices": 10,
    "oils": 120,
    "baking": 200,
    "candy": 200,
    "desserts": 300,
}

# Estimated kcal per single unit for specific keywords found in item names
_KEYWORD_KCAL: dict[str, float] = {
    "milk": 150,
    "cheese": 110,
    "butter": 100,
    "yogurt": 100,
    "cream": 200,
    "egg": 70,
    "eggs": 70,
    "bread": 250,
    "bagel": 270,
    "muffin": 340,
    "croissant": 230,
    "apple": 95,
    "banana": 105,
    "orange": 65,
    "grape": 60,
    "strawberry": 45,
    "blueberry": 45,
    "avocado": 230,
    "potato": 160,
    "tomato": 35,
    "onion": 45,
    "carrot": 50,
    "broccoli": 55,
    "spinach": 20,
    "lettuce": 15,
    "chicken": 200,
    "beef": 250,
    "pork": 240,
    "turkey": 180,
    "salmon": 180,
    "tuna": 130,
    "shrimp": 85,
    "rice": 200,
    "pasta": 200,
    "noodle": 200,
    "cereal": 200,
    "oat": 150,
    "granola": 200,
    "chips": 150,
    "cracker": 140,
    "cookie": 150,
    "chocolate": 550,
    "candy": 200,
    "ice cream": 250,
    "juice": 110,
    "soda": 150,
    "water": 0,
    "coffee": 5,
    "tea": 5,
    "beer": 150,
    "wine": 125,
    "soup": 150,
    "sauce": 80,
    "salsa": 20,
    "oil": 120,
    "sugar": 50,
    "flour": 100,
    "honey": 60,
    "jam": 55,
    "peanut butter": 190,
    "almond": 160,
    "walnut": 180,
    "protein bar": 200,
    "energy bar": 200,
}


def _estimate_kcal_per_unit(name: str | None, category: str | None) -> float | None:
    """Return estimated kcal for one unit of the item, or None if unknown."""
    name_lower = (name or "").lower()
    category_lower = (category or "").lower()

    # First try multi-word keyword matches (longer phrases first)
    for keyword in sorted(_KEYWORD_KCAL, key=len, reverse=True):
        if keyword in name_lower:
            return _KEYWORD_KCAL[keyword]

    # Fall back to category lookup
    if category_lower in _CATEGORY_KCAL:
        return _CATEGORY_KCAL[category_lower]

    return None


def add_calorie_estimates(receipt: dict) -> dict:
    """Return a copy of receipt with estimated_calories_kcal added to each item
    and total_estimated_calories_kcal added at the top level."""
    result = copy.deepcopy(receipt)
    total = 0.0
    has_any = False

    for item in result.get("items", []):
        name = item.get("name")
        category = item.get("category")
        quantity = item.get("quantity") or 1

        per_unit = _estimate_kcal_per_unit(name, category)
        if per_unit is not None:
            item_kcal = round(per_unit * quantity, 1)
            item["estimated_calories_kcal"] = item_kcal
            total += item_kcal
            has_any = True
        else:
            item["estimated_calories_kcal"] = None

    result["total_estimated_calories_kcal"] = round(total, 1) if has_any else None
    return result
