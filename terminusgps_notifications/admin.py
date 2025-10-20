from django.contrib import admin

from . import models


@admin.register(models.TerminusgpsNotificationsCustomer)
class TerminusgpsNotificationsCustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "sms_count", "voice_count", "subscription__status"]
    list_filter = ["subscription__status"]
    readonly_fields = ["tax", "grand_total"]
    exclude = ["subscription"]
    fieldsets = [
        (None, {"fields": ["user", "date_format", "resource_id"]}),
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
        (
            "Pricing",
            {"fields": ["tax_rate", "subtotal", "tax", "grand_total"]},
        ),
    ]


@admin.register(models.WialonToken)
class WialonTokenAdmin(admin.ModelAdmin):
    list_display = ["customer"]
    exclude = ["name"]
    readonly_fields = ["flags"]


@admin.register(models.WialonNotification)
class WialonNotificationAdmin(admin.ModelAdmin):
    list_display = ["name", "customer"]
    list_filter = ["customer"]
    readonly_fields = [
        "text",
        "wialon_id",
        "customer",
        "actions",
        "schedule",
        "control_schedule",
        "trigger",
        "unit_list",
    ]
