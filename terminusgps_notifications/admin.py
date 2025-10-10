from django.contrib import admin

from . import models


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user"]
    exclude = ["subscription", "user"]


@admin.register(models.WialonNotification)
class WialonNotificationAdmin(admin.ModelAdmin):
    list_display = ["customer"]
