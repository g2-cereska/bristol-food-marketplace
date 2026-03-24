from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Producer(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField()
    postcode = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name
    

class Product(models.Model):
    producer = models.ForeignKey(
        Producer,
        on_delete=models.CASCADE,
        related_name="products",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    availability_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def valid_batches(self):
        today = timezone.now().date()
        return self.batches.filter(
            is_approved=True,
            quantity_available__gt=0,
        ).exclude(
            expiry_date__lt=today
        ).order_by("expiry_date", "id")

    @property
    def total_stock(self):
        return self.valid_batches().aggregate(
            total=Sum("quantity_available")
        )["total"] or 0

    @property
    def is_available(self):
        today = timezone.now().date()

        if not self.is_active:
            return False
        if self.availability_date and self.availability_date > today:
            return False
        return self.total_stock > 0

    def __str__(self) -> str:
        return self.name

class ProductBatch(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="batches",
    )
    batch_code = models.CharField(max_length=50, unique=True)
    quantity_available = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)
    harvest_date = models.DateField(null=True, blank=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["expiry_date", "id"]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.batch_code}"

class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        CONFIRMED = "CONFIRMED", "Confirmed"
        FULFILLED = "FULFILLED", "Fulfilled"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"Order #{self.id} ({self.customer.username})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"


class OrderItemAllocation(models.Model):
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f"{self.order_item} <- {self.batch.batch_code} ({self.quantity})"