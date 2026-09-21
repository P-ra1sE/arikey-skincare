from django.contrib import admin

from .models import (
    Product,
    DeliveryLocation,
    Order,
    OrderItem,
)


# =========================================================
# PRODUCTS
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "price",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
    )


# =========================================================
# DELIVERY LOCATIONS
# =========================================================

@admin.register(DeliveryLocation)
class DeliveryLocationAdmin(admin.ModelAdmin):

    list_display = (
        "country",
        "state_region",
        "city_area",
        "landmark",
        "delivery_type",
        "fee",
        "is_active",
    )

    list_filter = (
        "country",
        "state_region",
        "delivery_type",
        "is_active",
    )

    search_fields = (
        "country",
        "state_region",
        "city_area",
        "landmark",
    )

    list_editable = (
        "fee",
        "is_active",
    )


# =========================================================
# ORDER ITEMS INLINE
# =========================================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        "product",
        "product_name",
        "unit_price",
        "quantity",
        "line_total",
    )


# =========================================================
# ORDERS
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "first_name",
        "last_name",
        "phone",
        "subtotal",
        "processing_fee",
        "total",
        "delivery_location",
        "delivery_fee",
        "product_payment_status",
        "delivery_payment_status",
        "order_method",
        "status",
        "created_at",
    )

    list_filter = (
        "product_payment_status",
        "delivery_payment_status",
        "order_method",
        "status",
        "delivery_location",
        "created_at",
    )

    search_fields = (
        "order_number",
        "reference",
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    readonly_fields = (
        "order_number",
        "reference",
        "subtotal",
        "processing_fee",
        "total",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "delivery_payment_status",
        "status",
    )

    inlines = [
        OrderItemInline
    ]


# =========================================================
# ORDER ITEMS
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "product_name",
        "order",
        "unit_price",
        "quantity",
        "line_total",
    )

    search_fields = (
        "product_name",
        "order__order_number",
    )