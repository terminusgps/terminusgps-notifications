import decimal

from authorizenet import apicontractsv1
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from encrypted_field import EncryptedField


class Customer(models.Model):
    """A Terminus GPS Notifications customer."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """Django user."""
    resource_id = models.CharField(
        max_length=8, null=True, blank=True, default=None
    )
    """Wialon resource id."""
    max_sms_count = models.IntegerField(default=500)
    """Maximum number of allowed sms messages for the period."""
    max_voice_count = models.IntegerField(default=500)
    """Maximum number of allowed voice messages for the period."""
    sms_count = models.IntegerField(default=0)
    """Current number of sms messages for the period."""
    voice_count = models.IntegerField(default=0)
    """Current number of voice messages for the period."""

    tax_rate = models.DecimalField(
        max_digits=9, decimal_places=4, default=0.0825
    )
    """Subscription tax rate."""
    subtotal = models.DecimalField(
        max_digits=9, decimal_places=2, default=44.99
    )
    """Subscription subtotal."""
    tax = models.GeneratedField(
        expression=(F("subtotal") * (F("tax_rate") + 1)) - F("subtotal"),
        output_field=models.DecimalField(max_digits=9, decimal_places=2),
        db_persist=True,
    )
    """Subscription tax."""
    grand_total = models.GeneratedField(
        expression=F("subtotal") * (F("tax_rate") + 1),
        output_field=models.DecimalField(max_digits=9, decimal_places=2),
        db_persist=True,
    )
    """Subscription grand total (subtotal + tax)."""

    subscription = models.ForeignKey(
        "terminusgps_payments.Subscription",
        on_delete=models.CASCADE,
        related_name="customer",
        null=True,
        blank=True,
        default=None,
    )
    """Associated subscription."""

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        """Returns the customer's username."""
        return self.user.username

    def generate_authorizenet_subscription(
        self,
        customer_profile_id: str,
        payment_profile_id: str,
        address_profile_id: str,
    ) -> apicontractsv1.ARBSubscriptionType:
        # Infinitely recurring starting now
        schedule = apicontractsv1.paymentScheduleType()
        schedule.startDate = timezone.now()
        schedule.totalOccurrences = 9999
        schedule.trialOccurrences = 0

        # Charge profile once per month
        schedule.interval = apicontractsv1.paymentScheduleTypeInterval()
        schedule.interval.length = 1
        schedule.interval.unit = apicontractsv1.ARBSubscriptionUnitEnum.months

        # Set customer data
        profile = apicontractsv1.customerProfileIdType()
        profile.customerProfileId = customer_profile_id
        profile.customerPaymentProfileId = payment_profile_id
        profile.customerAddressId = address_profile_id

        # Create the Authorizenet subscription contract
        anet_subscription = apicontractsv1.ARBSubscriptionType()
        anet_subscription.name = "Terminus GPS Notifications"
        anet_subscription.paymentSchedule = schedule
        anet_subscription.trialAmount = decimal.Decimal("0.00")
        anet_subscription.profile = profile
        anet_subscription.amount = self.grand_total
        return anet_subscription


class WialonToken(models.Model):
    """A Wialon API token."""

    customer = models.OneToOneField(
        "terminusgps_notifications.Customer",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="wialon_token",
    )
    """Associated customer."""
    name = EncryptedField(max_length=72)
    """Wialon API token name."""

    def __str__(self) -> str:
        """Returns '<username>'s Wialon Token'."""
        return f"{self.customer.user.username}'s Wialon Token"


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
