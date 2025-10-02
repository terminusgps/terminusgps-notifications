import typing
import urllib.parse
from functools import lru_cache

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_notifications.models import Customer, WialonToken


class HomeView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Home",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_notifications/partials/_home.html"
    template_name = "terminusgps_notifications/home.html"


class DashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Dashboard"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/partials/_dashboard.html"
    )
    template_name = "terminusgps_notifications/dashboard.html"


class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Account"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_notifications/partials/_account.html"
    template_name = "terminusgps_notifications/account.html"

    @staticmethod
    @lru_cache(maxsize=3, typed=True)
    def generate_wialon_login_params(
        customer: Customer,
        activation_time: int = 0,
        token_lifetime: int = 2_592_000,
    ) -> dict[str, typing.Any]:
        """
        Returns a dictionary of Wialon login parameters for Terminus GPS Notifications.

        :param customer: A customer.
        :type customer: ~terminusgps_notifications.Customer
        :param activation_time: Token activation time in UNIX-timestamp format. Default is ``0`` (now).
        :type activation_time: int
        :param token_lifetime: How long (in seconds) the token will live for. Default is ``2_592_000`` (30 days).
        :returns: A dictionary of Wialon login parameters.
        :rtype: dict[str, ~typing.Any]

        """
        return {
            "client_id": "Terminus GPS Notifications",
            "access_type": settings.WIALON_TOKEN_ACCESS_TYPE,
            "activation_time": activation_time,
            "duration": token_lifetime,
            "lang": "en",
            "flags": 0x1,
            "response_type": "token",
            "user": customer.user.username,
            "redirect_uri": urllib.parse.urljoin(
                "http://localhost:8000/"
                if settings.DEBUG
                else "https://app.terminusgps.com/n/",
                reverse("terminusgps_notifications:wialon callback"),
            ),
        }

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer = Customer.objects.get(user=self.request.user)
        login_params = self.generate_wialon_login_params(customer)
        context["login_params"] = urllib.parse.urlencode(login_params)
        context["wialon_token"] = customer.wialon_token
        return context


class SubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Subscription"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/partials/_subscription.html"
    )
    template_name = "terminusgps_notifications/subscription.html"


class NotificationsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Notifications"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/partials/_notifications.html"
    )
    template_name = "terminusgps_notifications/notifications.html"


class WialonLoginView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, RedirectView
):
    permanent = True
    query_string = True
    url = "https://hosting.terminusgps.com/login.html"


class WialonCallbackView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Logged Into Wialon"}
    partial_template_name = (
        "terminusgps_notifications/partials/_wialon_callback.html"
    )
    template_name = "terminusgps_notifications/wialon_callback.html"

    @transaction.atomic
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if username := request.GET.get("user"):
            if (
                request.user.is_authenticated
                and request.user.username == username
            ):
                token = WialonToken(name=request.GET.get("access_token"))
                token.save()
                customer = Customer.objects.get(user__username=username)
                customer.wialon_token = token
                customer.save()
        return super().get(request, *args, **kwargs)
