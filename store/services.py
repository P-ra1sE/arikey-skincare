from decimal import (
    Decimal,
    ROUND_UP,
)

from .models import Product


PAYSTACK_PERCENT = Decimal("0.015")
PAYSTACK_FLAT = Decimal("100.00")
PAYSTACK_CAP = Decimal("2000.00")
PAYSTACK_FLAT_WAIVER = Decimal("2500.00")


def calculate_processing_fee(amount):

    amount = Decimal(amount)

    if amount < PAYSTACK_FLAT_WAIVER:
        flat_fee = Decimal("0.00")
    else:
        flat_fee = PAYSTACK_FLAT

    applicable_fee = (
        amount * PAYSTACK_PERCENT
        + flat_fee
    )

    # Fee has reached Paystack's ₦2,000 cap
    if applicable_fee >= PAYSTACK_CAP:

        final_amount = (
            amount
            + PAYSTACK_CAP
        )

    else:

        final_amount = (
            (
                amount
                + flat_fee
            )
            /
            (
                Decimal("1.00")
                - PAYSTACK_PERCENT
            )
        ) + Decimal("0.01")

    final_amount = final_amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_UP
    )

    fee = (
        final_amount
        - amount
    )

    return fee.quantize(
        Decimal("0.01"),
        rounding=ROUND_UP
    )


def calculate_cart(items):

    checked_items = []

    subtotal = Decimal("0.00")

    for item in items:

        product_id = int(
            item["id"]
        )

        quantity = int(
            item["quantity"]
        )

        if quantity < 1 or quantity > 10:
            raise ValueError(
                "Invalid product quantity."
            )

        product = Product.objects.get(
            id=product_id,
            is_active=True
        )

        subtotal += (
            product.price
            * quantity
        )

        checked_items.append({
            "product": product,
            "quantity": quantity,
        })

    processing_fee = (
        calculate_processing_fee(
            subtotal
        )
    )

    online_total = (
        subtotal
        + processing_fee
    )

    return {
        "items": checked_items,
        "subtotal": subtotal,
        "processing_fee": processing_fee,
        "online_total": online_total,
    }