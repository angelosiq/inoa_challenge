from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from stocks.models import PriceLogUserProfile, Stock, StockUserProfile, UserProfile
from stocks.serializers import PriceLogSerializer, StockSerializer, UserProfileSerializer


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class PriceLogViewSet(viewsets.ModelViewSet):
    queryset = PriceLogUserProfile.objects.all()
    serializer_class = PriceLogSerializer


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=["get"])
    def get_info(self, request):
        user = request.user.userprofile
        return Response(
            {
                "balance": user.balance,
                "chart": StockUserProfile.chart(user.pk),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def add_funds(self, request):
        user = request.user.userprofile
        amount = request.data.get("amount")

        try:
            user.add_funds(amount)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"balance": user.balance}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def buy_stocks(self, request):
        user = request.user.userprofile
        amount = request.data.get("amount")
        stock_symbol = request.data.get("stock_symbol")
        is_active = request.data.get("is_active")
        checking_time_interval = request.data.get("checking_time_interval")

        try:
            user.buy_stocks(
                amount=amount,
                stock_symbol=stock_symbol,
                is_active=is_active,
                checking_time_interval=checking_time_interval,
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": f"Adquiridas {amount} unidades de {stock_symbol}."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def sell_stocks(self, request):
        user = request.user.userprofile
        amount = request.data.get("amount")
        stock_symbol = request.data.get("stock_symbol")

        try:
            user.sell_stocks(amount=amount, stock_symbol=stock_symbol)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"success": f"Vendidas {amount} unidades de {stock_symbol}."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def get_sell_stock_list(self, request):
        user = request.user.userprofile
        return Response(
            {
                "stocks": user.get_sell_stock_list(),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def send_notification(self, request):
        message = request.data.get("message")

        channel_layer = get_channel_layer()
        notification_message = {"type": "send_message", "message": message}
        async_to_sync(channel_layer.group_send)("notifications", notification_message)

        return Response({"success": "Mensagem enviada com sucesso!"}, status=status.HTTP_200_OK)
