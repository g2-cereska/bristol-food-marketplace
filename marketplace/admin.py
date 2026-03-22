from django.contrib import admin
from .models import Producer, Product, Order, OrderItem, Category


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer__username",)
    inlines = [OrderItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "producer", "category", "price", "availability_date")
    list_filter = ("producer", "category", "availability_date")
    search_fields = ("name", "description")


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "postcode")
    search_fields = ("name", "email", "postcode")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "unit_price", "line_total")
    list_filter = ("product",)
    search_fields = ("product__name",)