import pytest
from rest_framework import status
from stocks.models import StockUserProfile, Transaction, UserProfile

pytestmark = pytest.mark.django_db
ENDPOINT = "/api/user_profile"


def test_get_info(api_client, superuser):
    api_client.force_login(user=superuser)
    response = api_client.get(f"{ENDPOINT}/get_info/", format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["balance"] == 1000.0
    assert response.json()["chart"] is None


def test_add_funds(api_client, superuser):
    api_client.force_login(user=superuser)
    response = api_client.post(f"{ENDPOINT}/add_funds/", data={"amount": 10000}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["balance"] == 11000.0


def test_add_funds_negative_value(api_client, superuser):
    api_client.force_login(user=superuser)
    response = api_client.post(f"{ENDPOINT}/add_funds/", data={"amount": -10000}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"error": "O valor precisa ser maior que zero"}


def test_buy_stocks_no_funds(api_client, superuser, monkeypatch, interval):
    api_client.force_login(user=superuser)
    monkeypatch.setattr("stocks.models.StockUserProfile.interval_schedule", interval)

    response = api_client.post(
        f"{ENDPOINT}/buy_stocks/",
        data={"amount": 5000, "stock_symbol": "PETR4", "is_active": False, "checking_time_interval": 5},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"error": "Saldo insuficiente"}


def _buy_stocks(api_client, superuser, monkeypatch, interval):
    def mock_get_stock_latest_data(stock_symbol):
        return {
            "regularMarketPrice": "35.5",
        }

    api_client.force_login(user=superuser)

    monkeypatch.setattr("stocks.models.StockUserProfile.interval_schedule", interval)
    monkeypatch.setattr("brapi_api.services.get_stock_latest_data", mock_get_stock_latest_data)

    profile = UserProfile.objects.get(user=superuser)
    profile.balance = 10000000
    profile.save()

    return api_client.post(
        f"{ENDPOINT}/buy_stocks/",
        data={"amount": 5000, "stock_symbol": "PETR4", "is_active": False, "checking_time_interval": 5},
        format="json",
    )


def test_buy_stocks(api_client, superuser, monkeypatch, interval):
    response = _buy_stocks(api_client, superuser, monkeypatch, interval)

    stock_user_profile = StockUserProfile.objects.all()[0]
    buy_transaction = Transaction.objects.all()[0]

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"success": "Adquiridas 5000 unidades de PETR4."}

    assert stock_user_profile.amount == 5000

    assert buy_transaction.amount == 5000
    assert buy_transaction.transaction_type == "BUY"


def test_sell_stocks(api_client, superuser, monkeypatch, interval):
    _buy_stocks(api_client, superuser, monkeypatch, interval)

    response = api_client.post(
        f"{ENDPOINT}/sell_stocks/", data={"amount": 1500, "stock_symbol": "PETR4"}, format="json"
    )

    stock_user_profile = StockUserProfile.objects.all()[0]
    buy_transaction = Transaction.objects.all()[0]
    sell_transaction = Transaction.objects.all()[1]

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"success": "Vendidas 1500 unidades de PETR4."}

    assert stock_user_profile.amount == 3500

    assert buy_transaction.amount == 5000
    assert buy_transaction.transaction_type == "BUY"

    assert sell_transaction.amount == 1500
    assert sell_transaction.transaction_type == "SELL"


def test_sell_stocks_not_enough_stocks(api_client, superuser, monkeypatch, interval):
    _buy_stocks(api_client, superuser, monkeypatch, interval)

    response = api_client.post(
        f"{ENDPOINT}/sell_stocks/", data={"amount": 5001, "stock_symbol": "PETR4"}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"error": "Quantidade de ações insuficiente"}


def test_get_sell_stock_list(api_client, superuser, monkeypatch, interval):
    _buy_stocks(api_client, superuser, monkeypatch, interval)

    def mock_get_dict_stock_latest_price(stock_symbol):
        return {
            "PETR4": 35.5,
        }

    monkeypatch.setattr("brapi_api.services.get_dict_stock_latest_price", mock_get_dict_stock_latest_price)
    response = api_client.get(f"{ENDPOINT}/get_sell_stock_list/", format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "stocks": [{"amount": 5000, "current_price": 35.5, "symbol": "PETR4", "total": 177500.0}]
    }


def test_send_notification(api_client, superuser):
    api_client.force_login(user=superuser)
    response = api_client.post(f"{ENDPOINT}/send_notification/", data={"message": "Mensagem teste."}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"success": "Mensagem enviada com sucesso!"}
