from celery import shared_task
from core.networking import RequestsRetry, make_request
from django.conf import settings
from stocks.models import Price, Stock
from stocks.serializers import PriceSerializer


@shared_task(name="update_stock_data")
def update_stock_data(stock_pk):
    try:
        stock = Stock.objects.get(id=stock_pk)
    except Stock.DoesNotExist:
        return

    client = RequestsRetry().session
    response = make_request(
        fetch_method=client.get,
        endpoint=f"{settings.BRAPI_API_URL}/api/quote/{stock.symbol}",
        params={"range": "1d", "interval": "1m"},
    )

    if response:
        data = response["results"][0]
        price = Price.objects.create(
            stock=stock,
            current=data["regularMarketPrice"],
            timestamp=data["regularMarketTime"],
            open=data["regularMarketOpen"],
            close=data["regularMarketPreviousClose"],
            high=data["regularMarketDayHigh"],
            low=data["regularMarketDayLow"],
            volume=data["regularMarketVolume"],
        )
        return PriceSerializer(price).data

    return
