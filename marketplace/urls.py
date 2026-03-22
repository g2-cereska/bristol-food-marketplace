from rest_framework.routers import DefaultRouter
from .views import ProducerViewSet, ProductViewSet, OrderViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r"producers", ProducerViewSet, basename="producer")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = router.urls