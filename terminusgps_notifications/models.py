import typing
import urllib.parse

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinLengthValidator
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from encrypted_field import EncryptedField
from terminusgps.wialon import flags
from terminusgps.wialon.session import WialonSession

from .constants import WialonNotificationTrigger


def validate_is_digit(value: str) -> None:
    if not value.isdigit():
        raise ValidationError(
            _("This value can only contain digits, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )


class Customer(models.Model):
    """A Terminus GPS Notifications customer."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """Django user."""
    wialon_token = models.ForeignKey(
        "terminusgps_notifications.WialonToken",
        on_delete=models.SET_NULL,
        related_name="customers",
        blank=True,
        null=True,
        default=None,
    )
    """Associated Wialon API token."""
    resource_id = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        default=None,
        help_text="Please provide an 8-digit Wialon resource id for notifications.",
        validators=[validate_is_digit, MinLengthValidator(8)],
    )
    """Wialon resource id."""
    max_sms_count = models.IntegerField(
        default=500,
        help_text="Please enter the maximum number of allowed sms messages for the customer in a single period.",
    )
    """Maximum number of allowed sms messages for the period."""
    max_voice_count = models.IntegerField(
        default=500,
        help_text="Please enter the maximum number of allowed voice messages for the customer in a single period.",
    )
    """Maximum number of allowed voice messages for the period."""
    sms_count = models.IntegerField(
        default=0,
        help_text="Please enter the current sms message count for the customer.",
    )
    """Current number of sms messages for the period."""
    voice_count = models.IntegerField(
        default=0,
        help_text="Please enter the current voice message count for the customer.",
    )
    """Current number of voice messages for the period."""

    tax_rate = models.DecimalField(
        max_digits=9,
        decimal_places=4,
        default=0.0825,
        help_text="Please enter a tax rate for the customer.",
    )
    """Subscription tax rate."""
    subtotal = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=44.99,
        help_text="Please enter a dollar amount to charge the customer (+tax) every period.",
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

    def get_unit_choices(self) -> list[tuple[int, str]]:
        if self.wialon_token is None:
            return []
        with WialonSession(token=self.wialon_token.name) as session:
            return [
                (int(unit.get("id")), _(str(unit.get("nm"))))
                for unit in self._get_wialon_unit_list(session)
            ]

    def _get_wialon_unit_list(self, session: WialonSession) -> dict:
        return session.wialon_api.core_search_items(
            **{
                "spec": {
                    "itemsType": "avl_unit",
                    "propName": "sys_name",
                    "propValueMask": "*",
                    "sortType": "sys_name",
                    "propType": "property",
                },
                "force": int(False),
                "flags": flags.DataFlag.UNIT_BASE,
                "from": 0,
                "to": 0,
            }
        ).get("items", {})


class WialonToken(models.Model):
    """A Wialon API token."""

    name = EncryptedField(max_length=72)
    """Wialon API token name."""

    def __str__(self) -> str:
        """Returns the Wialon API token id."""
        return str(self.pk)


class WialonNotification(models.Model):
    """Wialon notification."""

    class WialonNotificationMethod(models.TextChoices):
        """Wialon notification method."""

        SMS = "sms", _("SMS")
        VOICE = "voice", _("Voice")

    wialon_id = models.PositiveIntegerField()
    """Wialon id."""
    customer = models.ForeignKey(
        "terminusgps_notifications.Customer",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    """Associated customer."""

    name = models.CharField(
        max_length=64,
        help_text="Please provide a memorable name for your notification.",
    )
    """Notification name."""
    text = models.TextField(max_length=1024)
    """Notification text."""
    method = models.CharField(
        max_length=5,
        default=WialonNotificationMethod.SMS,
        choices=WialonNotificationMethod.choices,
        help_text="Please select a notification method.",
    )
    """Notification method."""
    trigger = models.CharField(
        max_length=64,
        choices=WialonNotificationTrigger.choices,
        default=WialonNotificationTrigger.SENSOR,
        help_text="Please select a notification trigger.",
    )
    """Notification trigger."""
    trigger_parameters = models.JSONField(default=dict)
    """Notification trigger parameters."""
    activation_time = models.DateTimeField(
        default=timezone.now,
        null=True,
        blank=True,
        help_text="Please provide a valid date and time to activate the notification.",
    )
    """Activation date/time."""
    deactivation_time = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text="Please provide a valid date and time to deactivate the notification. Leave this blank to never deactivate.",
    )
    """Deactivation date/time."""
    max_alarms = models.PositiveIntegerField(
        default=0,
        help_text="Please provide the maximum number of alarms. 0 = unlimited alarms.",
    )
    """Maximum number of alarms (0 = unlimited)."""
    max_message_interval = models.PositiveIntegerField(
        default=0,
        choices=[
            (0, _("Any time")),
            (60, _("1 minute")),
            (600, _("10 minutes")),
            (1800, _("30 minutes")),
            (3600, _("1 hour")),
            (21600, _("6 hours")),
            (43200, _("12 hours")),
            (86400, _("1 day")),
            (864000, _("10 days")),
        ],
        help_text="Please provide the maximum allowed time between messages.",
    )
    """Max time interval between messages."""
    alarm_timeout = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(1800)],
        help_text="Please provide the number of seconds before alarm timeout. 0 = never timeout.",
    )
    """Alarm timeout in seconds. Max is ``1800`` (30 minutes in seconds)."""
    control_period = models.PositiveIntegerField(
        default=0,
        choices=[
            (0, _("Any time")),
            (60, _("Last minute")),
            (600, _("Last 10 minutes")),
            (3600, _("Last hour")),
            (86400, _("Last day")),
        ],
        help_text="Please provide the control period relative to current time.",
    )
    """Control period relative to current time in seconds."""
    min_duration_alarm = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(86400)],
        help_text="Please provide the minimum duration of alarm state in seconds.",
    )
    """Minimum duration of alarm state in seconds. Max is ``86400`` (1 day)."""
    min_duration_prev = models.PositiveIntegerField(
        default=0, validators=[MaxValueValidator(86400)]
    )
    """Minimum duration of previous state in seconds. Max is ``86400`` (1 day)."""
    language = models.CharField(
        max_length=2, default="en", choices={("en", _("English"))}
    )
    """2-letter language code."""
    units = models.CharField(blank=True, default="")
    """Comma-separated list of units for the notification."""
    flags = models.PositiveSmallIntegerField(
        default=0,
        choices={
            (0, _("Trigger on first message")),
            (1, _("Trigger on every message")),
            (2, _("Disabled")),
        },
    )
    """Flags."""

    class Meta:
        verbose_name = _("wialon notification")
        verbose_name_plural = _("wialon notifications")

    def __str__(self) -> str:
        """Returns the notification name."""
        return str(self.name)

    def get_action(self) -> dict[str, typing.Any]:
        """Returns the notification's action dictionary."""
        return {
            "act": {
                "t": "push_messages",
                "p": {
                    "url": urllib.parse.urljoin(
                        "https://api.terminusgps.com/",
                        f"/v3/notify/{self.method}/",
                    ),
                    "get": 1,
                },
            }
        }
