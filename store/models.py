from django.db import models


class Product(models.Model):
    id = models.PositiveIntegerField(primary_key=True)

    name = models.CharField(max_length=200)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    image = models.CharField(
        max_length=255,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name

class DeliveryLocation(models.Model):

    DELIVERY_TYPE_CHOICES = [
        ("fixed", "Fixed Delivery Fee"),
        ("quote", "Delivery Fee To Be Confirmed"),
    ]

    country = models.CharField(
        max_length=100
    )

    state_region = models.CharField(
        max_length=120
    )

    city_area = models.CharField(
        max_length=150
    )

    landmark = models.CharField(
        max_length=180,
        blank=True
    )

    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_TYPE_CHOICES,
        default="fixed"
    )

    fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):

        location = (
            f"{self.city_area}, "
            f"{self.state_region}, "
            f"{self.country}"
        )

        if self.landmark:
            location += f" — {self.landmark}"

        return location

class Order(models.Model):

    PRODUCT_PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    DELIVERY_PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(
    max_length=50,
    unique=True,
    null=True,
    blank=True
)

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(
        max_length=30,
        default=""
    )

    address = models.CharField(
        max_length=255
    )

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    zip_code = models.CharField(
        max_length=30,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        default="Nigeria"
    )

    delivery_location = models.ForeignKey(
    DeliveryLocation,
    on_delete=models.PROTECT,
    null=True,
    blank=True
)

    # Products only
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # Fee customer pays for Paystack
    processing_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    # Delivery charge — NOT part of Paystack payment
    delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    # What customer pays online:
    # subtotal + processing_fee
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # Paystack transaction reference
    reference = models.CharField(
        max_length=100,
        unique=True
    )

    product_payment_status = models.CharField(
        max_length=20,
        choices=PRODUCT_PAYMENT_STATUS,
        default='pending'
    )

    delivery_payment_status = models.CharField(
        max_length=20,
        choices=DELIVERY_PAYMENT_STATUS,
        default='pending'
    )
    
    ORDER_METHOD_CHOICES = [
    ('paystack', 'Pay Online'),
    ('whatsapp', 'Order via WhatsApp'),
]
    order_method = models.CharField(
    max_length=20,
    choices=ORDER_METHOD_CHOICES,
    default='paystack'
)

    delivery_payment_method = models.CharField(
        max_length=30,
        default='pay_on_delivery'
    )

    status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.order_number or f"Order {self.pk}"
    
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_name = models.CharField(
        max_length=200
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    def __str__(self):
        return (
            f"{self.product_name} "
            f"x {self.quantity}"
        )

    @property
    def line_total(self):
        return self.unit_price * self.quantity
    



