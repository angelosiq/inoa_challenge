from rest_framework import serializers
from stocks.models import PriceLogUserProfile, Stock, StockUserProfile, UserProfile


class StockUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockUserProfile
        fields = "__all__"


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class PriceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceLogUserProfile
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
