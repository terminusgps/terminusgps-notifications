import ast
import logging
import typing
import urllib.parse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinLengthValidator
from django.db import models, transaction
from django.db.models import F
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from encrypted_field import EncryptedField
from terminusgps.validators import validate_is_digit
from terminusgps.wialon import flags
from terminusgps.wialon.session import WialonAPIError, WialonSession

logger = logging.getLogger(__name__)


class TerminusgpsNotificationsCustomer(models.Model):
    """A Terminus GPS Notifications customer."""

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="terminusgps_notifications_customer",
    )
    """Django user."""
    company = models.CharField(
        max_length=64, null=True, blank=True, default=None
    )
    """Company name."""
    date_format = models.CharField(
        choices=[
            ("%Y-%m-%d %H:%M:%S", "YYYY-MM-DD HH:MM:SS"),
            ("%Y-%m-%d %H:%M", "YYYY-MM-DD HH:MM"),
        ],
        default="%Y-%m-%d %H:%M:%S",
        help_text="Select a date format for notification messages.",
        max_length=24,
    )
    """Date format for notifications."""
    resource_id = models.CharField(
        blank=True,
        default=None,
        help_text="Enter an 8-digit Wialon resource id to create notifications in.",
        max_length=8,
        null=True,
        validators=[validate_is_digit, MinLengthValidator(8)],
    )
    """Wialon resource id."""
    max_sms_count = models.PositiveIntegerField(
        default=500,
        help_text="Enter the maximum number of allowed sms messages in a single period.",
    )
    """Maximum number of allowed sms messages for the period."""
    max_voice_count = models.PositiveIntegerField(
        default=500,
        help_text="Enter the maximum number of allowed voice messages in a single period.",
    )
    """Maximum number of allowed voice messages for the period."""
    sms_count = models.PositiveIntegerField(default=0)
    """Current number of sms messages for the period."""
    voice_count = models.PositiveIntegerField(default=0)
    """Current number of voice messages for the period."""

    tax_rate = models.DecimalField(
        max_digits=9,
        decimal_places=4,
        default=0.0825,
        help_text="Enter a tax rate as a decimal.",
    )
    """Subscription tax rate."""
    subtotal = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=64.99,
        help_text="Enter a dollar amount to charge the customer (not incl. tax) every period.",
    )
    """Subscription subtotal."""
    tax = models.GeneratedField(
        expression=(F("subtotal") * (F("tax_rate") + 1)) - F("subtotal"),
        output_field=models.DecimalField(max_digits=9, decimal_places=2),
        db_persist=True,
        help_text="Automatically generated tax amount.",
    )
    """Subscription tax total."""
    grand_total = models.GeneratedField(
        expression=F("subtotal") * (F("tax_rate") + 1),
        output_field=models.DecimalField(max_digits=9, decimal_places=2),
        db_persist=True,
        help_text="Automatically generated grand total amount (subtotal+tax).",
    )
    """Subscription grand total (subtotal + tax)."""

    subscription = models.ForeignKey(
        "terminusgps_payments.Subscription",
        on_delete=models.SET_NULL,
        related_name="terminusgps_notifications_customer",
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

        :param force: Whether to force a Wialon API call instead of using a cached response. Default is :py:obj:`False` (use cache).
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
        "terminusgps_notifications.TerminusgpsNotificationsCustomer",
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

    name = models.CharField(
        max_length=64, help_text="Provide a memorable name."
    )
    """Notification name."""
    message = models.CharField(max_length=1024, help_text="Enter a message.")
    """Notification message."""
    method = models.CharField(
        choices=WialonNotificationMethod.choices,
        default=WialonNotificationMethod.SMS,
        help_text="Select a delivery method.",
        max_length=5,
    )
    """Notification method."""

    activation_time = models.DateTimeField(
        blank=True,
        default=None,
        help_text="Provide a valid date and time in the format: YYYY-MM-DD HH:MM:SS. Leave this blank to activate immediately.",
        null=True,
    )
    """Activation date/time."""
    deactivation_time = models.DateTimeField(
        blank=True,
        default=None,
        help_text="Provide a valid date and time in the format: YYYY-MM-DD HH:MM:SS. Leave this blank to never deactivate.",
        null=True,
    )
    """Deactivation date/time."""
    max_alarms = models.PositiveIntegerField(
        default=0,
        help_text="Provide the maximum number of alarms. 0 = unlimited alarms.",
    )
    """Maximum number of alarms (0 = unlimited)."""
    max_message_interval = models.PositiveIntegerField(
        default=3600,
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
        help_text="Select the maximum allowed time between messages.",
    )
    """Max time interval between messages."""
    alarm_timeout = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(1800)],
        help_text="Provide the alarm timeout in seconds. 0 = never timeout.",
    )
    """Alarm timeout in seconds. Max is ``1800`` (30 minutes in seconds)."""
    control_period = models.PositiveIntegerField(
        default=3600,
        choices=[
            (0, _("Any time")),
            (60, _("Last minute")),
            (600, _("Last 10 minutes")),
            (3600, _("Last hour")),
            (86400, _("Last day")),
        ],
        help_text="Select a control period relative to current time.",
    )
    """Control period relative to current time in seconds."""
    min_duration_alarm = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(86400)],
        help_text="Provide the minimum duration of alarm state in seconds.",
    )
    """Minimum duration of alarm state in seconds. Max is ``86400`` (1 day)."""
    min_duration_prev = models.PositiveIntegerField(
        default=0, validators=[MaxValueValidator(86400)]
    )
    """Minimum duration of previous state in seconds. Max is ``86400`` (1 day)."""
    language = models.CharField(
        max_length=2,
        default="en",
        choices=[("en", _("English"))],
        help_text="Select a valid language.",
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
    """Flags."""

    timezone = models.IntegerField(default=0)
    """Timezone."""
    unit_list = models.CharField(blank=True, max_length=2048)
    """List of Wialon units."""
    trigger = models.JSONField(blank=True, default=dict)
    """Trigger."""
    schedule = models.JSONField(blank=True, default=dict)
    """Schedule."""
    control_schedule = models.JSONField(blank=True, default=dict)
    """Control schedule."""
    actions = models.JSONField(blank=True, default=dict)
    """Actions."""
    text = models.CharField(max_length=1024, blank=True)
    """Text."""
    enabled = models.BooleanField(default=True)
    """Whether the notification is enabled in Wialon."""

    wialon_id = models.PositiveBigIntegerField()
    """Wialon id."""
    customer = models.ForeignKey(
        "terminusgps_notifications.TerminusgpsNotificationsCustomer",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    """Associated customer."""
    date_created = models.DateTimeField(auto_now_add=True)
    """Date created."""

    class Meta:
        verbose_name = _("wialon notification")
        verbose_name_plural = _("wialon notifications")

    def __str__(self) -> str:
        """Returns the notification name."""
        return str(self.name)

    def get_absolute_url(self) -> str:
        return reverse(
            "terminusgps_notifications:detail notifications",
            kwargs={"notification_pk": self.pk},
        )

    def get_text(self) -> str:
        """Returns the notification text (txt)."""
        return urllib.parse.urlencode(
            {
                "unit_id": "%UNIT_ID%",
                "user_id": self.customer.user.pk,
                "message": self.message,
            }
        )

    def get_actions(self) -> list[dict[str, typing.Any]]:
        """Returns a list of notification actions (act)."""
        return [
            {
                "t": "push_messages",
                "p": {
                    "url": urllib.parse.urljoin(
                        "https://api.terminusgps.com/",
                        f"/v3/notify/{self.method}/",
                    ),
                    "get": 1,  # 1 - GET request, 2 - POST request
                },
            }
        ]

    @transaction.atomic
    def enable(self, session: WialonSession) -> None:
        """Enables the notification in Wialon."""
        try:
            if not self.enabled:
                session.wialon_api.resource_update_notification(
                    **{
                        "itemId": int(self.customer.resource_id),
                        "id": self.wialon_id,
                        "callMode": "enable",
                        "e": 1,
                    }
                )
                self.enabled = True
        except WialonAPIError as e:
            logger.critical(e)
            raise

    @transaction.atomic
    def disable(self, session: WialonSession) -> None:
        """Disables the notification in Wialon."""
        try:
            if self.enabled:
                session.wialon_api.resource_update_notification(
                    **{
                        "itemId": int(self.customer.resource_id),
                        "id": self.wialon_id,
                        "callMode": "enable",
                        "e": 0,
                    }
                )
                self.enabled = False
        except WialonAPIError as e:
            logger.critical(e)
            raise

    def get_wialon_parameters(self, call_mode: str) -> dict[str, typing.Any]:
        """Returns parameters for Wialon notification API calls."""
        allowed_call_modes: set[str] = {"create", "update", "delete"}
        if call_mode not in allowed_call_modes:
            raise ValueError(
                f"Invalid call_mode '{call_mode}'. Options are: {allowed_call_modes}"
            )
        return {
            "itemId": int(self.customer.resource_id),
            "id": 0 if call_mode == "create" else self.wialon_id,
            "callMode": call_mode,
            "n": self.name,
            "txt": self.text,
            "ta": self.activation_time if self.activation_time else 0,
            "td": self.deactivation_time if self.deactivation_time else 0,
            "ma": self.max_alarms,
            "mmtd": self.max_message_interval,
            "cdt": self.alarm_timeout,
            "mast": self.min_duration_alarm,
            "mpst": self.min_duration_prev,
            "cp": self.control_period,
            "fl": self.flags,
            "la": self.language,
            "tz": self.timezone,
            "un": ast.literal_eval(self.unit_list),
            "trg": self.trigger,
            "act": self.actions,
            "sch": self.schedule,
            "ctrl_sch": self.control_schedule,
        }

    def update_in_wialon(
        self, call_mode: str, session: WialonSession
    ) -> dict[str, typing.Any]:
        """Updates the notification in Wialon."""
        try:
            params = self.get_wialon_parameters(call_mode=call_mode)
            return session.wialon_api.resource_update_notification(**params)
        except WialonAPIError as e:
            logger.critical(e)
            raise
