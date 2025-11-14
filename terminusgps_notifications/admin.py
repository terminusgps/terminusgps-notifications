from django.contrib import admin

from . import models


@admin.register(models.TerminusgpsNotificationsCustomer)
class TerminusgpsNotificationsCustomerAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "messages_count",
        "messages_max",
        "subscription__status",
    ]
    list_filter = ["subscription__status"]
    readonly_fields = ["tax", "grand_total", "messages_count", "subtotal"]
    exclude = ["subscription"]
    fieldsets = [
        (None, {"fields": ["user", "date_format"]}),
        ("Messaging", {"fields": ["messages_count", "messages_max"]}),
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


@admin.register(models.MessagePackage)
class MessagePackageAdmin(admin.ModelAdmin):
    list_display = ["customer", "price"]


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
        "trigger_type",
        "trigger_parameters",
        "unit_list",
    ]
