import urllib.parse

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from terminusgps_payments.models import CustomerProfile

from terminusgps_notifications.models import (
    TerminusgpsNotificationsCustomer,
    WialonToken,
)


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
    try:
        if user.is_authenticated:
            return TerminusgpsNotificationsCustomer.objects.get(user=user)
    except TerminusgpsNotificationsCustomer.DoesNotExist:
        return


def get_customer_profile(user: AbstractBaseUser) -> CustomerProfile | None:
    """
    Returns the :py:obj:`~terminusgps_payments.models.CustomerProfile` for a user.

    :param user: A Django user.
    :type user: ~django.contrib.auth.models.AbstractBaseUser
    :returns: A customer profile object, if the user has one.
    :rtype: ~terminusgps_payments.models.CustomerProfile | None

    """
    try:
        if user.is_authenticated:
            return CustomerProfile.objects.get(user=user)
    except CustomerProfile.DoesNotExist:
        return


def get_wialon_token(user: AbstractBaseUser) -> str | None:
    """
    Returns the :py:obj:`~terminusgps_notifications.models.WialonToken` for a user.

    :param user: A Django user.
    :type user: ~django.contrib.auth.models.AbstractBaseUser
    :returns: A Wialon API token, if the user has one.
    :rtype: str | None

    """
    try:
        if user.is_authenticated:
            token = WialonToken.objects.get(customer__user=user)
            return getattr(token, "name", None)
    except WialonToken.DoesNotExist:
        return


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
            "redirect_uri": urllib.parse.urljoin(
                "https://api.terminusgps.com/"
                if not settings.DEBUG
                else "http://127.0.0.1:8000/",
                reverse("terminusgps_notifications:account"),
            ),
        }
    )
