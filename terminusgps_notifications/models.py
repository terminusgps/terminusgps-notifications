from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from encrypted_field import EncryptedField
from terminusgps.authorizenet.constants import SubscriptionStatus
from terminusgps.wialon import flags
from terminusgps.wialon.session import WialonSession


class Customer(models.Model):
    """A Terminus GPS Notifications customer."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """Django user."""
    tax_rate = models.DecimalField(
        max_digits=9, decimal_places=4, default=0.0825
    )
    """Tax rate."""
    wialon_resource_id = models.PositiveIntegerField(null=True, blank=True)
    """Wialon resource id."""

    subscription = models.ForeignKey(
        "terminusgps_payments.Subscription",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    """Notifications subscription."""
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

    def save(self, **kwargs) -> None:
        if not self.wialon_resource_id and self.wialon_token is not None:
            # TODO: Retrieve resource_name from somewhere else (settings?)
            resource_name: str = "Terminus GPS Notifications"
            resource_id: int = self._get_wialon_resource_id(resource_name)
            self.wialon_resource_id = resource_id
        return super().save(**kwargs)

    def _get_wialon_resource_id(self, resource_name: str) -> int:
        """Retrieves or creates a Wialon resource by name."""
        with WialonSession(token=self.wialon_token.name) as session:
            wialon_response = session.wialon_api.core_search_items(
                **{
                    "spec": {
                        "itemsType": "avl_resource",
                        "propName": "sys_name",
                        "propValueMask": resource_name,
                        "sortType": "sys_name",
                        "propType": "property",
                    },
                    "force": 0,
                    "flags": flags.DataFlag.RESOURCE_BASE,
                    "from": 0,
                    "to": 0,
                }
            )
            if int(wialon_response.get("totalItemsCount", 0)) == 1:
                resource = wialon_response.get("items")[0]
            else:
                wialon_response = session.wialon_api.core_create_resource(
                    **{
                        "creatorId": session.uid,
                        "name": resource_name,
                        "dataFlags": flags.DataFlag.RESOURCE_BASE,
                        "skipCreatorCheck": True,
                    }
                )
                resource = wialon_response.get("item")
            return int(resource.get("id"))

    @property
    def is_subscribed(self) -> bool:
        """Whether the customer is subscribed."""
        return (
            self.subscription.status == SubscriptionStatus.ACTIVE
            if self.subscription is not None
            else False
        )


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
        ordering = ["-date_updated"]

    def __str__(self) -> str:
        return f"WialonToken #{self.pk}"

    @transaction.atomic
    def refresh(self, duration: int = 2_592_000) -> None:
        """
        Refreshes the Wialon API token.

        :param duration: Token lifetime duration in seconds. Default is ``2_592_000`` (30 days).
        :type days: int
        :returns: Nothing.
        :rtype: None

        """
        with WialonSession(token=settings.WIALON_TOKEN) as session:
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
