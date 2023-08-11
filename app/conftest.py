import pytest
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.fixture(name="api_client")
def client_api():
    client = APIClient
    return client


@pytest.fixture()
def stock():
    return baker.make("stocks.Stock")
