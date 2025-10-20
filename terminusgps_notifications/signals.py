import logging
import typing

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from terminusgps.wialon.flags import DataFlag
from terminusgps.wialon.session import WialonAPIError, WialonSession

logger = logging.getLogger(__name__)

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


def create_notification_resource_in_wialon(sender, **kwargs):
    if customer := kwargs.get("instance"):
        if not customer.resource_id and hasattr(customer, "token"):
            token = getattr(customer, "token").name
            with WialonSession(token=token) as session:
                try:
                    logging.debug(
                        f"Searching Wialon for notification resource on behalf of '{customer}'..."
                    )
                    results = search_wialon_for_notification_resource(session)
                    if results["totalItemsCount"] == 1:
                        customer.resource_id = int(results["items"][0]["id"])
                        logging.info(
                            f"Found existing notification resource for '{customer}': '{customer.resource_id}'"
                        )
                    else:
                        logging.debug(
                            f"No notification resource found for: '{customer}'..."
                        )
                        logging.info(
                            f"Creating notification resource on behalf of '{customer}'..."
                        )
                        response = create_wialon_notification_resource(session)
                        customer.resource_id = int(response["item"]["id"])
                        logging.debug(
                            f"Created notification resource for '{customer}': '{customer.resource_id}'"
                        )
                    customer.save(update_fields=["resource_id"])
                except WialonAPIError as e:
                    logger.warning(e)
