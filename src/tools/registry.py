"""
Tool registry for ReAct agent — 3 core e-commerce tools.
Each tool module owns its own data (PRODUCTS, COUPONS, SHIPPING_RATES).
"""

from src.tools.calc_shipping import calc_shipping
from src.tools.check_stock import check_stock
from src.tools.get_discount import get_discount

TOOL_SPECS = [
    {
        "name": "check_stock",
        "description": (
            "Look up inventory for a product by name. Returns stock count, "
            "unit_price_vnd (integer VND), and weight_kg per unit. "
            "Use before confirming an order. Example: item_name='iPhone'."
        ),
        "parameters": {"item_name": "string — product name, e.g. iPhone, MacBook"},
        "function": check_stock,
    },
    {
        "name": "get_discount",
        "description": (
            "Validate a coupon code and return discount_percent (0–100). "
            "Codes are case-insensitive. Returns an error string if invalid. "
            "Example: coupon_code='WINNER'."
        ),
        "parameters": {"coupon_code": "string — e.g. WINNER, NEWUSER"},
        "function": get_discount,
    },
    {
        "name": "calc_shipping",
        "description": (
            "Compute shipping fee in VND from total package weight and destination city. "
            "Supported cities: Hanoi, Ho Chi Minh (HCM), Da Nang; others use default rates. "
            "Example: weight_kg=0.7, destination='Hanoi'."
        ),
        "parameters": {
            "weight_kg": "float — total weight of all items in kg",
            "destination": "string — city name",
        },
        "function": calc_shipping,
    },
]
