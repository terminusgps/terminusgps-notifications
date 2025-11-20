from collections.abc import Sequence
from typing import Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django_tasks import task


@task
def send_email(
    to: Sequence[str],
    subject: str,
    template_name: str,
    reply_to: Sequence[str] = ("support@terminusgps.com",),
    from_email: str | None = None,
    context: dict[str, Any] | None = None,
    html_template_name: str | None = None,
) -> bool:
    """
    Constructs and sends an email to target email addresses.

    :param to: Required. A sequence of destination email addresses.
    :type to: ~collections.abc.Sequence[str]
    :param subject: Required. Email subject line.
    :type subject: str
    :param template_name: Required. Email message template name.
    :type template_name: str
    :param reply_to: Optional. Reply-to email address. Default is ``"support@terminusgps.com"``.
    :type reply_to: str
    :param from_email: Optional. Origin email address. Default is :py:obj:`None`
    :type from_email: str | None
    :param context: Optional. Email context dictionary for template rendering. Default is :py:obj:`None`.
    :type context: dict[str, ~typing.Any] | None
    :param html_template_name: Optional. Email HTML template name. If provided, attaches HTML alternative to the email. Default is :py:obj:`None`.
    :type html_template_name: str | None

    """
    msg = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string(template_name, context=context),
        from_email=from_email,
        to=to,
        bcc=[admin[1] for admin in settings.ADMINS],
        reply_to=reply_to,
    )
    if html_template_name is not None:
        html_content = render_to_string(html_template_name, context=context)
        msg.attach_alternative(html_content, "text/html")
    return bool(msg.send(fail_silently=True))
