from rest_framework import serializers


class QuoteTickerSerializer(serializers.Serializer):

    results = serializers.ListField()
    requestedAt = serializers.DateTimeField(required=False)
    took = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class QuoteListSerializer(serializers.Serializer):

    indexes = serializers.ListField(required=False)
    stocks = serializers.ListField(required=False)
