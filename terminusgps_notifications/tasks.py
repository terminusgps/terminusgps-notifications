import logging
from typing import Any
from urllib.parse import urljoin

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.template.loader import render_to_string
from django.urls import reverse
from django_tasks import task
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps_payments.models import Subscription
from terminusgps_payments.services import AuthorizenetService

from terminusgps_notifications.models import (
    ExtensionPackage,
    TerminusgpsNotificationsCustomer,
)

logger = logging.getLogger(__name__)
BASE_URL = "https://api.terminusgps.com/"


@task
def send_email_registration_confirmation(
    email_addr: str, first_name: str | None = None
) -> bool:
    template_name: str = (
        "terminusgps_notifications/emails/registration_confirmation.txt"
    )
    html_template_name: str = (
        "terminusgps_notifications/emails/registration_confirmation.html"
    )
    subject: str = "Terminus GPS Notifications - Account Registered"
    context: dict[str, str | None] = {
        "first_name": first_name,
        "link_homepage": urljoin(
            BASE_URL, reverse("terminusgps_notifications:home")
        ),
        "link_dashboard": urljoin(
            BASE_URL, reverse("terminusgps_notifications:dashboard")
        ),
        "link_account": urljoin(
            BASE_URL, reverse("terminusgps_notifications:account")
        ),
        "link_subscription": urljoin(
            BASE_URL, reverse("terminusgps_notifications:subscription")
        ),
        "link_notifications": urljoin(
            BASE_URL, reverse("terminusgps_notifications:notifications")
        ),
    }
    text_content: str = render_to_string(template_name, context=context)
    html_content: str = render_to_string(html_template_name, context=context)
    msg: EmailMultiAlternatives = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[email_addr],
        bcc=[admin[1] for admin in settings.ADMINS],
    )
    msg.attach_alternative(html_content, "text/html")
    return bool(msg.send(fail_silently=True))


@task
def send_email_subscription_created(
    email_addr: str, first_name: str | None = None
) -> bool:
    template_name: str = (
        "terminusgps_notifications/emails/subscription_created.txt"
    )
    html_template_name: str = (
        "terminusgps_notifications/emails/subscription_created.html"
    )
    subject: str = "Terminus GPS Notifications - New Subscription"
    context: dict[str, Any] = {
        "first_name": first_name,
        "executions_max": 500,
        "link_homepage": urljoin(
            BASE_URL, reverse("terminusgps_notifications:home")
        ),
        "link_notifications": urljoin(
            BASE_URL, reverse("terminusgps_notifications:notifications")
        ),
    }
    text_content: str = render_to_string(template_name, context=context)
    html_content: str = render_to_string(html_template_name, context=context)
    msg: EmailMultiAlternatives = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[email_addr],
        bcc=[admin[1] for admin in settings.ADMINS],
    )
    msg.attach_alternative(html_content, "text/html")
    return bool(msg.send(fail_silently=True))


@task
def send_email_subscription_updated(email_addr: str) -> bool:
    template_name: str = (
        "terminusgps_notifications/emails/subscription_updated.txt"
    )
    html_template_name: str = (
        "terminusgps_notifications/emails/subscription_updated.html"
    )
    subject: str = "Terminus GPS Notifications - Updated Subscription"
    context: dict[str, Any] = {}
    text_content: str = render_to_string(template_name, context=context)
    html_content: str = render_to_string(html_template_name, context=context)
    msg: EmailMultiAlternatives = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[email_addr],
        bcc=[admin[1] for admin in settings.ADMINS],
    )
    msg.attach_alternative(html_content, "text/html")
    return bool(msg.send(fail_silently=True))


@task
def refresh_subscription_status(subscription_pk: int) -> str | None:
    """
    Refreshes and returns a subscription status from Authorizenet by pk.

    Returns :py:obj:`None` if the pk didn't point to a subscription.

    :param subscription_pk: A subscription primary key.
    :type subscription_pk: int
    :returns: The current subscription status from Authorizenet, if the subscription exists.
    :rtype: str | None

    """
    try:
        subscription = Subscription.objects.get(pk=subscription_pk)
        service = AuthorizenetService()
        new_status = str(service.get_subscription_status(subscription).status)
        subscription.status = new_status
        subscription.save(update_fields=["status"])
        return new_status
    except (
        Subscription.DoesNotExist,
        AuthorizenetControllerExecutionError,
    ) as e:
        logger.warning(e)


@task
def reset_executions_count(customer_pk: int) -> None:
    """
    Sets a customer's executions count to 0.

    :param customer_pk: A customer primary key.
    :type customer_pk: int
    :returns: Nothing.
    :rtype: None

    """
    try:
        customer = TerminusgpsNotificationsCustomer.objects.get(pk=customer_pk)
        customer.executions_count = 0
        customer.save(update_fields=["executions_count"])
    except TerminusgpsNotificationsCustomer.DoesNotExist as e:
        logger.critical(e)


@task
def reset_executions_max(customer_pk: int) -> None:
    """
    Recalculates and resets a customer's maximum executions.

    :param customer_pk: A customer primary key.
    :type customer_pk: int
    :returns: Nothing.
    :rtype: None

    """
    try:
        customer = TerminusgpsNotificationsCustomer.objects.get(pk=customer_pk)
        packages = ExtensionPackage.objects.filter(customer=customer)
        customer.executions_max = (
            packages.aggregate(Sum("executions")).get("executions__sum")
            if packages.exists()
            else customer.executions_max_base
        )
        customer.save(update_fields=["executions_max"])
    except TerminusgpsNotificationsCustomer.DoesNotExist as e:
        logger.critical(e)


@task
def reset_subtotal(customer_pk: int) -> None:
    """
    Recalculates and resets a customer's subtotal.

    :param customer_pk: A customer primary key.
    :type customer_pk: int
    :returns: Nothing.
    :rtype: None

    """
    try:
        customer = TerminusgpsNotificationsCustomer.objects.get(pk=customer_pk)
        packages = ExtensionPackage.objects.filter(customer=customer)
        customer.subtotal = (
            packages.aggregate(Sum("price")).get("price__sum")
            if packages.exists()
            else customer.subtotal_base
        )
        customer.save(update_fields=["subtotal"])
    except TerminusgpsNotificationsCustomer.DoesNotExist as e:
        logger.critical(e)
