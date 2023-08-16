from celery import shared_task
from core.networking import RequestsRetry, make_request
from django.conf import settings
from django_celery_beat.models import PeriodicTask
from rest_framework.authtoken.models import Token
from stocks.models import PriceLogUserProfile, StockUserProfile
from stocks.serializers import PriceLogSerializer


@shared_task(name="update_stock_data")
def update_stock_data(stock_user_profile_pk):
    try:
        stock_user_profile = StockUserProfile.objects.get(id=stock_user_profile_pk)
    except StockUserProfile.DoesNotExist:
        PeriodicTask.objects.get(args=f"[{stock_user_profile_pk}]").delete()
        return "Task deleted"

    client = RequestsRetry().session
    response = make_request(
        fetch_method=client.get,
        endpoint=f"{settings.BRAPI_API_URL}/api/quote/{stock_user_profile.stock.symbol}",
        params={"range": "1d", "interval": "1m"},
    )

    if response:
        data = response["results"][0]

        price = PriceLogUserProfile.objects.create(
            stock_user_profile=stock_user_profile,
            current_price=data["regularMarketPrice"],
            timestamp=data["regularMarketTime"],
            open=data["regularMarketOpen"],
            close=data["regularMarketPreviousClose"],
            high=data["regularMarketDayHigh"],
            low=data["regularMarketDayLow"],
            volume=data["regularMarketVolume"],
        )

        if stock_user_profile.buy_price and data["regularMarketPrice"] <= stock_user_profile.buy_price:
            _send_notification(stock_user_profile, type_="BUY")
        if stock_user_profile.sell_price and data["regularMarketPrice"] >= stock_user_profile.sell_price:
            _send_notification(stock_user_profile, type_="SELL")

        return PriceLogSerializer(price).data

    return


def _send_notification(stock_user_profile, type_="BUY"):
    user = stock_user_profile.user.user
    token = Token.objects.get(user=user).key

    client = RequestsRetry().session
    make_request(
        fetch_method=client.post,
        endpoint=f"{settings.CURRENT_HOST}/api/user_profile/send_notification/",
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
        json={"message": f"{type_} the stock {stock_user_profile.stock.symbol} now!"},
    )
