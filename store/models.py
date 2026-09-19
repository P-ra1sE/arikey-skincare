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


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    ORDER_CHANNEL_CHOICES = [
        ('website', 'Website'),
        ('whatsapp', 'WhatsApp'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('paystack', 'Paystack'),
        ('whatsapp', 'WhatsApp Arrangement'),
    ]

    order_channel = models.CharField(
        max_length=20,
        choices=ORDER_CHANNEL_CHOICES,
        default='website'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='paystack'
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

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
        max_length=30
    )

    country = models.CharField(
        max_length=100
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    shipping = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    reference = models.CharField(
        max_length=100,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.reference} - "
            f"{self.first_name} {self.last_name}"
        )


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