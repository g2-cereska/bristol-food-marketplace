from rest_framework import viewsets, filters
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticatedOrReadOnly
from .models import Producer, Product, Order
from .serializers import ProducerSerializer, ProductSerializer, OrderSerializer

def perform_create(self, serializer):
    serializer.save(customer_name=self.request.user.username)

class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class ProducerViewSet(viewsets.ModelViewSet):
    queryset = Producer.objects.all().order_by("id")
    serializer_class = ProducerSerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("producer").all().order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("products").all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

