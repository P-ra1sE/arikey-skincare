import json
import uuid
import requests
import hashlib
import hmac

from decimal import Decimal
from urllib.parse import quote

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Product, Order, OrderItem


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
    return render(request, "checkout.html")


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
                "error": "Invalid request data."
            },
            status=400
        )


    # -----------------------------------------------------
    # VALIDATE CUSTOMER INFORMATION
    # -----------------------------------------------------

    required_fields = [
        "first_name",
        "last_name",
        "email",
        "address",
        "city",
        "state",
        "zip",
        "country",
    ]


    for field in required_fields:

        value = str(
            data.get(field, "")
        ).strip()

        if not value:

            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        field
                        .replace("_", " ")
                        .title()
                        + " is required."
                    )
                },
                status=400
            )


    # -----------------------------------------------------
    # ORDER METHOD
    # -----------------------------------------------------

    order_method = data.get(
        "order_method",
        "paystack"
    )


    if order_method not in [
        "paystack",
        "whatsapp"
    ]:

        return JsonResponse(
            {
                "success": False,
                "error": "Invalid order method."
            },
            status=400
        )


    # -----------------------------------------------------
    # CART ITEMS
    # -----------------------------------------------------

    items = data.get(
        "items",
        []
    )


    if not isinstance(items, list) or not items:

        return JsonResponse(
            {
                "success": False,
                "error": "Your shopping bag is empty."
            },
            status=400
        )


    checked_items = []

    subtotal = Decimal(
        "0.00"
    )


    # -----------------------------------------------------
    # VALIDATE PRODUCTS USING DJANGO DATABASE
    # -----------------------------------------------------

    for item in items:

        try:

            product_id = int(
                item.get("id")
            )

            quantity = int(
                item.get("quantity")
            )

        except (
            TypeError,
            ValueError
        ):

            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid product information."
                },
                status=400
            )


        # Quantity safety check

        if quantity < 1 or quantity > 10:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid product quantity."
                },
                status=400
            )


        # Get actual product from Django database

        try:

            product = Product.objects.get(
                id=product_id,
                is_active=True
            )

        except Product.DoesNotExist:

            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        f"Product {product_id} "
                        "is unavailable."
                    )
                },
                status=400
            )


        # Django calculates price.
        # We do NOT trust prices from JavaScript.

        subtotal += (
            product.price
            * quantity
        )


        checked_items.append(
            {
                "product": product,
                "quantity": quantity
            }
        )


    # -----------------------------------------------------
    # SHIPPING CALCULATION
    # -----------------------------------------------------

    if subtotal >= Decimal("30000.00"):

        shipping = Decimal(
            "0.00"
        )

    else:

        shipping = Decimal(
            "2500.00"
        )


    total = (
        subtotal
        + shipping
    )


    # -----------------------------------------------------
    # CREATE UNIQUE ORDER REFERENCE
    # -----------------------------------------------------

    reference = (
        "ARIKEY-"
        + uuid.uuid4()
        .hex[:12]
        .upper()
    )


    # -----------------------------------------------------
    # ORDER CHANNEL
    # -----------------------------------------------------

    if order_method == "whatsapp":

        order_channel = "whatsapp"

    else:

        order_channel = "website"


    # -----------------------------------------------------
    # CREATE ORDER AND ORDER ITEMS
    # -----------------------------------------------------

    with transaction.atomic():

        order = Order.objects.create(

            first_name=
                data["first_name"].strip(),

            last_name=
                data["last_name"].strip(),

            email=
                data["email"].strip(),

            address=
                data["address"].strip(),

            city=
                data["city"].strip(),

            state=
                data["state"].strip(),

            zip_code=
                data["zip"].strip(),

            country=
                data["country"].strip(),

            subtotal=
                subtotal,

            shipping=
                shipping,

            total=
                total,

            reference=
                reference,

            status=
                "pending",

            order_channel=
                order_channel,

            payment_method=
                order_method,
        )


        # Create products belonging to order

        for checked_item in checked_items:

            product = checked_item[
                "product"
            ]

            quantity = checked_item[
                "quantity"
            ]


            OrderItem.objects.create(

                order=
                    order,

                product=
                    product,

                product_name=
                    product.name,

                unit_price=
                    product.price,

                quantity=
                    quantity
            )


    # =====================================================
    # WHATSAPP ORDER
    # =====================================================

    if order_method == "whatsapp":

        message_lines = [

            "Hello Arikey Skincare,",

            "",

            "I would like to place this order:",

            "",

            f"Order Reference: {order.reference}",

            "",
        ]


        # Add products to WhatsApp message

        for checked_item in checked_items:

            product = checked_item[
                "product"
            ]

            quantity = checked_item[
                "quantity"
            ]


            message_lines.append(
                f"{product.name} x {quantity}"
            )


        # Add total and closing message

        message_lines.extend(
            [
                "",
                f"Total: ₦{order.total:,.0f}",
                "",
                "Please confirm my order. Thank you."
            ]
        )


        whatsapp_message = "\n".join(
            message_lines
        )


        # Get WhatsApp number from settings.py

        whatsapp_number = getattr(
            settings,
            "WHATSAPP_NUMBER",
            ""
        )


        whatsapp_url = ""


        if whatsapp_number:

            whatsapp_url = (
                "https://wa.me/"
                + whatsapp_number
                + "?text="
                + quote(
                    whatsapp_message
                )
            )


        # Send WhatsApp information back to frontend

        return JsonResponse(
            {
                "success": True,

                "order_method":
                    "whatsapp",

                "reference":
                    order.reference,

                "total":
                    float(order.total),

                "whatsapp_url":
                    whatsapp_url,

                "whatsapp_message":
                    whatsapp_message,
            }
        )


    # =====================================================
    # PAYSTACK ORDER
    # =====================================================

    # Check that Paystack secret key exists

    if not settings.PAYSTACK_SECRET_KEY:

        return JsonResponse(
            {
                "success": False,
                "error": "Paystack is not configured."
            },
            status=500
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
    }


    # -----------------------------------------------------
    # INITIALIZE PAYSTACK PAYMENT
    # -----------------------------------------------------

    try:

        paystack_response = requests.post(

            "https://api.paystack.co/transaction/initialize",

            headers={
                "Authorization":
                    f"Bearer {settings.PAYSTACK_SECRET_KEY}",

                "Content-Type":
                    "application/json",
            },

            json=
                paystack_data,

            timeout=
                30,
        )


        paystack_result = (
            paystack_response.json()
        )


    # -----------------------------------------------------
    # PAYSTACK CONNECTION ERROR
    # -----------------------------------------------------

    except requests.RequestException:

        return JsonResponse(
            {
                "success": False,

                "error": (
                    "Could not connect to Paystack. "
                    "Please try again."
                )
            },
            status=502
        )


    # -----------------------------------------------------
    # INVALID RESPONSE FROM PAYSTACK
    # -----------------------------------------------------

    except ValueError:

        return JsonResponse(
            {
                "success": False,

                "error": (
                    "Paystack returned "
                    "an invalid response."
                )
            },
            status=502
        )


    # -----------------------------------------------------
    # TEMPORARY TEST OUTPUT
    # -----------------------------------------------------

    print(
        "PAYSTACK RESPONSE:",
        paystack_result
    )


    # -----------------------------------------------------
    # PAYSTACK REJECTED PAYMENT INITIALIZATION
    # -----------------------------------------------------

    if (
        not paystack_response.ok
        or
        not paystack_result.get(
            "status"
        )
    ):

        return JsonResponse(
            {
                "success": False,

                "error":
                    paystack_result.get(
                        "message",
                        "Unable to start payment."
                    )
            },
            status=400
        )


    # -----------------------------------------------------
    # GET PAYSTACK PAYMENT URL
    # -----------------------------------------------------

    try:

        authorization_url = (
            paystack_result[
                "data"
            ][
                "authorization_url"
            ]
        )

    except (
        KeyError,
        TypeError
    ):

        return JsonResponse(
            {
                "success": False,

                "error": (
                    "Paystack did not return "
                    "a payment link."
                )
            },
            status=502
        )


    # -----------------------------------------------------
    # SEND PAYMENT LINK TO CHECKOUT PAGE
    # -----------------------------------------------------

    return JsonResponse(
        {
            "success": True,

            "order_method":
                "paystack",

            "reference":
                order.reference,

            "total":
                float(order.total),

            "authorization_url":
                authorization_url,
        }
    )


def payment_callback(request):

    reference = (
        request.GET.get("reference")
        or request.GET.get("trxref")
    )

    if not reference:
        return redirect("checkout")

    try:
        order = Order.objects.get(
            reference=reference
        )

    except Order.DoesNotExist:
        return redirect("checkout")


    # If already paid, don't verify again
    if order.status == "paid":
        return redirect(
            f"/order-success.html?reference={order.reference}"
        )


    if not settings.PAYSTACK_SECRET_KEY:
        return redirect("checkout")


    try:
        response = requests.get(
            (
                "https://api.paystack.co/"
                f"transaction/verify/{reference}"
            ),

            headers={
                "Authorization":
                    f"Bearer {settings.PAYSTACK_SECRET_KEY}"
            },

            timeout=30,
        )

        result = response.json()

    except (
        requests.RequestException,
        ValueError
    ):
        return redirect(
            "checkout"
        )


    if (
        not response.ok
        or not result.get("status")
    ):
        return redirect(
            "checkout"
        )


    payment = result.get(
        "data",
        {}
    )


    # ---------------------------------
    # VERIFY PAYMENT DETAILS
    # ---------------------------------

    expected_amount = int(
        order.total * 100
    )


    payment_successful = (
        payment.get("status") == "success"
        and payment.get("reference") == order.reference
        and payment.get("amount") == expected_amount
        and payment.get("currency") == "NGN"
    )


    if payment_successful:

        order.status = "paid"
        order.save()

        return redirect(
            f"/order-success.html"
            f"?reference={order.reference}"
        )


    return redirect(
        "/checkout.html?payment=failed"
    )


def order_success(request):

    reference = request.GET.get(
        "reference"
    )

    order = None

    if reference:

        try:
            order = Order.objects.get(
                reference=reference,
                status="paid"
            )

        except Order.DoesNotExist:
            order = None


    return render(
        request,
        "order-success.html",
        {
            "order": order
        }
    )
    
    # =========================================================
# PAYSTACK WEBHOOK
# =========================================================

@csrf_exempt
@require_POST
def paystack_webhook(request):

    secret_key = settings.PAYSTACK_SECRET_KEY

    if not secret_key:
        return HttpResponse(
            status=500
        )


    # -----------------------------------------------------
    # VERIFY PAYSTACK SIGNATURE
    # -----------------------------------------------------

    paystack_signature = request.headers.get(
        "x-paystack-signature",
        ""
    )

    calculated_signature = hmac.new(
        secret_key.encode("utf-8"),
        request.body,
        hashlib.sha512
    ).hexdigest()


    if not hmac.compare_digest(
        calculated_signature,
        paystack_signature
    ):
        return HttpResponse(
            status=400
        )


    # -----------------------------------------------------
    # READ EVENT
    # -----------------------------------------------------

    try:
        event = json.loads(
            request.body
        )

    except json.JSONDecodeError:
        return HttpResponse(
            status=400
        )


    # -----------------------------------------------------
    # SUCCESSFUL PAYMENT
    # -----------------------------------------------------

    if event.get("event") == "charge.success":

        payment = event.get(
            "data",
            {}
        )

        reference = payment.get(
            "reference"
        )


        if reference:

            try:
                order = Order.objects.get(
                    reference=reference,
                    payment_method="paystack"
                )

            except Order.DoesNotExist:

                # We still acknowledge the webhook
                # so Paystack does not keep retrying.
                return HttpResponse(
                    status=200
                )


            expected_amount = int(
                order.total * 100
            )


            payment_is_valid = (

                payment.get("status")
                == "success"

                and payment.get("reference")
                == order.reference

                and payment.get("amount")
                == expected_amount

                and payment.get("currency")
                == "NGN"
            )


            if (
                payment_is_valid
                and order.status != "paid"
            ):

                order.status = "paid"

                order.save()


    # Paystack expects 200 OK
    return HttpResponse(
        status=200
    )
