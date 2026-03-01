from rest_framework import serializers
from .models import Producer, Product, Order


class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = ["id", "name", "email", "postcode"]


class ProductSerializer(serializers.ModelSerializer):
    producer = ProducerSerializer(read_only=True)
    producer_id = serializers.PrimaryKeyRelatedField(
        source="producer",
        queryset=Producer.objects.all(),
        write_only=True
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
        ]


class OrderSerializer(serializers.ModelSerializer):
    product_ids = serializers.PrimaryKeyRelatedField(
        source="products",
        queryset=Product.objects.all(),
        many=True,
        write_only=True
    )
    products = ProductSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_name",
            "created_at",
            "status",
            "products",
            "product_ids",
        ]
        read_only_fields = ["created_at", "status"]