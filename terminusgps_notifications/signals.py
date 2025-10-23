import logging

from terminusgps.wialon.session import WialonAPIError, WialonSession

from . import services

logger = logging.getLogger(__name__)


def create_notification_resource_in_wialon(sender, **kwargs):
    if customer := kwargs.get("instance"):
        if not customer.resource_id and hasattr(customer, "token"):
            token = getattr(customer, "token").name
            try:
                with WialonSession(token=token) as session:
                    results = services.search_wialon_for_notification_resource(
                        session
                    )
                    if results["totalItemsCount"] > 0:
                        customer.resource_id = int(results["items"][0]["id"])
                    else:
                        response = (
                            services.create_wialon_notification_resource(
                                session
                            )
                        )
                        customer.resource_id = int(response["item"]["id"])
                    customer.save(update_fields=["resource_id"])
            except WialonAPIError as e:
                logger.critical(e)
