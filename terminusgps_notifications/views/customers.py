import decimal
import typing

from authorizenet import apicontractsv1
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import FormView, RedirectView, TemplateView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
    Subscription,
)
from terminusgps_payments.services import AuthorizenetService

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
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        context["customer"] = customer
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
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        try:
            customer_profile = CustomerProfile.objects.get(user=customer.user)
        except CustomerProfile.DoesNotExist:
            customer_profile = CustomerProfile(user=customer.user)
            service = AuthorizenetService()
            anet_response = service.create_customer_profile(customer_profile)
            customer_profile.pk = int(anet_response.customerProfileId)
            customer_profile.save()
        context["customer_profile"] = customer_profile
        context["customer"] = customer
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

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        context["customer"] = customer
        return context


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
                customer = Customer.objects.get(
                    user__username=request.GET.get("user", "")
                )
                if not hasattr(customer, "token"):
                    token.customer = customer
                    token.save()
            except Customer.DoesNotExist:
                return HttpResponse(status=404)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        context["customer"] = customer
        context["has_token"] = hasattr(customer, "token")
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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Adds :py:attr:`anet_service` to the view for Authorizenet API calls."""
        self.anet_service = AuthorizenetService()
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds `customer` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        context["customer"] = customer
        return context

    def get_form(self, form_class=None) -> CustomerSubscriptionCreationForm:
        """Sets customer payment profiles and address profiles in the form."""
        form = super().get_form(form_class=form_class)
        payment_qs = PaymentProfile.objects.for_user(self.request.user)
        address_qs = AddressProfile.objects.for_user(self.request.user)
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["payment_profile"].empty_label = None
        form.fields["address_profile"].queryset = address_qs
        form.fields["address_profile"].empty_label = None
        return form

    @transaction.atomic
    def form_valid(
        self, form: CustomerSubscriptionCreationForm
    ) -> HttpResponse:
        """Creates a subscription for the customer in Authorizenet."""
        try:
            # Retrieve db objects for Authorizenet API call
            customer, _created = Customer.objects.get_or_create(
                user=self.request.user
            )
            customer_profile = CustomerProfile.objects.get(
                user=self.request.user
            )
        except CustomerProfile.DoesNotExist:
            customer_profile = CustomerProfile(user=self.request.user)
            anet_response = self.anet_service.create_customer_profile(
                customer_profile
            )
            customer_profile.pk = int(anet_response.customerProfileId)
            customer_profile.save()

        # Set subscription variables
        name = "Terminus GPS Notifications"
        start_date = timezone.now()
        amount = customer.grand_total
        trial_amount = decimal.Decimal("0.00")
        payment_profile = form.cleaned_data["payment_profile"]
        address_profile = form.cleaned_data["address_profile"]

        # Set once-per-month interval
        interval = apicontractsv1.paymentScheduleTypeInterval()
        interval.length = 1
        interval.unit = "months"

        # Set infinitely recurring payment schedule
        schedule = apicontractsv1.paymentScheduleType()
        schedule.startDate = start_date
        schedule.totalOccurrences = 9999
        schedule.trialOccurrences = 0
        schedule.interval = interval

        # Set customer payment information
        profile = apicontractsv1.customerProfileIdType()
        profile.customerProfileId = str(customer_profile.pk)
        profile.customerPaymentProfileId = str(payment_profile.pk)
        profile.customerAddressId = str(address_profile.pk)

        # Set Authorizenet subscription contract
        anet_subscription = apicontractsv1.ARBSubscriptionType()
        anet_subscription.name = name
        anet_subscription.amount = amount
        anet_subscription.trialAmount = trial_amount
        anet_subscription.profile = profile
        anet_subscription.paymentSchedule = schedule

        try:
            # Create subscription locally and in Authorizenet
            subscription = Subscription(
                name=name,
                amount=amount,
                customer_profile=customer_profile,
                payment_profile=payment_profile,
                address_profile=address_profile,
            )
            anet_response = self.anet_service.create_subscription(
                subscription, anet_subscription
            )
            subscription.pk = int(anet_response.subscriptionId)
            subscription.save()
            customer.subscription = subscription
            customer.save()
            return HttpResponseRedirect(
                reverse("terminusgps_notifications:subscription"),
                headers={"HX-Retarget": "#subscription"},
            )
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _("Whoops! %(error)s"),
                            code="invalid",
                            params={"error": str(e)},
                        ),
                    )
            return self.form_invalid(form=form)


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
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        context["customer"] = customer
        return context


class WialonLoginView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, RedirectView
):
    http_method_names = ["get"]
    permanent = True
    query_string = True
    url = "https://hosting.terminusgps.com/login.html"
