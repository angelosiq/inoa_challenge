from brapi_api.viewsets import BrapiApiQuoteTickerViewset
from rest_framework import routers
from stocks.viewsets import PriceLogViewSet, StockViewSet, UserProfileViewSet

router = routers.DefaultRouter()
router.register(r"brapi_api/quote", BrapiApiQuoteTickerViewset, basename="brapi-api-quote-ticker")
router.register(r"stocks", StockViewSet, basename="stock")
router.register(r"prices_logs", PriceLogViewSet, basename="price-log")
router.register(r"user_profile", UserProfileViewSet, basename="user-profile")
