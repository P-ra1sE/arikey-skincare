from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'price',
        'is_active'
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'is_active',
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'product_name',
        'unit_price',
        'quantity',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'reference',
        'first_name',
        'last_name',
        'email',
        'order_channel',
        'payment_method',
        'total',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'order_channel',
        'payment_method',
        'created_at',
    )

    search_fields = (
        'reference',
        'first_name',
        'last_name',
        'email',
    )

    inlines = [
        OrderItemInline
    ]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'product_name',
        'order',
        'unit_price',
        'quantity',
    )

# Register your models here.
