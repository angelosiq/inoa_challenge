from dataclasses import dataclass
from typing import Dict

from core.networking import RequestsRetry, make_request
from django.conf import settings


@dataclass
class BrapiApiRequest:
    api_url: str = str(settings.BRAPI_API_URL)

    def get_quote_ticker(self, ticker: str, query: Dict = None):
        endpoint = f"{self.api_url}/api/quote/{ticker}"

        client = RequestsRetry().session
        return make_request(client.get, endpoint, params=query)

    def get_quote_list(self, query: Dict = None):
        endpoint = f"{self.api_url}/api/quote/list"

        client = RequestsRetry().session
        return make_request(client.get, endpoint, params=query)
