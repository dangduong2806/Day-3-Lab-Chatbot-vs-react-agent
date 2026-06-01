"""Tool: check_stock — inventory lookup by product name."""

from typing import Any, Dict, Optional

# Catalog data for this tool only
PRODUCTS: Dict[str, Dict[str, Any]] = {
    "iphone": {
        "display_name": "iPhone 15",
        "unit_price_vnd": 25_990_000,
        "weight_kg": 0.35,
        "stock": 42,
    },
    "macbook": {
        "display_name": "MacBook Air M3",
        "unit_price_vnd": 28_990_000,
        "weight_kg": 1.24,
        "stock": 15,
    },
    "airpods": {
        "display_name": "AirPods Pro 2",
        "unit_price_vnd": 5_990_000,
        "weight_kg": 0.05,
        "stock": 120,
    },
}


def _normalize_item(item_name: str) -> str:
    return item_name.strip().lower().replace(" ", "")


def _find_product(item_name: str) -> Optional[Dict[str, Any]]:
    key = _normalize_item(item_name)
    if key in PRODUCTS:
        return PRODUCTS[key]
    for name, product in PRODUCTS.items():
        if name in key or key in name:
            return product
    return None


def check_stock(item_name: str) -> str:
    """
    Return available quantity and unit price for an item.
    Input: product name (e.g. 'iPhone', 'MacBook').
    """
    product = _find_product(item_name)
    if not product:
        available = ", ".join(p["display_name"] for p in PRODUCTS.values())
        return f"Error: Product '{item_name}' not found. Available: {available}"

    return (
        f"product={product['display_name']}; "
        f"stock={product['stock']}; "
        f"unit_price_vnd={product['unit_price_vnd']}; "
        f"weight_kg={product['weight_kg']}"
    )
