import typing
import urllib.parse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinLengthValidator
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from encrypted_field import EncryptedField
from terminusgps.validators import validate_is_digit
from terminusgps.wialon import flags
from terminusgps.wialon.session import WialonSession

from .constants import WialonNotificationTriggerType


class Customer(models.Model):
    """A Terminus GPS Notifications customer."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """Django user."""
    date_format = models.CharField(
        max_length=64,
        default="%Y-%m-%d %H:%M:%S",
        choices=[
            ("%Y-%m-%d %H:%M:%S", "YYYY-MM-DD HH:MM:SS"),
            ("%Y-%m-%d %H:%M", "YYYY-MM-DD HH:MM"),
        ],
    )
    """Date format for notifications."""
    resource_id = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        default=None,
        help_text="Please enter an 8-digit Wialon resource id to create notifications in.",
        validators=[validate_is_digit, MinLengthValidator(8)],
    )
    """Wialon resource id."""
    max_sms_count = models.PositiveIntegerField(
        default=500,
        help_text="Please enter the maximum number of allowed sms messages for the customer in a single period.",
    )
    """Maximum number of allowed sms messages for the period."""
    max_voice_count = models.PositiveIntegerField(
        default=500,
        help_text="Please enter the maximum number of allowed voice messages for the customer in a single period.",
    )
    """Maximum number of allowed voice messages for the period."""
    sms_count = models.PositiveIntegerField(
        default=0,
        help_text="Please enter the current sms message count for the customer.",
    )
    """Current number of sms messages for the period."""
    voice_count = models.PositiveIntegerField(
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
    """Subscription tax total."""
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
        """Returns the customer user."""
        return str(self.user)

    def get_units_from_wialon(
        self, session: WialonSession, force: bool = False
    ) -> list[dict[str, typing.Any]]:
        """
        Returns a list of of customer Wialon unit dictionaries from the Wialon API.

        Wialon unit dictionary format:

        +------------+---------------+---------------------------+
        | key        | type          | desc                      |
        +============+===============+===========================+
        | ``"mu"``   | :py:obj:`int` | Measurement system        |
        +------------+---------------+---------------------------+
        | ``"nm"``   | :py:obj:`str` | Unit name                 |
        +------------+---------------+---------------------------+
        | ``"cls"``  | :py:obj:`int` | Superclass ID: 'avl_unit' |
        +------------+---------------+---------------------------+
        | ``"id"``   | :py:obj:`int` | Unit ID                   |
        +------------+---------------+---------------------------+
        | ``"uacl"`` | :py:obj:`int` | User's access rights      |
        +------------+---------------+---------------------------+

        :param force: Whether to force a Wialon API call or use Wialon's cached response. Default is :py:obj:`False`.
        :type force: bool
        :returns: A list of Wialon unit dictionaries.
        :rtype: list[dict[str, ~typing.Any]]

        """
        return session.wialon_api.core_search_items(
            **{
                "spec": {
                    "itemsType": "avl_unit",
                    "propName": "sys_id",
                    "propValueMask": "*",
                    "sortType": "sys_id",
                    "propType": "property",
                },
                "force": int(force),
                "flags": flags.DataFlag.UNIT_BASE,
                "from": 0,
                "to": 0,
            }
        ).get("items", [])


class WialonToken(models.Model):
    """Wialon API token."""

    customer = models.OneToOneField(
        "terminusgps_notifications.Customer",
        on_delete=models.CASCADE,
        related_name="token",
    )
    """Associated customer."""

    name = EncryptedField(max_length=72)
    """Wialon API token name."""
    flags = models.PositiveIntegerField(
        default=settings.WIALON_TOKEN_ACCESS_TYPE
    )
    """Wialon token flags."""

    def __str__(self) -> str:
        """Returns '<customer email>'s WialonToken'."""
        return f"{self.customer}'s WialonToken"


class WialonNotification(models.Model):
    """Wialon notification."""

    class WialonNotificationMethod(models.TextChoices):
        """Wialon notification method."""

        SMS = "sms", _("SMS")
        VOICE = "voice", _("Voice")

    wialon_id = models.PositiveBigIntegerField()
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
    activation_time = models.DateTimeField(
        default=timezone.now,
        null=True,
        blank=True,
        help_text="Please provide a valid date and time in the format: YYYY-MM-DD HH:MM:SS.",
    )
    """Activation date/time."""
    deactivation_time = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text="Please provide a valid date and time in the format: YYYY-MM-DD HH:MM:SS. Leave this blank to never deactivate.",
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
        max_length=2, default="en", choices=[("en", _("English"))]
    )
    """2-letter language code."""
    flags = models.PositiveSmallIntegerField(
        default=0,
        choices=[
            (0, _("Trigger on first message")),
            (1, _("Trigger on every message")),
            (2, _("Disabled")),
        ],
    )
    """Notification flags."""

    class Meta:
        verbose_name = _("wialon notification")
        verbose_name_plural = _("wialon notifications")

    def __str__(self) -> str:
        """Returns the notification name."""
        return str(self.name)

    def get_action(self) -> dict[str, typing.Any]:
        """Returns the notification action."""
        return {
            "act": {
                "t": "push_messages",
                "p": {
                    "url": urllib.parse.urljoin(
                        "https://api.terminusgps.com/",
                        f"/v3/notify/{self.method}/",
                    ),
                    "get": 1,  # 1 - GET request, 2 - POST request
                },
            }
        }


class WialonNotificationTrigger(models.Model):
    """Wialon notification trigger."""

    type = models.CharField(
        max_length=64,
        choices=WialonNotificationTriggerType.choices,
        default=WialonNotificationTriggerType.SENSOR,
    )
    """Notification trigger type."""
    parameters = models.JSONField(default=dict)
    """Notification trigger parameters."""
