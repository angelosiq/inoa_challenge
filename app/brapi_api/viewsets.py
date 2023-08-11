from brapi_api.requests import BrapiApiRequest
from brapi_api.serializers import QuoteListSerializer, QuoteTickerSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response


class BrapiApiQuoteTickerViewset(viewsets.ViewSet):

    lookup_field = "ticker"

    def retrieve(self, request, ticker):
        brapi_api_client = BrapiApiRequest()

        quote_ticker_list = brapi_api_client.get_quote_ticker(ticker, query=request.GET)

        serializer = QuoteTickerSerializer(data=quote_ticker_list)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        brapi_api_client = BrapiApiRequest()

        quote_list = brapi_api_client.get_quote_list(query=request.GET)

        serializer = QuoteListSerializer(data=quote_list)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
