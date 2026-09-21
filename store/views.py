import hashlib
import hmac
import json
import uuid
from decimal import Decimal
from urllib.parse import quote

import requests

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import CheckoutForm
from .models import DeliveryLocation, Order, OrderItem, Product
from .services import calculate_cart


# =========================================================
# PAGE VIEWS
# =========================================================

def home(request):
    return render(request, "home.html")


def shop(request):
    return render(request, "shopnow.html")


def our_story(request):
    return render(request, "ourstory.html")


def contact(request):
    return render(request, "contactus.html")


def product_details(request):
    return render(request, "product-details.html")


def cart(request):
    return render(request, "cart.html")


def checkout(request):
    countries = (
        DeliveryLocation.objects
        .filter(is_active=True)
        .values_list("country", flat=True)
        .distinct()
        .order_by("country")
    )

    return render(
        request,
        "checkout.html",
        {
            "delivery_countries": countries,
        },
    )


# =========================================================
# DELIVERY LOCATION APIS
# =========================================================

def delivery_countries(request):
    countries = (
        DeliveryLocation.objects
        .filter(is_active=True)
        .values_list("country", flat=True)
        .distinct()
        .order_by("country")
    )

    return JsonResponse({
        "success": True,
        "countries": list(countries),
    })


def delivery_states(request):
    country = request.GET.get("country", "").strip()

    if not country:
        return JsonResponse({
            "success": True,
            "states": [],
        })

    states = (
        DeliveryLocation.objects
        .filter(
            country__iexact=country,
            is_active=True,
        )
        .values_list("state_region", flat=True)
        .distinct()
        .order_by("state_region")
    )

    return JsonResponse({
        "success": True,
        "states": list(states),
    })


def delivery_locations(request):
    country = request.GET.get("country", "").strip()
    state = request.GET.get("state", "").strip()
    search = request.GET.get("q", "").strip()

    if not country or not state:
        return JsonResponse({
            "success": True,
            "locations": [],
        })

    locations = DeliveryLocation.objects.filter(
        country__iexact=country,
        state_region__iexact=state,
        is_active=True,
    )

    if search:
        locations = locations.filter(
            Q(city_area__icontains=search)
            | Q(landmark__icontains=search)
        )

    locations = locations.order_by(
        "city_area",
        "landmark",
    )[:40]

    data = []

    for location in locations:
        if (
            location.delivery_type == "fixed"
            and location.fee is not None
        ):
            fee = float(location.fee)
            fee_message = f"₦{location.fee:,.0f} — Pay on delivery"
        else:
            fee = None
            fee_message = "Delivery fee to be confirmed on WhatsApp"

        label = f"{location.city_area}, {location.state_region}"

        if location.landmark:
            label += f" — {location.landmark}"

        data.append({
            "id": location.id,
            "country": location.country,
            "state_region": location.state_region,
            "city_area": location.city_area,
            "landmark": location.landmark,
            "label": label,
            "delivery_type": location.delivery_type,
            "fee": fee,
            "fee_message": fee_message,
        })

    return JsonResponse({
        "success": True,
        "locations": data,
    })


# =========================================================
# CHECKOUT QUOTE
# =========================================================

@require_POST
def checkout_quote(request):
    try:
        data = json.loads(request.body)

        items = data.get("items", [])
        location_id = data.get("delivery_location")

        delivery_location = DeliveryLocation.objects.get(
            id=location_id,
            is_active=True,
        )

        if (
            delivery_location.delivery_type == "fixed"
            and delivery_location.fee is None
        ):
            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        "The delivery fee for this location "
                        "has not been configured yet."
                    ),
                },
                status=400,
            )

        quote_data = calculate_cart(items)

    except (
        ValueError,
        KeyError,
        Product.DoesNotExist,
        DeliveryLocation.DoesNotExist,
        TypeError,
        json.JSONDecodeError,
    ):
        return JsonResponse(
            {
                "success": False,
                "error": "Unable to calculate order.",
            },
            status=400,
        )

    if delivery_location.delivery_type == "fixed":
        delivery_fee = float(delivery_location.fee)
        delivery_message = "Pay on delivery"
    else:
        delivery_fee = None
        delivery_message = "Delivery fee to be confirmed on WhatsApp"

    return JsonResponse(
        {
            "success": True,
            "subtotal": float(quote_data["subtotal"]),
            "processing_fee": float(quote_data["processing_fee"]),
            "online_total": float(quote_data["online_total"]),
            "delivery_location": delivery_location.id,
            "delivery_type": delivery_location.delivery_type,
            "delivery_fee": delivery_fee,
            "delivery_message": delivery_message,
        }
    )


# =========================================================
# CREATE ORDER
# =========================================================

@require_POST
def create_order(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid checkout data.",
            },
            status=400,
        )

    form = CheckoutForm(data)

    if not form.is_valid():
        return JsonResponse(
            {
                "success": False,
                "errors": form.errors.get_json_data(),
            },
            status=400,
        )

    order_method = data.get("order_method", "paystack")

    if order_method not in ("paystack", "whatsapp"):
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid order method.",
            },
            status=400,
        )

    items = data.get("items", [])

    if not isinstance(items, list) or not items:
        return JsonResponse(
            {
                "success": False,
                "error": "Your shopping bag is empty.",
            },
            status=400,
        )

    try:
        cart_data = calculate_cart(items)
    except (
        ValueError,
        Product.DoesNotExist,
        KeyError,
        TypeError,
    ):
        return JsonResponse(
            {
                "success": False,
                "error": "One or more products in your bag are invalid.",
            },
            status=400,
        )

    delivery_location = form.cleaned_data["delivery_location"]

    if (
        delivery_location.delivery_type == "fixed"
        and delivery_location.fee is None
    ):
        return JsonResponse(
            {
                "success": False,
                "error": (
                    "The delivery fee for this location "
                    "has not been configured yet."
                ),
            },
            status=400,
        )

    order_number = "ARIKEY-" + uuid.uuid4().hex[:10].upper()

    if order_method == "paystack":
        reference = "PAY-" + uuid.uuid4().hex[:16].upper()
    else:
        reference = "WA-" + uuid.uuid4().hex[:16].upper()

    subtotal = cart_data["subtotal"]

    if delivery_location.delivery_type == "fixed":
        delivery_fee = delivery_location.fee
    else:
        delivery_fee = Decimal("0.00")

    if order_method == "paystack":
        processing_fee = cart_data["processing_fee"]
        total = cart_data["online_total"]
    else:
        processing_fee = Decimal("0.00")
        total = subtotal

    with transaction.atomic():
        order = Order.objects.create(
            order_number=order_number,
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"],
            phone=form.cleaned_data["phone"],
            address=form.cleaned_data["address"],
            city=form.cleaned_data["city"],
            state=form.cleaned_data["state"],
            zip_code=form.cleaned_data["zip"],
            country=form.cleaned_data["country"],
            delivery_location=delivery_location,
            delivery_fee=delivery_fee,
            subtotal=subtotal,
            processing_fee=processing_fee,
            total=total,
            reference=reference,
            product_payment_status="pending",
            delivery_payment_status="pending",
            delivery_payment_method="pay_on_delivery",
            order_method=order_method,
            status="pending",
        )

        for item in cart_data["items"]:
            product = item["product"]
            quantity = item["quantity"]

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                unit_price=product.price,
                quantity=quantity,
            )

    # -----------------------------------------------------
    # ORDER VIA WHATSAPP
    # -----------------------------------------------------

    if order_method == "whatsapp":
        whatsapp_number = getattr(
            settings,
            "WHATSAPP_NUMBER",
            "",
        ).strip()

        if not whatsapp_number:
            return JsonResponse(
                {
                    "success": False,
                    "error": "WhatsApp ordering is not configured.",
                },
                status=500,
            )

        product_lines = []

        for item in order.items.all():
            product_lines.append(
                f"{item.product_name} x {item.quantity} "
                f"- ₦{item.line_total:,.0f}"
            )

        products_text = "\n".join(product_lines)

        delivery_location_text = (
            f"{delivery_location.city_area}, "
            f"{delivery_location.state_region}, "
            f"{delivery_location.country}"
        )

        if delivery_location.landmark:
            delivery_location_text += (
                f" — {delivery_location.landmark}"
            )

        if delivery_location.delivery_type == "fixed":
            delivery_fee_text = (
                f"₦{order.delivery_fee:,.0f} "
                "(Pay on Delivery)"
            )
        else:
            delivery_fee_text = (
                "To be confirmed with seller on WhatsApp"
            )

        whatsapp_message = f"""
Hello Arikey Skincare,

I would like to place an order.

ORDER DETAILS

Order Number: {order.order_number}

Customer:
{order.first_name} {order.last_name}

Phone:
{order.phone}

Email:
{order.email}

Address:
{order.address}

City:
{order.city}

State:
{order.state}

Country:
{order.country}

DELIVERY

Selected Delivery Location:
{delivery_location_text}

Delivery Fee:
{delivery_fee_text}

Delivery Payment:
PENDING — Pay on Delivery

PRODUCTS

{products_text}

Product Subtotal:
₦{order.subtotal:,.0f}

Product Payment:
PENDING

Please confirm my order and payment details.
""".strip()

        whatsapp_url = (
            "https://wa.me/"
            + whatsapp_number
            + "?text="
            + quote(whatsapp_message)
        )

        return JsonResponse(
            {
                "success": True,
                "order_method": "whatsapp",
                "order_number": order.order_number,
                "whatsapp_url": whatsapp_url,
            }
        )

    # -----------------------------------------------------
    # PAYSTACK
    # -----------------------------------------------------

    paystack_secret_key = getattr(
        settings,
        "PAYSTACK_SECRET_KEY",
        "",
    ).strip()

    if not paystack_secret_key:
        return JsonResponse(
            {
                "success": False,
                "error": "Paystack is not configured.",
            },
            status=500,
        )

    callback_url = request.build_absolute_uri(
        reverse("payment-callback")
    )

    paystack_data = {
        "email": order.email,
        "amount": int(order.total * 100),
        "reference": order.reference,
        "currency": "NGN",
        "callback_url": callback_url,
        "metadata": json.dumps(
            {
                "order_number": order.order_number,
                "phone": order.phone,
                "delivery_location_id": delivery_location.id,
            }
        ),
    }

    try:
        paystack_response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            headers={
                "Authorization": f"Bearer {paystack_secret_key}",
                "Content-Type": "application/json",
            },
            json=paystack_data,
            timeout=30,
        )

        paystack_result = paystack_response.json()

    except (requests.RequestException, ValueError):
        return JsonResponse(
            {
                "success": False,
                "error": "Unable to connect to Paystack.",
            },
            status=502,
        )

    if not paystack_response.ok or not paystack_result.get("status"):
        return JsonResponse(
            {
                "success": False,
                "error": paystack_result.get(
                    "message",
                    "Unable to start payment.",
                ),
            },
            status=400,
        )

    try:
        authorization_url = paystack_result["data"]["authorization_url"]
    except (KeyError, TypeError):
        return JsonResponse(
            {
                "success": False,
                "error": "Paystack did not return a payment link.",
            },
            status=502,
        )

    return JsonResponse(
        {
            "success": True,
            "order_method": "paystack",
            "order_number": order.order_number,
            "reference": order.reference,
            "authorization_url": authorization_url,
        }
    )


# =========================================================
# PAYSTACK CALLBACK
# =========================================================

def payment_callback(request):
    reference = request.GET.get("reference")

    if not reference:
        return redirect("checkout")

    try:
        order = Order.objects.get(
            reference=reference,
            order_method="paystack",
        )
    except Order.DoesNotExist:
        return redirect("checkout")

    if order.product_payment_status == "paid":
        return redirect(
            reverse("order-success")
            + "?order="
            + order.order_number
        )

    paystack_secret_key = getattr(
        settings,
        "PAYSTACK_SECRET_KEY",
        "",
    ).strip()

    if not paystack_secret_key:
        return redirect("checkout")

    try:
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers={
                "Authorization": f"Bearer {paystack_secret_key}",
            },
            timeout=30,
        )

        result = response.json()

    except (requests.RequestException, ValueError):
        return redirect("checkout")

    payment = result.get("data", {})
    expected_amount = int(order.total * 100)

    payment_is_valid = (
        response.ok
        and result.get("status")
        and payment.get("status") == "success"
        and payment.get("reference") == order.reference
        and payment.get("amount") == expected_amount
        and payment.get("currency") == "NGN"
    )

    if payment_is_valid:
        order.product_payment_status = "paid"
        order.delivery_payment_status = "pending"
        order.status = "confirmed"

        order.save(
            update_fields=[
                "product_payment_status",
                "delivery_payment_status",
                "status",
            ]
        )

        return redirect(
            reverse("order-success")
            + "?order="
            + order.order_number
        )

    order.product_payment_status = "failed"
    order.save(
        update_fields=[
            "product_payment_status",
        ]
    )

    return redirect(
        reverse("checkout")
        + "?payment=failed"
    )


# =========================================================
# ORDER SUCCESS PAGE
# =========================================================

def order_success(request):
    order_number = request.GET.get("order")

    if not order_number:
        return redirect("home-page")

    try:
        order = (
            Order.objects
            .prefetch_related("items")
            .select_related("delivery_location")
            .get(
                order_number=order_number,
                product_payment_status="paid",
                order_method="paystack",
            )
        )
    except Order.DoesNotExist:
        return redirect("home-page")

    item_lines = []

    for item in order.items.all():
        item_lines.append(
            f"{item.product_name} x {item.quantity} "
            f"- ₦{item.line_total:,.0f}"
        )

    products_text = "\n".join(item_lines)

    if order.delivery_location:
        delivery_location_text = (
            f"{order.delivery_location.city_area}, "
            f"{order.delivery_location.state_region}, "
            f"{order.delivery_location.country}"
        )

        if order.delivery_location.landmark:
            delivery_location_text += (
                f" — {order.delivery_location.landmark}"
            )

        if order.delivery_location.delivery_type == "fixed":
            delivery_fee_text = (
                f"₦{order.delivery_fee:,.0f} "
                "(Pay on Delivery)"
            )
        else:
            delivery_fee_text = (
                "To be confirmed with seller on WhatsApp"
            )
    else:
        delivery_location_text = "Not selected"
        delivery_fee_text = "To be confirmed"

    message = f"""
Hello Arikey Skincare,

I just placed and paid for an order on your website.

ORDER DETAILS

Order Number: {order.order_number}

Customer:
{order.first_name} {order.last_name}

Phone:
{order.phone}

Email:
{order.email}

Address:
{order.address}

City:
{order.city}

State:
{order.state}

Country:
{order.country}

DELIVERY

Selected Delivery Location:
{delivery_location_text}

Delivery Fee:
{delivery_fee_text}

Delivery Payment:
PENDING — Pay on Delivery

PRODUCTS

{products_text}

PAYMENT

Product Subtotal:
₦{order.subtotal:,.0f}

Payment Processing Fee:
₦{order.processing_fee:,.0f}

Amount Paid Online:
₦{order.total:,.0f}

Product Payment:
PAID

I would like to arrange delivery.
""".strip()

    whatsapp_number = getattr(
        settings,
        "WHATSAPP_NUMBER",
        "",
    ).strip()

    whatsapp_url = ""

    if whatsapp_number:
        whatsapp_url = (
            "https://wa.me/"
            + whatsapp_number
            + "?text="
            + quote(message)
        )

    return render(
        request,
        "order-success.html",
        {
            "order": order,
            "whatsapp_url": whatsapp_url,
        },
    )


# =========================================================
# PAYSTACK WEBHOOK
# =========================================================

@csrf_exempt
@require_POST
def paystack_webhook(request):
    secret_key = getattr(
        settings,
        "PAYSTACK_SECRET_KEY",
        "",
    ).strip()

    if not secret_key:
        return HttpResponse(status=500)

    paystack_signature = request.headers.get(
        "x-paystack-signature",
        "",
    )

    calculated_signature = hmac.new(
        secret_key.encode("utf-8"),
        request.body,
        hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(
        calculated_signature,
        paystack_signature,
    ):
        return HttpResponse(status=400)

    try:
        event = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    if event.get("event") == "charge.success":
        payment = event.get("data", {})
        reference = payment.get("reference")

        if reference:
            try:
                order = Order.objects.get(
                    reference=reference,
                    order_method="paystack",
                )
            except Order.DoesNotExist:
                return HttpResponse(status=200)

            expected_amount = int(
                order.total * 100
            )

            payment_is_valid = (
                payment.get("status") == "success"
                and payment.get("reference") == order.reference
                and payment.get("amount") == expected_amount
                and payment.get("currency") == "NGN"
            )

            if (
                payment_is_valid
                and order.product_payment_status != "paid"
            ):
                order.product_payment_status = "paid"
                order.delivery_payment_status = "pending"
                order.status = "confirmed"

                order.save(
                    update_fields=[
                        "product_payment_status",
                        "delivery_payment_status",
                        "status",
                    ]
                )

    return HttpResponse(status=200)
