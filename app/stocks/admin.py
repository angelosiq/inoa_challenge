from django.contrib import admin
from stocks import models

admin.site.register(models.Stock)
admin.site.register(models.StockUserProfile)
admin.site.register(models.UserProfile)
admin.site.register(models.Transaction)
admin.site.register(models.PriceLogUserProfile)
