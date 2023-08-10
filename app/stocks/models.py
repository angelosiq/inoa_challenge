from django.db import models


class Stock(models.Model):
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    checking_time_in_minutes = models.IntegerField(default=5)

    def __str__(self):
        return self.name
