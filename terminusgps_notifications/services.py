import typing
from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from terminusgps.wialon.flags import DataFlag
from terminusgps.wialon.session import WialonSession

if settings.configured and not hasattr(settings, "WIALON_RESOURCE_NAME"):
    raise ImproperlyConfigured("'WIALON_RESOURCE_NAME' setting is required.")


def get_wialon_login_parameters(username: str) -> str:
    return urlencode(
        {
            "client_id": "Terminus GPS Notifications",
            "access_type": settings.WIALON_TOKEN_ACCESS_TYPE,
            "activation_time": 0,
            "duration": 2_592_000,
            "lang": "en",
            "flags": 0x1,
            "user": username,
            "redirect_uri": urljoin(
                "https://api.terminusgps.com/v3/"
                if not settings.DEBUG
                else "http://127.0.0.1:8000/",
                reverse("terminusgps_notifications:account"),
            ),
            "response_type": "token",
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
