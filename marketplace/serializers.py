from decimal import Decimal

from rest_framework import serializers
from .models import Producer, Product, Order, OrderItem, Category


class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = ["id", "name", "email", "postcode"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


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

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "availability_date",
            "producer",
            "producer_id",
            'category',
            'category_id',
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
        fields = ["id", "customer", "created_at", "status", "total_amount", "items"]
        read_only_fields = ["created_at", "status", "total_amount"]


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemWriteSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        items_data = validated_data["items"]

        order = Order.objects.create(customer=request.user)
        total = Decimal("0.00")

        for item in items_data:
            product = item["product"]
            quantity = item["quantity"]
            unit_price = product.price
            line_total = unit_price * quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
            )

            total += line_total

        order.total_amount = total
        order.save()

        return order