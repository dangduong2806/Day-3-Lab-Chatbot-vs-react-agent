def get_discount(coupon_code: str):
    coupons = {
        "WINNER": 0.10,
        "VIP": 0.20,
    }

    code = coupon_code.strip().upper()
    discount = coupons.get(code, 0.0)

    return {
        "coupon_code": code,
        "discount": discount,
        "valid": code in coupons
    }