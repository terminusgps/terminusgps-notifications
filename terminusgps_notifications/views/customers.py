import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import FormView, RedirectView, TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
)

from terminusgps_notifications.forms import CustomerSubscriptionCreationForm
from terminusgps_notifications.models import Customer, WialonToken


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class DashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Dashboard"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/customers/partials/_dashboard.html"
    )
    template_name = "terminusgps_notifications/customers/dashboard.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        return context


class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Account"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/customers/partials/_account.html"
    )
    template_name = "terminusgps_notifications/customers/account.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        try:
            customer, _ = Customer.objects.get_or_create(
                user=self.request.user
            )
            customer_profile = CustomerProfile.objects.get(
                user=self.request.user
            )
            context["customer"] = customer
            context["customer_profile"] = customer_profile
        except CustomerProfile.DoesNotExist:
            context["customer"] = customer
            context["customer_profile"] = None
        return context


class SubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Subscription"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/customers/partials/_subscription.html"
    )
    template_name = "terminusgps_notifications/customers/subscription.html"


class NotificationsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Notifications"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/customers/partials/_notifications.html"
    )
    template_name = "terminusgps_notifications/customers/notifications.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if name := request.GET.get("access_token"):
            token = WialonToken(name=name)
            try:
                token.customer = Customer.objects.get(
                    user__username=request.GET.get("user", "")
                )
                token.save()
            except Customer.DoesNotExist:
                return HttpResponse(status=404)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        try:
            context["customer"] = Customer.objects.get(user=self.request.user)
            context["has_token"] = hasattr(context["customer"], "token")
        except Customer.DoesNotExist:
            context["customer"] = None
            context["has_token"] = None
        return context


class CustomerSubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Subscription"}
    form_class = CustomerSubscriptionCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_notifications/customers/partials/_create_subscription.html"
    template_name = (
        "terminusgps_notifications/customers/create_subscription.html"
    )

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
        try:
            context["customer"] = Customer.objects.get(user=self.request.user)
        except Customer.DoesNotExist:
            context["customer"] = None
        return context

    def form_valid(
        self, form: CustomerSubscriptionCreationForm
    ) -> HttpResponse:
        return HttpResponseRedirect(
            reverse("terminusgps_notifications:subscription"),
            headers={"HX-Retarget": "#subscription"},
        )


class CustomerStatsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/customers/partials/_stats.html"
    )
    template_name = "terminusgps_notifications/customers/stats.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        try:
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


class WialonCallbackView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Logged Into Wialon"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/customers/partials/_wialon_callback.html"
    )
    template_name = "terminusgps_notifications/customers/wialon_callback.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if name := request.GET.get("access_token"):
            token = WialonToken(name=name)
        else:
            return HttpResponse(status=406)
        try:
            token.customer = Customer.objects.get(
                user__username=request.GET.get("user", "")
            )
            token.save()
            return super().get(request, *args, **kwargs)
        except Customer.DoesNotExist:
            return HttpResponse(status=404)
