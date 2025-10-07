from django.contrib import admin

from . import models


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user"]


@admin.register(models.WialonToken)
class WialonTokenAdmin(admin.ModelAdmin):
    list_display = ["customer"]


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["customer"]
