from __future__ import annotations


DESTINATION_RATES = {
    "hanoi": {"base": 20_000, "per_kg": 8_000},
    "ha noi": {"base": 20_000, "per_kg": 8_000},
    "ho chi minh": {"base": 25_000, "per_kg": 10_000},
    "hcmc": {"base": 25_000, "per_kg": 10_000},
    "danang": {"base": 22_000, "per_kg": 9_000},
    "da nang": {"base": 22_000, "per_kg": 9_000},
}

DEFAULT_RATE = {"base": 35_000, "per_kg": 12_000}


def calc_shipping(weight: float, destination: str) -> int:
    """Calculate shipping cost in VND from package weight and destination."""
    try:
        package_weight = float(weight)
    except (TypeError, ValueError) as exc:
        raise ValueError("weight must be a number in kilograms") from exc

    if package_weight <= 0:
        raise ValueError("weight must be greater than 0")

    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("destination must be a non-empty string")

    normalized_destination = destination.strip().lower()
    rate = DESTINATION_RATES.get(normalized_destination, DEFAULT_RATE)

    return int(rate["base"] + package_weight * rate["per_kg"])
