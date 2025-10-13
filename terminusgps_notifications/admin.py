from django.contrib import admin

from . import models


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user"]
    exclude = ["subscription"]
    fieldsets = [
        (None, {"fields": ["user", "date_format", "resource_id"]}),
        ("Pricing", {"fields": ["tax_rate", "subtotal"]}),
        (
            "Messaging",
            {
                "fields": [
                    "max_sms_count",
                    "max_voice_count",
                    "sms_count",
                    "voice_count",
                ]
            },
        ),
    ]


@admin.register(models.WialonToken)
class WialonTokenAdmin(admin.ModelAdmin):
    list_display = ["customer"]
    exclude = ["name"]
    readonly_fields = ["flags"]


@admin.register(models.WialonNotification)
class WialonNotificationAdmin(admin.ModelAdmin):
    list_display = ["customer"]
