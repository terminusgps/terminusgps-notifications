from django.apps import AppConfig
from django.db.models.signals import post_save


class TerminusgpsNotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "terminusgps_notifications"
    verbose_name = "Terminus GPS Notifications"

    def ready(self):
        from . import models, signals

        post_save.connect(
            signals.create_notification_resource_in_wialon,
            sender=models.TerminusgpsNotificationsCustomer,
        )
