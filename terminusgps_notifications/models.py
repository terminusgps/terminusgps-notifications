from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from encrypted_field import EncryptedField
from terminusgps.authorizenet.constants import SubscriptionStatus
from terminusgps.wialon.session import WialonSession


class Customer(models.Model):
    """A Terminus GPS Notifications customer."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """Django user."""
    tax_rate = models.DecimalField(
        max_digits=9, decimal_places=4, default=0.0825
    )
    """Tax rate."""
    subscription = models.ForeignKey(
        "terminusgps_payments.Subscription",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    """Notifications subscription."""
    wialon_resource_id = models.PositiveIntegerField(null=True, blank=True)
    """Wialon resource id."""
    wialon_token = models.OneToOneField(
        "terminusgps_notifications.WialonToken",
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )
    """Wialon API token."""

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        """Returns the customer's username."""
        return self.user.username

    @property
    def is_subscribed(self) -> bool:
        """Whether the customer is subscribed."""
        if self.subscription is None:
            return False
        status = self.subscription.status
        active = SubscriptionStatus.ACTIVE
        return status == active


class WialonToken(models.Model):
    """A Wialon API token."""

    name = EncryptedField(max_length=72)
    """Wialon token name."""
    date_created = models.DateTimeField(auto_now_add=True)
    """Date/time created."""
    date_updated = models.DateTimeField(auto_now=True)
    """Date/time updated."""

    class Meta:
        verbose_name = _("wialon token")
        verbose_name_plural = _("wialon tokens")

    def __str__(self) -> str:
        return f"WialonToken #{self.pk}"

    @transaction.atomic
    def refresh(self, duration: int = 2_592_000) -> None:
        """
        Refreshes the Wialon API token for another ``duration`` seconds.

        :param duration: Token lifetime duration in seconds. Default is ``2_592_000`` (30 days).
        :type days: int
        :returns: Nothing.
        :rtype: None

        """
        with WialonSession(token=settings.TERMINUSGPS_WIALON_TOKEN) as session:
            session.wialon_api.token_update(
                **{
                    "callMode": "update",
                    "h": self.name,
                    "app": "Terminus GPS Notifications",
                    "at": 0,
                    "dur": duration,
                    "fl": settings.WIALON_TOKEN_ACCESS_TYPE,
                    "p": "{}",
                }
            )


class Notification(models.Model):
    """A notification."""

    customer = models.ForeignKey(
        "terminusgps_notifications.Customer",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    """Associated customer."""

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")

    def __str__(self) -> str:
        return f"Notification #{self.pk}"
