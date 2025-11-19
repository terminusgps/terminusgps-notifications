import urllib.parse

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from terminusgps_payments.models import CustomerProfile

from terminusgps_notifications.models import TerminusgpsNotificationsCustomer


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


def get_wialon_token(user: AbstractBaseUser) -> str | None:
    """
    Returns the :py:obj:`~terminusgps_notifications.models.WialonToken` for a user.

    :param user: A Django user.
    :type user: ~django.contrib.auth.models.AbstractBaseUser
    :returns: A Wialon API token, if the user has one.
    :rtype: str | None

    """
    customer = get_customer(user)
    if customer is not None and hasattr(customer, "token"):
        return getattr(customer, "token").name


def get_wialon_redirect_uri() -> str:
    """Returns the redirect (callback) URI for Wialon authentication."""
    return urllib.parse.urljoin(
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
    return urllib.parse.urlencode(
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
