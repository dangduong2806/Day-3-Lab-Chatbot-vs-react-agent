"""Tool: track_order - look up order status by order id."""

from __future__ import annotations

from typing import Dict


ORDERS: Dict[str, Dict[str, str]] = {
    "ORD-1001": {
        "status": "delivered",
        "location": "Ho Chi Minh City",
        "eta": "completed",
    },
    "ORD-1002": {
        "status": "in_transit",
        "location": "Da Nang sorting center",
        "eta": "2026-06-03",
    },
    "ORD-1003": {
        "status": "processing",
        "location": "Hanoi warehouse",
        "eta": "2026-06-04",
    },
}


def track_order(order_id: str) -> str:
    """Return the current status, location, and ETA for an order."""
    if not isinstance(order_id, str) or not order_id.strip():
        raise ValueError("order_id must be a non-empty string")

    normalized_order_id = order_id.strip().upper()
    order = ORDERS.get(normalized_order_id)
    if not order:
        available = ", ".join(sorted(ORDERS))
        return f"Error: Order '{order_id}' not found. Available demo orders: {available}"

    return (
        f"order_id={normalized_order_id}; "
        f"status={order['status']}; "
        f"location={order['location']}; "
        f"eta={order['eta']}"
    )
