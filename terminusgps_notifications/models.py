from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_field import EncryptedField
from terminusgps.authorizenet.constants import SubscriptionStatus


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

    value = EncryptedField()
    """Wialon token value."""
    date_created = models.DateTimeField(auto_now_add=True)
    """Date/time created."""
    date_updated = models.DateTimeField(auto_now=True)
    """Date/time updated."""

    class Meta:
        verbose_name = _("wialon token")
        verbose_name_plural = _("wialon tokens")

    def __str__(self) -> str:
        return f"WialonToken #{self.pk}"


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
