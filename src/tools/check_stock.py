"""Tool: check_stock — inventory lookup by product name."""

from src.tools.common import list_product_names, resolve_product


def check_stock(item_name: str) -> str:
    """
    Return available quantity and unit price for an item.
    Input: product name (e.g. 'iPhone', 'MacBook').
    """
    product = resolve_product(item_name)
    if not product:
        return (
            f"Error: Product '{item_name}' not found. "
            f"Available: {list_product_names()}"
        )

    return (
        f"product={product['display_name']}; "
        f"stock={product['stock']}; "
        f"unit_price_vnd={product['unit_price_vnd']}; "
        f"weight_kg={product['weight_kg']}"
    )
