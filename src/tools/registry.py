"""
Tool registry for ReAct agent — core e-commerce tools.
Each tool module owns its own data (PRODUCTS, COUPONS, SHIPPING_RATES).
"""

from src.tools.calculate_installment import calculate_installment
from src.tools.calc_shipping import calc_shipping
from src.tools.check_stock import check_stock
from src.tools.get_discount import get_discount
from src.tools.reserve_item import reserve_item
from src.tools.track_order import track_order

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
            "Example: weight=0.7, destination='Hanoi'."
        ),
        "parameters": {
            "weight": "float — total weight of all items in kg",
            "destination": "string — city name",
        },
        "function": calc_shipping,
    },
    {
        "name": "reserve_item",
        "description": (
            "Reserve a product for a customer after stock has been checked. "
            "Use only when the user explicitly asks to reserve or hold an item. "
            "Example: item_name='MacBook Air M3', quantity=1, customer_name='Nguyen Van A'."
        ),
        "parameters": {
            "item_name": "string — product name, e.g. iPhone, MacBook",
            "quantity": "integer — number of units to reserve",
            "customer_name": "string — customer name",
        },
        "function": reserve_item,
    },
    {
        "name": "track_order",
        "description": (
            "Look up current order status, location, and ETA by order ID. "
            "Example: order_id='ORD-1002'."
        ),
        "parameters": {"order_id": "string — order ID, e.g. ORD-1002"},
        "function": track_order,
    },
    {
        "name": "calculate_installment",
        "description": (
            "Calculate monthly installment payment in VND for supported terms. "
            "Supported months: 3, 6, 12. Example: amount_vnd=28990000, months=6."
        ),
        "parameters": {
            "amount_vnd": "integer — amount to finance in VND",
            "months": "integer — installment term, one of 3, 6, 12",
        },
        "function": calculate_installment,
    },
]
