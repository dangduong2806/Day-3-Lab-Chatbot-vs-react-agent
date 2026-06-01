"""Tool: reserve_item - reserve inventory for a customer."""

from __future__ import annotations

from typing import Dict, Any

from src.tools.check_stock import _find_product


RESERVATIONS: Dict[str, Dict[str, Any]] = {}


def reserve_item(item_name: str, quantity: int, customer_name: str) -> str:
    """Reserve an item for a customer if enough stock is available."""
    product = _find_product(item_name)
    if not product:
        return f"Error: Product '{item_name}' not found."

    try:
        requested_quantity = int(quantity)
    except (TypeError, ValueError) as exc:
        raise ValueError("quantity must be an integer") from exc

    if requested_quantity <= 0:
        raise ValueError("quantity must be greater than 0")

    if not isinstance(customer_name, str) or not customer_name.strip():
        raise ValueError("customer_name must be a non-empty string")

    if requested_quantity > int(product["stock"]):
        return (
            f"Error: Not enough stock for {product['display_name']}. "
            f"requested={requested_quantity}; available={product['stock']}"
        )

    reservation_id = f"RSV-{len(RESERVATIONS) + 1001}"
    RESERVATIONS[reservation_id] = {
        "item_name": product["display_name"],
        "quantity": requested_quantity,
        "customer_name": customer_name.strip(),
    }

    return (
        f"reservation_id={reservation_id}; "
        f"status=reserved; "
        f"product={product['display_name']}; "
        f"quantity={requested_quantity}; "
        f"customer_name={customer_name.strip()}"
    )
