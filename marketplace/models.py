from django.db import models
from django.core.validators import MinValueValidator

class Status(models.TextChoices):
    NEW = "NEW", "New"
    CONFIRMED = "CONFIRMED", "Confirmed"
    FULFILLED = "FULFILLED", "Fulfilled"

status = models.CharField(
    max_length=20,
    choices=Status.choices,
    default=Status.NEW
)

class Producer(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField()
    postcode = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)])
    availability_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    
    customer_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status, default="NEW")
    products = models.ManyToManyField(Product, related_name="orders", blank=True)

    def __str__(self) -> str:
        return f"Order #{self.id} ({self.customer_name})"
