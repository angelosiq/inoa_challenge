from brapi_api.viewsets import BrapiApiQuoteTickerViewset
from rest_framework import routers
from stocks.viewsets import PriceViewSet, StockViewSet

router = routers.DefaultRouter()
router.register(r"brapi_api/quote", BrapiApiQuoteTickerViewset, basename="brapi-api-quote-ticker")
router.register(r"stocks", StockViewSet, basename="stock")
router.register(r"prices", PriceViewSet, basename="price")
