import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from requests.sessions import Session
from rest_framework.exceptions import APIException
from urllib3.util import Retry


class RequestsRetry:
    def __init__(self, retries=3, backoff_factor=0.3, status_forcelist=None, allowed_methods=None):
        self.retries = retries
        self.backoff_factor = backoff_factor
        if status_forcelist is None:
            status_forcelist = (502, 504)
        self.status_forcelist = status_forcelist
        if allowed_methods is None:
            allowed_methods = Retry.DEFAULT_ALLOWED_METHODS
        self.allowed_methods = allowed_methods

    @property
    def session(self):
        session = Session()
        retry = Retry(
            total=self.retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
            allowed_methods=self.allowed_methods,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session


def make_request(fetch_method, endpoint, base_timeout=settings.BASE_TIMEOUT, **kwargs):
    try:
        response = fetch_method(endpoint, timeout=base_timeout, **kwargs)

        if 400 <= response.status_code < 500:
            raise APIException(detail=response.text, code=response.status_code)
        elif response.status_code >= 500:
            raise APIException()

        return response.json()
    except requests.exceptions.RetryError:
        return []
