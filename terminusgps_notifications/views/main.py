import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views.generic import FormView, RedirectView, TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import AddressProfile, PaymentProfile

from terminusgps_notifications.forms import CustomerSubscriptionCreationForm
from terminusgps_notifications.models import Customer


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

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"], _ = Customer.objects.get_or_create(
            user=self.request.user
        )
        return context


class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Account"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_notifications/partials/_account.html"
    template_name = "terminusgps_notifications/account.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["customer"] = Customer.objects.get(user=self.request.user)
        except Customer.DoesNotExist:
            context["customer"] = None
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


class CustomerSubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Subscription"}
    form_class = CustomerSubscriptionCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_notifications/partials/_create_subscription.html"
    )
    template_name = "terminusgps_notifications/create_subscription.html"

    def get_form(self, form_class=None) -> CustomerSubscriptionCreationForm:
        form = super().get_form(form_class=form_class)
        payment_qs = PaymentProfile.objects.for_user(self.request.user)
        address_qs = AddressProfile.objects.for_user(self.request.user)
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["payment_profile"].empty_label = None
        form.fields["address_profile"].queryset = address_qs
        form.fields["address_profile"].empty_label = None
        return form

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"], _ = Customer.objects.get_or_create(
            user=self.request.user
        )
        return context


class CustomerStatsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_notifications/partials/_stats.html"
    template_name = "terminusgps_notifications/stats.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["customer"] = Customer.objects.get(user=self.request.user)
        except Customer.DoesNotExist:
            context["customer"] = None
        return context


class WialonLoginView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, RedirectView
):
    http_method_names = ["get"]
    permanent = True
    query_string = True
    url = "https://hosting.terminusgps.com/login.html"


class WialonCallbackView(TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Logged Into Wialon"}
    http_method_names = ["get"]
    template_name = "terminusgps_notifications/wialon_callback.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        print(f"{request.GET = }")
        return super().get(request, *args, **kwargs)
