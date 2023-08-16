from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import ExpressionWrapper, F, FloatField, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"

    def __str__(self):
        return self.symbol


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        name = self.user.get_full_name() if self.user.get_full_name() else self.user.username
        return f"Perfil de {name}"

    def check_balance(self, amount, remove_funds=False):
        if amount <= 0:
            raise ValueError("O valor precisa ser maior que zero")
        if self.balance < amount and remove_funds:
            raise ValueError("Saldo insuficiente")

    def add_funds(self, amount):
        self.check_balance(amount)
        self.balance += amount
        self.save()
        return self.balance

    def remove_funds(self, amount):
        self.check_balance(amount, remove_funds=True)
        self.balance -= amount
        self.save()
        return self.balance

    def buy_stocks(self, amount, stock_symbol, is_active, checking_time_interval):
        from brapi_api.services import get_stock_latest_data

        stock = Stock.objects.get_or_create(symbol=stock_symbol)[0]
        stock_user_profile, created_stock_user_profile = StockUserProfile.objects.get_or_create(user=self, stock=stock)

        stock_latest_data = get_stock_latest_data(stock_symbol)
        stock_price = Decimal(stock_latest_data["regularMarketPrice"])

        self.check_balance(amount * stock_price, remove_funds=True)
        stock_user_profile.create_transaction(transaction_type="BUY", amount=amount, price_per_stock=stock_price)

        if created_stock_user_profile:
            stock_user_profile.amount = amount
        else:
            stock_user_profile.amount += amount

        stock_user_profile.checking_time_interval = checking_time_interval
        stock_user_profile.is_active = is_active
        stock_user_profile.save()

        self.remove_funds(amount * stock_price)
        return stock_user_profile

    def sell_stocks(self, amount, stock_symbol):
        from brapi_api.services import get_stock_latest_data

        try:
            stock = Stock.objects.get(symbol=stock_symbol)
            stock_user_profile = StockUserProfile.objects.get(user=self, stock=stock)
        except (Stock.DoesNotExist, StockUserProfile.DoesNotExist):
            raise ValueError("Ação não encontrada")

        if stock_user_profile.amount < amount:
            raise ValueError("Quantidade de ações insuficiente")

        stock_latest_data = get_stock_latest_data(stock_symbol)
        stock_price = Decimal(stock_latest_data["regularMarketPrice"])

        stock_user_profile.create_transaction(transaction_type="SELL", amount=amount, price_per_stock=stock_price)

        stock_user_profile.amount -= amount
        stock_user_profile.save()

        self.add_funds(amount * stock_price)
        return stock_user_profile

    def get_sell_stock_list(self, filter_by_symbol=None):
        from brapi_api.services import get_dict_stock_latest_price

        stock_user_profile = StockUserProfile.objects.filter(user=self, amount__gt=0)

        symbols = stock_user_profile.values_list("stock__symbol", flat=True)
        price_dict = get_dict_stock_latest_price(",".join(symbols))

        stocks = [
            {
                "symbol": sup.stock.symbol,
                "amount": sup.amount,
                "current_price": price_dict[sup.stock.symbol],
                "total": sup.amount * price_dict[sup.stock.symbol],
            }
            for sup in stock_user_profile
        ]

        if not filter_by_symbol:
            return stocks

        try:
            return [stock for stock in stocks if stock["symbol"] == filter_by_symbol][0]
        except IndexError as exc:
            raise ValueError("Ação não encontrada") from exc


class StockUserProfile(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null=True, blank=True)

    ONE_MINUTE = 1
    FIVE_MINUTES = 5
    TEN_MINUTES = 10
    THIRTY_MINUTES = 30
    SIXTY_MINUTES = 60
    NINTY_MINUTES = 90
    ONE_HUNDRED_AND_TWENTY_MINUTES = 120
    INTERVALS = (
        (ONE_MINUTE, _("1 minuto")),
        (FIVE_MINUTES, _("5 minutos")),
        (TEN_MINUTES, _("10 minutos")),
        (THIRTY_MINUTES, _("30 minutos")),
        (SIXTY_MINUTES, _("60 minutos")),
        (NINTY_MINUTES, _("90 minutos")),
        (ONE_HUNDRED_AND_TWENTY_MINUTES, _("120 minutos")),
    )

    is_active = models.BooleanField(default=False)
    checking_time_interval = models.IntegerField(choices=INTERVALS, default=TEN_MINUTES)
    task = models.OneToOneField(PeriodicTask, on_delete=models.CASCADE, null=True, blank=True)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ("user", "stock")

    def __str__(self):
        return f"{self.user} - {self.stock}"

    def setup_task(self):
        self.task = PeriodicTask.objects.create(
            name=str(self),
            task="update_stock_data",
            interval=self.interval_schedule,
            args=[self.id],
            start_time=timezone.now(),
        )
        self.save()

    @property
    def interval_schedule(self):
        return IntervalSchedule.objects.get(every=self.checking_time_interval, period="minutes")

    def delete(self, *args, **kwargs):
        if self.task is not None:
            self.task.delete()
        return super().delete(*args, **kwargs)

    def create_transaction(self, transaction_type, amount, price_per_stock):
        return Transaction.objects.create(
            stock_user_profile=self,
            transaction_type=transaction_type,
            amount=amount,
            price_per_stock=price_per_stock,
        )

    @classmethod
    def chart(cls, profile_id):
        from brapi_api.services import get_dict_stock_latest_price

        all_symbols = cls.objects.filter(user_id=profile_id).values_list("stock__symbol", flat=True).distinct()

        if not all_symbols:
            return None

        price_dict = get_dict_stock_latest_price(",".join(all_symbols))

        queryset = (
            cls.objects.filter(user_id=profile_id)
            .values("stock", "stock__symbol")
            .annotate(
                total_investment=ExpressionWrapper(Sum(F("amount")), output_field=FloatField()),
            )
            .filter(total_investment__gt=0)
            .order_by("stock__symbol")
        )

        if not queryset:
            return None

        for el in queryset:
            el["total_investment"] = el["total_investment"] * price_dict[el["stock__symbol"]]

        return {
            "type": "doughnut",
            "data": {
                "labels": [item["stock__symbol"] for item in queryset],
                "datasets": [
                    {"label": "Patrimônio", "data": [item["total_investment"] for item in queryset], "hoverOffset": 4}
                ],
            },
        }


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("BUY", "Comprar"),
        ("SELL", "Vender"),
    )

    stock_user_profile = models.ForeignKey(StockUserProfile, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    amount = models.PositiveIntegerField()
    price_per_stock = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock_user_profile} - {self.transaction_type} - {self.amount} - {self.price_per_stock}"


class PriceLogUserProfile(models.Model):
    stock_user_profile = models.ForeignKey(StockUserProfile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    open = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()

    class Meta:
        verbose_name = "Price Log"
        verbose_name_plural = "Prices Logs"

    def __str__(self):
        return f"{self.stock_user_profile.user} - {self.stock_user_profile.stock} - {self.timestamp}"


@receiver(post_save, sender=StockUserProfile)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()

    if instance.task is not None:
        instance.task.enabled = instance.is_active is True
        instance.task.interval = instance.interval_schedule
        instance.task.save()
