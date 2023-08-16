from core.networking import RequestsRetry, make_request
from django.conf import settings


def get_stock_latest_data(stock_symbol):
    client = RequestsRetry().session
    response = make_request(
        fetch_method=client.get,
        endpoint=f"{settings.BRAPI_API_URL}/api/quote/{stock_symbol}",
        params={"range": "1d", "interval": "1m"},
    )

    if response:
        try:
            return response["results"][0] if "," not in stock_symbol else response["results"]
        except IndexError:
            return None
    return None


def get_dict_stock_latest_price(stock_symbol):
    stock_data = get_stock_latest_data(stock_symbol)
    if "," not in stock_symbol:
        return {
            stock_symbol: stock_data["regularMarketPrice"],
        }
    return {stock_data_element["symbol"]: stock_data_element["regularMarketPrice"] for stock_data_element in stock_data}
