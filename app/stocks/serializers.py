from rest_framework import serializers

from .models import Price, Stock


class StockSerializer(serializers.ModelSerializer):

    remote_endpoint = serializers.CharField(read_only=True)

    class Meta:
        model = Stock
        fields = "__all__"


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = "__all__"
