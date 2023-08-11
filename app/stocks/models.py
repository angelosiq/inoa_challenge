from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

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

    is_active = models.BooleanField(default=True)
    checking_time_interval = models.IntegerField(choices=INTERVALS, default=TEN_MINUTES)
    task = models.OneToOneField(PeriodicTask, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"

    def __str__(self):
        return self.name

    def setup_task(self):
        self.task = PeriodicTask.objects.create(
            name=self.symbol,
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


class Price(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    current = models.DecimalField(max_digits=10, decimal_places=2)
    open = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()

    class Meta:
        verbose_name = "Price"
        verbose_name_plural = "Prices"

    def __str__(self):
        return f"{self.stock} - {self.timestamp}"


@receiver(post_save, sender=Stock)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
    if created:
        instance.setup_task()
    else:
        if instance.task is not None:
            instance.task.enabled = instance.is_active is True
            instance.task.save()
