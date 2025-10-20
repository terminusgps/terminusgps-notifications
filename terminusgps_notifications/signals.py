import logging

from terminusgps.wialon.session import WialonAPIError, WialonSession

from . import services

logger = logging.getLogger(__name__)


def create_notification_resource_in_wialon(sender, **kwargs):
    if customer := kwargs.get("instance"):
        if not customer.resource_id and hasattr(customer, "token"):
            token = getattr(customer, "token").name
            with WialonSession(token=token) as session:
                try:
                    logging.debug(
                        f"Searching Wialon for notification resource on behalf of '{customer}'..."
                    )
                    results = services.search_wialon_for_notification_resource(
                        session
                    )
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
                        response = (
                            services.create_wialon_notification_resource(
                                session
                            )
                        )
                        customer.resource_id = int(response["item"]["id"])
                        logging.debug(
                            f"Created notification resource for '{customer}': '{customer.resource_id}'"
                        )
                    customer.save(update_fields=["resource_id"])
                except WialonAPIError as e:
                    logger.warning(e)
