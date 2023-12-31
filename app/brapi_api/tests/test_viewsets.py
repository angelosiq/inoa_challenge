import pytest
import responses
from rest_framework import status

ENDPOINT = "/api/brapi_api/quote"
pytestmark = pytest.mark.django_db


@responses.activate
def test_retrieve(api_client, superuser, settings, quote_data):
    api_client.force_login(user=superuser)
    with responses.RequestsMock() as rmock:
        rmock.add(
            responses.GET,
            f"{settings.BRAPI_API_URL}/api/quote/COGN3",
            json=quote_data,
            content_type="application/json",
            status=200,
        )

        response = api_client.get(f"{ENDPOINT}/COGN3", format="json", follow=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == quote_data


@responses.activate
def test_list(api_client, superuser, settings, quote_list_data):
    api_client.force_login(user=superuser)
    with responses.RequestsMock() as rmock:
        rmock.add(
            responses.GET,
            f"{settings.BRAPI_API_URL}/api/quote/list",
            json=quote_list_data,
            content_type="application/json",
            status=200,
        )

        response = api_client.get(f"{ENDPOINT}", format="json", follow=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == quote_list_data
