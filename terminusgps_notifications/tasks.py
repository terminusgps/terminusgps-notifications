from collections.abc import Sequence
from typing import Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import F
from django.template.loader import render_to_string
from django_tasks import task

from terminusgps_notifications.models import (
    MessagePackage,
    TerminusgpsNotificationsCustomer,
)


@task
def send_email(
    to: Sequence[str],
    subject: str,
    template_name: str,
    reply_to: Sequence[str] = ("support@terminusgps.com",),
    from_email: str = "noreply@terminusgps.com",
    bcc: Sequence[str] | None = None,
    cc: Sequence[str] | None = None,
    context: dict[str, Any] | None = None,
    html_template_name: str | None = None,
) -> bool:
    """
    Sends an email to target addresses.

    :param to: Sequence of destination email addresses.
    :type to: ~collections.abc.Sequence[str]
    :param subject: Subject line.
    :type subject: str
    :param template_name: Email template name.
    :type template_name: str
    :param reply_to: Reply-to email address. Default is ``("support@terminusgps.com",)``.
    :type reply_to: str
    :param from_email: Origin email address. Default is :py:obj:`None`
    :type from_email: str | None
    :param cc: Sequence of closed-copy email addresses.
    :type cc: ~collections.abc.Sequence[str] | None
    :param bcc: Sequence of blind closed-copy email addresses.
    :type bcc: ~collections.abc.Sequence[str] | None
    :param context: Email context. Default is :py:obj:`None`.
    :type context: dict[str, ~typing.Any] | None
    :param html_template_name: Email HTML template name. If provided, attaches HTML alternative to the email. Default is :py:obj:`None`.
    :type html_template_name: str | None

    """
    msg = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string(template_name, context=context),
        from_email=from_email,
        to=to,
        cc=cc if cc else [],
        bcc=bcc if bcc else [admin[1] for admin in settings.ADMINS],
        reply_to=reply_to,
    )
    if html_template_name is not None:
        html_content = render_to_string(html_template_name, context=context)
        msg.attach_alternative(html_content, "text/html")
    return bool(msg.send(fail_silently=True))


@task
def reset_customer_messages(customer_pk: int) -> None:
    """
    Sets the customer's :py:attr:`messages_count` to 0.

    :param customer_pk: Customer primary key.
    :type customer_pk: int
    :returns: Nothing.
    :rtype: None

    """
    try:
        customer = TerminusgpsNotificationsCustomer.objects.get(pk=customer_pk)
        customer.messages_count = 0
        customer.save(update_fields=["messages_count"])
    except TerminusgpsNotificationsCustomer.DoesNotExist:
        return


@task
def reset_customer_packages(customer_pk: int) -> None:
    """
    Deletes fully used customer packages.

    :param customer_pk: Customer primary key.
    :type customer_pk: int
    :returns: Nothing.
    :rtype: None

    """
    packages = MessagePackage.objects.filter(customer__pk=customer_pk)
    packages.filter(count__gte=F("max")).delete()
