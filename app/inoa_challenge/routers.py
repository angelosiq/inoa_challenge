from rest_framework import routers
from stocks.viewsets import StockViewSet

router = routers.DefaultRouter()
router.register(r"stocks", StockViewSet, basename="stock")
