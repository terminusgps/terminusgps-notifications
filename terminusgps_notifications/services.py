import typing

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from terminusgps.wialon.flags import DataFlag
from terminusgps.wialon.session import WialonSession

if settings.configured and not hasattr(settings, "WIALON_RESOURCE_NAME"):
    raise ImproperlyConfigured("'WIALON_RESOURCE_NAME' setting is required.")


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
