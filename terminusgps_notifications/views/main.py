import typing
import urllib.parse

from django.contrib.auth.mixins import LoginRequiredMixin
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
    def generate_wialon_login_params(
        customer: Customer,
        client_id: str = "Terminus GPS Notifications",
        access_type: int = -1,
        activation_time: int = 0,
        duration: int = 2_592_000,
        lang: str = "en",
        flags: int = 0x1,
    ) -> str:
        redirect_uri = urllib.parse.urljoin(
            "http://localhost:8000/",  # TODO: Get actual domain
            reverse("terminusgps_notifications:wialon callback"),
        )
        return urllib.parse.urlencode(
            {
                "client_id": client_id,
                "access_type": access_type,
                "activation_time": activation_time,
                "duration": duration,
                "lang": lang,
                "flags": flags,
                "redirect_uri": redirect_uri,
                "response_type": "token",
                "user": customer.user.username,
            }
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer = Customer.objects.get(user=self.request.user)
        login_params = self.generate_wialon_login_params(customer)
        context["login_params"] = login_params
        try:
            context["wialon_token"] = customer.wialon_token
        except WialonToken.DoesNotExist:
            context["wialon_token"] = None
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

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if username := request.GET.get("user"):
            if (
                request.user.is_authenticated
                and request.user.username == username
            ):
                customer = Customer.objects.get(user__username=username)
                token = WialonToken()
                token.value = request.GET.get("access_token")
                token.save()
                customer.wialon_token = token
                customer.save()
        return super().get(request, *args, **kwargs)
