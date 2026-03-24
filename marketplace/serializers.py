from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Producer,
    Product,
    ProductBatch,
    Order,
    OrderItem,
    OrderItemAllocation,
    Category,
)


class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = ["id", "name", "email", "postcode"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class ProductBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBatch
        fields = [
            "id",
            "batch_code",
            "quantity_available",
            "expiry_date",
            "harvest_date",
            "is_approved",
            "created_at",
        ]

class ProductSerializer(serializers.ModelSerializer):
    producer = ProducerSerializer(read_only=True)
    producer_id = serializers.PrimaryKeyRelatedField(
        source="producer",
        queryset=Producer.objects.all(),
        write_only=True,
    )

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    total_stock = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "availability_date",
            "is_active",
            "total_stock",
            "is_available",
            "producer",
            "producer_id",
            "category",
            "category_id",
        ]


class OrderItemReadSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "unit_price", "line_total"]


class OrderItemWriteSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
    )
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source="customer.username", read_only=True)
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "created_at",
            "status",
            "payment_status",
            "total_amount",
            "items",
        ]
        read_only_fields = ["created_at", "status", "payment_status", "total_amount"]


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemWriteSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")

        product_ids = [item["product"].id for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Duplicate products are not allowed in one order.")

        today = timezone.now().date()

        for item in value:
            product = item["product"]
            quantity = item["quantity"]

            if not product.is_active:
                raise serializers.ValidationError(
                    f"Product '{product.name}' is not currently active."
                )

            if product.availability_date and product.availability_date > today:
                raise serializers.ValidationError(
                    f"Product '{product.name}' is not available until {product.availability_date}."
                )

            available_total = product.valid_batches().aggregate(
                total=Sum("quantity_available")
            )["total"] or 0

            if quantity > available_total:
                raise serializers.ValidationError(
                    f"Only {available_total} units of '{product.name}' are available."
                )

        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        items_data = validated_data["items"]

        order = Order.objects.create(customer=request.user)
        total = Decimal("0.00")

        for item in items_data:
            product = Product.objects.select_for_update().get(pk=item["product"].pk)
            quantity_needed = item["quantity"]

            valid_batches = product.valid_batches().select_for_update()

            available_total = valid_batches.aggregate(
                total=Sum("quantity_available")
            )["total"] or 0

            if quantity_needed > available_total:
                raise serializers.ValidationError(
                    f"Not enough stock for '{product.name}'."
                )

            unit_price = product.price
            line_total = unit_price * quantity_needed

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity_needed,
                unit_price=unit_price,
                line_total=line_total,
            )

            remaining = quantity_needed
            for batch in valid_batches:
                if remaining == 0:
                    break

                take = min(batch.quantity_available, remaining)
                if take <= 0:
                    continue

                OrderItemAllocation.objects.create(
                    order_item=order_item,
                    batch=batch,
                    quantity=take,
                )

                batch.quantity_available -= take
                batch.save(update_fields=["quantity_available"])

                remaining -= take

            total += line_total

        order.total_amount = total
        order.save(update_fields=["total_amount"])

        return order