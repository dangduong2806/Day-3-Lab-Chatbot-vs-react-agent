"""Tool: calculate_installment - compute monthly installment payments."""

from __future__ import annotations

import math


SUPPORTED_MONTHS = {
    3: 0.00,
    6: 0.03,
    12: 0.06,
}


def calculate_installment(amount_vnd: int, months: int) -> str:
    """Calculate monthly payment in VND for supported installment terms."""
    try:
        amount = int(amount_vnd)
        term = int(months)
    except (TypeError, ValueError) as exc:
        raise ValueError("amount_vnd and months must be integers") from exc

    if amount <= 0:
        raise ValueError("amount_vnd must be greater than 0")

    if term not in SUPPORTED_MONTHS:
        supported = ", ".join(str(value) for value in sorted(SUPPORTED_MONTHS))
        return f"Error: Unsupported installment term '{months}'. Supported months: {supported}"

    interest_rate = SUPPORTED_MONTHS[term]
    interest_vnd = math.ceil(amount * interest_rate)
    total_vnd = amount + interest_vnd
    monthly_payment_vnd = math.ceil(total_vnd / term)

    return (
        f"amount_vnd={amount}; "
        f"months={term}; "
        f"interest_rate={interest_rate}; "
        f"interest_vnd={interest_vnd}; "
        f"total_vnd={total_vnd}; "
        f"monthly_payment_vnd={monthly_payment_vnd}"
    )
