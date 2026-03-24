from django.contrib import admin
from .models import Producer, Category, Product, ProductBatch, Order, OrderItem, OrderItemAllocation


class ProductBatchInline(admin.TabularInline):
    model = ProductBatch
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "producer", "category", "price", "is_active")
    list_filter = ("category", "producer", "is_active")
    search_fields = ("name", "description")
    inlines = [ProductBatchInline]


@admin.register(ProductBatch)
class ProductBatchAdmin(admin.ModelAdmin):
    list_display = (
        "batch_code",
        "product",
        "quantity_available",
        "expiry_date",
        "harvest_date",
        "is_approved",
    )
    list_filter = ("is_approved", "expiry_date", "product__category")
    search_fields = ("batch_code", "product__name")


admin.site.register(Producer)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderItemAllocation)