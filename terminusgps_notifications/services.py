import typing
from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from terminusgps.wialon.flags import DataFlag
from terminusgps.wialon.session import WialonSession
from terminusgps_payments.models import CustomerProfile

from terminusgps_notifications.models import (
    TerminusgpsNotificationsCustomer,
    WialonToken,
)

if settings.configured and not hasattr(settings, "WIALON_RESOURCE_NAME"):
    raise ImproperlyConfigured("'WIALON_RESOURCE_NAME' setting is required.")


def get_customer(
    user: AbstractBaseUser,
) -> TerminusgpsNotificationsCustomer | None:
    """
    Returns the :py:obj:`~terminusgps_notifications.models.TerminusgpsNotificationsCustomer` for a user.

    :param user: A Django user.
    :type user: ~django.contrib.auth.models.AbstractBaseUser
    :returns: A customer object, if the user has one.
    :rtype: ~terminusgps_notifications.models.TerminusgpsNotificationsCustomer | None

    """
    if hasattr(user, "terminusgps_notifications_customer"):
        return getattr(user, "terminusgps_notifications_customer")


def get_customer_profile(user: AbstractBaseUser) -> CustomerProfile | None:
    """
    Returns the :py:obj:`~terminusgps_payments.models.CustomerProfile` for a user.

    :param user: A Django user.
    :type user: ~django.contrib.auth.models.AbstractBaseUser
    :returns: A customer profile object, if the user has one.
    :rtype: ~terminusgps_payments.models.CustomerProfile | None

    """
    if hasattr(user, "customer_profile"):
        return getattr(user, "customer_profile")


def get_wialon_token(user: AbstractBaseUser) -> WialonToken | None:
    """
    Returns the :py:obj:`~terminusgps_notifications.models.WialonToken` for a user.

    :param user: A Django user.
    :type user: ~django.contrib.auth.models.AbstractBaseUser
    :returns: A Wialon API token, if the user has one.
    :rtype: ~terminusgps_notifications.models.WialonToken | None

    """
    customer = get_customer(user)
    if customer is not None and hasattr(customer, "token"):
        return getattr(customer, "token")


def get_wialon_redirect_uri() -> str:
    """Returns the redirect (callback) URI for Wialon authentication."""
    return urljoin(
        "https://api.terminusgps.com/"
        if not settings.DEBUG
        else "http://127.0.0.1:8000/",
        reverse("terminusgps_notifications:account"),
    )


def get_wialon_login_parameters(username: str) -> str:
    """
    Returns a query string of path parameters to be added to the Wialon authentication request.

    :param username: A username to autofill into the authentication form.
    :type username: str
    :returns: A query string.
    :rtype: str

    """
    return urlencode(
        {
            "client_id": "Terminus GPS Notifications",
            "access_type": settings.WIALON_TOKEN_ACCESS_TYPE,
            "activation_time": 0,
            "duration": 0,
            "lang": "en",
            "flags": 0x1,
            "user": username,
            "response_type": "token",
            "redirect_uri": get_wialon_redirect_uri(),
        }
    )


def search_wialon_for_notification_resource(
    session: WialonSession,
) -> dict[str, typing.Any]:
    """Searches the customer's Wialon database for notification resource."""
    return session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_resource",
                "propName": "sys_name",
                "propValueMask": settings.WIALON_RESOURCE_NAME,
                "sortType": "sys_name",
                "propType": "property",
            },
            "force": 0,
            "flags": DataFlag.RESOURCE_BASE,
            "from": 0,
            "to": 0,
        }
    )


def create_wialon_notification_resource(
    session: WialonSession,
) -> dict[str, typing.Any]:
    """Creates a notification resource in the customer's Wialon database."""
    return session.wialon_api.core_create_resource(
        **{
            "creatorId": session.uid,
            "name": settings.WIALON_RESOURCE_NAME,
            "dataFlags": DataFlag.RESOURCE_BASE,
            "skipCreatorCheck": int(True),
        }
    )
