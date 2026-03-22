from rest_framework import filters, status, viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Producer, Product, Order, Category
from .serializers import (
    ProducerSerializer,
    ProductSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    CategorySerializer,
)


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class ProducerViewSet(viewsets.ModelViewSet):
    queryset = Producer.objects.all().order_by("id")
    serializer_class = ProducerSerializer
    permission_classes = [IsStaffOrReadOnly]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("producer", "category").all().order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    def get_queryset(self):
        queryset = Product.objects.select_related("producer", "category").all().order_by("id")
        category_id = self.request.query_params.get("category")

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()

        queryset = Order.objects.select_related("customer").prefetch_related(
            "items__product__producer"
        ).order_by("-created_at")

        if user.is_staff:
            return queryset

        return queryset.filter(customer=user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        output = OrderSerializer(order, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)