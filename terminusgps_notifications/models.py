import logging
import typing
import urllib.parse
from collections.abc import Collection

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.db.models import F
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from encrypted_field import EncryptedField
from terminusgps.wialon import flags
from terminusgps.wialon.session import WialonAPIError, WialonSession

from terminusgps_notifications.constants import (
    WialonNotificationTriggerType,
    WialonNotificationUpdateCallModeType,
)

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
        """Returns the customer user's username."""
        return str(self.user.username)

    def get_unit_groups_from_wialon(
        self,
        resource_id: str | int,
        session: WialonSession,
        force: bool = False,
    ) -> list[dict[str, typing.Any]]:
        """
        Returns a list of of customer Wialon unit group dictionaries from the Wialon API.

        Wialon unit group dictionary format:

        +------------+---------------+---------------------------------+
        | key        | type          | desc                            |
        +============+===============+=================================+
        | ``"mu"``   | :py:obj:`int` | Measurement system              |
        +------------+---------------+---------------------------------+
        | ``"nm"``   | :py:obj:`str` | Unit group name                 |
        +------------+---------------+---------------------------------+
        | ``"cls"``  | :py:obj:`int` | Superclass ID: 'avl_unit_group' |
        +------------+---------------+---------------------------------+
        | ``"id"``   | :py:obj:`int` | Unit group ID                   |
        +------------+---------------+---------------------------------+
        | ``"uacl"`` | :py:obj:`int` | User's access rights            |
        +------------+---------------+---------------------------------+

        :param force: Whether to force a Wialon API call instead of using a cached response. Default is :py:obj:`False` (use cache).
        :type force: bool
        :raises ValueError: If ``resource_id`` was a string and contained non-digit characters.
        :returns: A list of Wialon unit group dictionaries.
        :rtype: list[dict[str, ~typing.Any]]

        """
        if isinstance(resource_id, str) and not resource_id.isdigit():
            raise ValueError(
                f"resource_id can only contain digits, got '{resource_id}'."
            )
        return session.wialon_api.core_search_items(
            **{
                "spec": {
                    "itemsType": "avl_unit_group",
                    "propName": "sys_billing_account_guid,sys_name",
                    "propValueMask": f"{resource_id},*",
                    "sortType": "sys_name",
                    "propType": "property,property",
                },
                "force": int(force),
                "flags": flags.DataFlag.UNIT_BASE,
                "from": 0,
                "to": 0,
            }
        ).get("items", [])

    def get_units_from_wialon(
        self,
        resource_id: str | int,
        session: WialonSession,
        items_type: str = "avl_unit",
        force: bool = False,
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
        :raises ValueError: If ``resource_id`` was a string and contained non-digit characters.
        :returns: A list of Wialon unit dictionaries.
        :rtype: list[dict[str, ~typing.Any]]

        """
        if isinstance(resource_id, str) and not resource_id.isdigit():
            raise ValueError(
                f"resource_id can only contain digits, got '{resource_id}'."
            )
        return session.wialon_api.core_search_items(
            **{
                "spec": {
                    "itemsType": items_type,
                    "propName": "sys_billing_account_guid,sys_name",
                    "propValueMask": f"{resource_id},*",
                    "sortType": "sys_name",
                    "propType": "property,property",
                },
                "force": int(force),
                "flags": flags.DataFlag.UNIT_BASE,
                "from": 0,
                "to": 0,
            }
        ).get("items", [])

    def get_resources_from_wialon(
        self, session: WialonSession, force: bool = False
    ) -> list[dict[str, typing.Any]]:
        """
        Returns a list of of customer Wialon resource dictionaries from the Wialon API.

        Wialon resource dictionary format:

        +------------+---------------+-------------------------------+
        | key        | type          | desc                          |
        +============+===============+===============================+
        | ``"mu"``   | :py:obj:`int` | Measurement system            |
        +------------+---------------+-------------------------------+
        | ``"nm"``   | :py:obj:`str` | Resource name                 |
        +------------+---------------+-------------------------------+
        | ``"cls"``  | :py:obj:`int` | Superclass ID: 'avl_resource' |
        +------------+---------------+-------------------------------+
        | ``"id"``   | :py:obj:`int` | Resource ID                   |
        +------------+---------------+-------------------------------+
        | ``"uacl"`` | :py:obj:`int` | User's access rights          |
        +------------+---------------+-------------------------------+

        :param force: Whether to force a Wialon API call instead of using a cached response. Default is :py:obj:`False` (use cache).
        :type force: bool
        :returns: A list of Wialon resource dictionaries.
        :rtype: list[dict[str, ~typing.Any]]

        """
        return session.wialon_api.core_search_items(
            **{
                "spec": {
                    "itemsType": "avl_resource",
                    "propName": "sys_name",
                    "propValueMask": "*",
                    "sortType": "sys_name",
                    "propType": "property",
                },
                "force": int(force),
                "flags": flags.DataFlag.RESOURCE_BASE,
                "from": 0,
                "to": 0,
            }
        ).get("items", [])

    def get_notifications_from_wialon(
        self,
        resource_id: str | int,
        session: WialonSession,
        notification_ids: Collection[int] | None = None,
    ) -> list[dict[str, typing.Any]]:
        """
        Returns a list of notification dictionaries from the Wialon API.

        Wialon notification dictionary format:

        +----------------+----------------+-----------------------------------------------+
        | key            | type           | desc                                          |
        +================+================+===============================================+
        | ``"id"``       | :py:obj:`int`  | Notification ID                               |
        +----------------+----------------+-----------------------------------------------+
        | ``"n"``        | :py:obj:`str`  | Notification name                             |
        +----------------+----------------+-----------------------------------------------+
        | ``"txt"``      | :py:obj:`int`  | Notification text                             |
        +----------------+----------------+-----------------------------------------------+
        | ``"ta"``       | :py:obj:`int`  | Activation time (UNIX timestamp)              |
        +----------------+----------------+-----------------------------------------------+
        | ``"td"``       | :py:obj:`int`  | Deactivation time (UNIX timestamp)            |
        +----------------+----------------+-----------------------------------------------+
        | ``"ma"``       | :py:obj:`int`  | Maximum number of alarms (0 = unlimited)      |
        +----------------+----------------+-----------------------------------------------+
        | ``"mmtd"``     | :py:obj:`int`  | Maximum time interval between messages (sec)  |
        +----------------+----------------+-----------------------------------------------+
        | ``"cdt"``      | :py:obj:`int`  | Alarm timeout (sec)                           |
        +----------------+----------------+-----------------------------------------------+
        | ``"mast"``     | :py:obj:`int`  | Minimum duration of the alarm state (sec)     |
        +----------------+----------------+-----------------------------------------------+
        | ``"mpst"``     | :py:obj:`int`  | Minimum duration of previous state (sec)      |
        +----------------+----------------+-----------------------------------------------+
        | ``"cp"``       | :py:obj:`int`  | Control period relative to current time (sec) |
        +----------------+----------------+-----------------------------------------------+
        | ``"fl"``       | :py:obj:`int`  | Notification flags                            |
        +----------------+----------------+-----------------------------------------------+
        | ``"tz"``       | :py:obj:`int`  | Notification timezone                         |
        +----------------+----------------+-----------------------------------------------+
        | ``"la"``       | :py:obj:`str`  | Notification language code                    |
        +----------------+----------------+-----------------------------------------------+
        | ``"ac"``       | :py:obj:`int`  | Alarms count                                  |
        +----------------+----------------+-----------------------------------------------+
        | ``"d"``        | :py:obj:`str`  | Notification description                      |
        +----------------+----------------+-----------------------------------------------+
        | ``"sch"``      | :py:obj:`dict` | Notification schedule (see below)             |
        +----------------+----------------+-----------------------------------------------+
        | ``"ctrl_sch"`` | :py:obj:`dict` | Notification control schedule (see below)     |
        +----------------+----------------+-----------------------------------------------+
        | ``"un"``       | :py:obj:`list` | List of unit/unit group IDs                   |
        +----------------+----------------+-----------------------------------------------+
        | ``"act"``      | :py:obj:`list` | List of notification actions (see below)      |
        +----------------+----------------+-----------------------------------------------+
        | ``"trg"``      | :py:obj:`dict` | Notification trigger (see below)              |
        +----------------+----------------+-----------------------------------------------+
        | ``"ct"``       | :py:obj:`int`  | Creation time (UNIX timestamp)                |
        +----------------+----------------+-----------------------------------------------+
        | ``"mt"``       | :py:obj:`int`  | Last modification time (UNIX timestamp)       |
        +----------------+----------------+-----------------------------------------------+

        Notification schedule/control schedule format:

        +----------+----------------+------------------------------------------------------------------+
        | key      | type           | desc                                                             |
        +==========+================+==================================================================+
        | ``"f1"`` | :py:obj:`int`  | Beginning of interval 1 (minutes from midnight)                  |
        +----------+----------------+------------------------------------------------------------------+
        | ``"f2"`` | :py:obj:`int`  | Beginning of interval 2 (minutes from midnight)                  |
        +----------+----------------+------------------------------------------------------------------+
        | ``"t1"`` | :py:obj:`int`  | End of interval 1 (minutes from midnight)                        |
        +----------+----------------+------------------------------------------------------------------+
        | ``"t2"`` | :py:obj:`int`  | End of interval 2 (minutes from midnight)                        |
        +----------+----------------+------------------------------------------------------------------+
        | ``"m"``  | :py:obj:`int`  | Mask of the days of the month (1: 2:\ sup:`0`, 31: 2\ :sup:`30`) |
        +----------+----------------+------------------------------------------------------------------+
        | ``"y"``  | :py:obj:`int`  | Mask of months (Jan: 2\ :sup:`0`, Dec: 2:\ sup:`11`)             |
        +----------+----------------+------------------------------------------------------------------+
        | ``"w"``  | :py:obj:`int`  | Mask of days of the week (Mon: 2\ :sup:`0`, Sun: 2\ :sup:`6`)    |
        +----------+----------------+------------------------------------------------------------------+
        | ``"f"``  | :py:obj:`int`  | Schedule flags                                                   |
        +----------+----------------+------------------------------------------------------------------+

        Notification `action <https://wialon-help.link/bb04a9a5>`_ format (each item in the ``act`` list):

        +----------+-----------------+-------------------+
        | key      | type            | desc              |
        +==========+=================+===================+
        | ``"t"``  | :py:obj:`str`   | Action type       |
        +----------+-----------------+-------------------+
        | ``"p"``  | :py:obj:`dict`  | Action parameters |
        +----------+-----------------+-------------------+

        Notification `trigger <https://wialon-help.link/9d54585d>`_ format:

        +----------+-----------------+--------------------+
        | key      | type            | desc               |
        +==========+=================+====================+
        | ``"t"``  | :py:obj:`str`   | Trigger type       |
        +----------+-----------------+--------------------+
        | ``"p"``  | :py:obj:`dict`  | Trigger parameters |
        +----------+-----------------+--------------------+

        :param resource_id: A Wialon resource id.
        :type resource_id: str | int
        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param notification_ids: Optional. A list of notification ids.
        :type notification_ids: ~collections.abc.Collection[int] | None
        :raises ValueError: If ``resource_id`` was a string containing non-digit characters.
        :returns: A list of Wialon notification dictionaries.
        :rtype: list[dict[str, ~typing.Any]]

        """
        if isinstance(resource_id, str) and not resource_id.isdigit():
            raise ValueError(
                f"resource_id can only contain digits, got '{resource_id}'."
            )
        params = {"itemId": resource_id}
        if notification_ids is not None:
            params["col"] = notification_ids
        return session.wialon_api.resource_get_notification_data(**params)


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
    unit_list = models.JSONField(blank=True, default=list)
    """List of Wialon units."""
    trigger_type = models.CharField(
        choices=WialonNotificationTriggerType.choices,
        default=WialonNotificationTriggerType.SENSOR,
    )
    """Trigger type."""
    trigger_parameters = models.JSONField(blank=True, default=dict)
    """Trigger parameters."""
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
    date_created = models.DateTimeField(auto_now_add=True)
    """Date created."""

    wialon_id = models.PositiveBigIntegerField()
    """Wialon id."""
    resource_id = models.PositiveBigIntegerField()
    """Resource id."""
    customer = models.ForeignKey(
        "terminusgps_notifications.TerminusgpsNotificationsCustomer",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    """Associated customer."""

    class Meta:
        verbose_name = _("wialon notification")
        verbose_name_plural = _("wialon notifications")

    def __str__(self) -> str:
        """Returns the notification name."""
        return str(self.name)

    @transaction.atomic
    def save(self, **kwargs) -> None:
        """Sets :py:attr:`text` and :py:attr:`actions` before saving."""
        update_fields = kwargs.get("update_fields", [])
        if not self.text or "message" in update_fields:
            self.text = self.get_text()
        if not self.actions or "method" in update_fields:
            self.actions = self.get_actions()
        return super().save(**kwargs)

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
                    "get": 1,  # 1 = GET request, 2 = POST request
                },
            }
        ]

    def update_in_wialon(
        self,
        call_mode: WialonNotificationUpdateCallModeType,
        session: WialonSession,
    ) -> dict[str, typing.Any]:
        """
        Updates the notification in Wialon.

        :param call_mode: Call mode to use when calling ``resource/update_notification``.
        :type call_mode: ~terminusgps_notifications.constants.WialonNotificationUpdateCallMode
        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :raises WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary of notification data.
        :rtype: dict[str, ~typing.Any]

        """
        try:
            params = self.get_wialon_parameters(call_mode=call_mode)
            return session.wialon_api.resource_update_notification(**params)
        except WialonAPIError:
            raise

    def get_wialon_parameters(self, call_mode: str) -> dict[str, typing.Any]:
        """
        Returns parameters for Wialon notification API calls.

        :param call_mode: A Wialon API update notification call mode.
        :type call_mode: str
        :returns: A dictionary of Wialon API update notification parameters.
        :rtype: dict[str, ~typing.Any]

        """
        return {
            "itemId": self.resource_id,
            "id": 0 if call_mode == "create" else self.wialon_id,
            "callMode": call_mode,
            "n": self.name,
            "txt": self.text,
            "ta": self.activation_time.timestamp()
            if self.activation_time is not None
            else 0,
            "td": self.deactivation_time.timestamp()
            if self.deactivation_time is not None
            else 0,
            "ma": self.max_alarms,
            "mmtd": self.max_message_interval,
            "cdt": self.alarm_timeout,
            "mast": self.min_duration_alarm,
            "mpst": self.min_duration_prev,
            "cp": self.control_period,
            "fl": self.flags,
            "la": self.language,
            "tz": self.timezone,
            "un": self.unit_list,
            "trg": {"t": self.trigger_type, "p": self.trigger_parameters},
            "act": self.actions,
            "sch": self.schedule,
            "ctrl_sch": self.control_schedule,
        }
