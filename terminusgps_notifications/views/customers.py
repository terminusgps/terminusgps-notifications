import decimal
import typing

from authorizenet import apicontractsv1
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet, Sum
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    RedirectView,
    TemplateView,
)
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import (
    AddressProfile,
    PaymentProfile,
    Subscription,
)
from terminusgps_payments.services import AuthorizenetService

from terminusgps_notifications import services, tasks
from terminusgps_notifications.forms import (
    CustomerSubscriptionCreationForm,
    ExtensionPackageCreationForm,
)
from terminusgps_notifications.models import ExtensionPackage, WialonToken


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class DashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Dashboard",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/customers/partials/_dashboard.html"
    )
    template_name = "terminusgps_notifications/customers/dashboard.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Adds :py:attr:`customer`, :py:attr:`has_token` and :py:attr:`has_subscription` to the view."""
        customer = (
            services.get_customer(request.user)
            if hasattr(request, "user")
            else None
        )
        token = (
            services.get_wialon_token(request.user)
            if hasattr(request, "user")
            else None
        )
        subscription = (
            getattr(customer, "subscription")
            if customer is not None and hasattr(customer, "subscription")
            else None
        )
        self.customer = customer
        self.has_token = bool(token)
        self.has_subscription = bool(subscription)
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds :py:attr:`customer`, :py:attr:`has_token` and :py:attr:`has_subscription` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["has_token"] = self.has_token
        context["has_subscription"] = self.has_subscription
        return context


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Account"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/customers/partials/_account.html"
    )
    template_name = "terminusgps_notifications/customers/account.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Adds :py:attr:`customer`, :py:attr:`has_token` and :py:attr:`login_params` to the view."""
        customer = (
            services.get_customer(request.user)
            if hasattr(request, "user")
            else None
        )
        token = (
            services.get_wialon_token(request.user)
            if hasattr(request, "user")
            else None
        )
        login_params = (
            services.get_wialon_login_parameters(request.user)
            if hasattr(request, "user")
            else None
        )
        self.customer = customer
        self.has_token = bool(token)
        self.login_params = login_params
        return super().setup(request, *args, **kwargs)

    @transaction.atomic
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Saves a Wialon API token for the user based on the ``user_name`` and ``access_token`` path parameters."""
        if hasattr(request, "user") and self.customer is not None:
            user = getattr(request, "user")
            username = request.GET.get("user_name")
            access_token = request.GET.get("access_token")
            if all(
                [
                    username,
                    access_token,
                    hasattr(user, "username"),
                    getattr(user, "username") == self.customer.user.username,
                ]
            ):
                if hasattr(self.customer, "token"):
                    old_token = getattr(self.customer, "token")
                    old_token.delete()
                new_token = WialonToken()
                new_token.name = access_token
                new_token.customer = self.customer
                new_token.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds :py:attr:`customer`, :py:attr:`has_token` and :py:attr:`login_params` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["has_token"] = self.has_token
        context["login_params"] = self.login_params
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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Adds :py:attr:`customer` to the view."""
        customer = (
            services.get_customer(request.user)
            if hasattr(request, "user")
            else None
        )
        self.customer = customer
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds :py:attr:`customer` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Adds :py:attr:`customer` and :py:attr:`has_token` to the view context."""
        customer = (
            services.get_customer(request.user)
            if hasattr(request, "user")
            else None
        )
        token = (
            services.get_wialon_token(request.user)
            if hasattr(request, "user")
            else None
        )
        packages = (
            getattr(customer, "package").all()
            if customer and hasattr(customer, "package")
            else None
        )

        self.customer = customer
        self.has_token = bool(token)
        self.packages = packages
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds :py:attr:`customer` and :py:attr:`has_token` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["has_token"] = self.has_token
        context["packages"] = self.packages
        return context


class ExtensionPackageListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "packages"
    extra_context = {"title": "Extension Packages"}
    http_method_names = ["get"]
    model = ExtensionPackage
    ordering = "pk"
    paginate_by = 4
    partial_template_name = (
        "terminusgps_notifications/subscriptions/packages/partials/_list.html"
    )
    template_name = (
        "terminusgps_notifications/subscriptions/packages/list.html"
    )

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(customer__user=self.request.user)
            .order_by(self.get_ordering())
        )


class ExtensionPackageCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    extra_context = {"title": "Create Extension Package"}
    http_method_names = ["get", "post"]
    form_class = ExtensionPackageCreationForm
    partial_template_name = "terminusgps_notifications/subscriptions/packages/partials/_create.html"
    template_name = (
        "terminusgps_notifications/subscriptions/packages/create.html"
    )
    success_url = reverse_lazy("terminusgps_notifications:list packages")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Adds :py:attr:`customer` to the view."""
        self.customer = (
            services.get_customer(request.user)
            if hasattr(request, "user")
            else None
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds :py:attr:`customer` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        return context

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        """Sets the initial value for :py:attr:`customer` in the form."""
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["customer"] = self.customer
        return initial

    def get_form(self, form_class=None):
        """Sets choices for :py:attr:`customer` in the form."""
        form = super().get_form(form_class=form_class)
        form.fields["customer"].choices = (
            [(self.customer.pk, str(self.customer))]
            if self.customer is not None
            else []
        )
        return form

    def form_valid(self, form: ExtensionPackageCreationForm) -> HttpResponse:
        if form.cleaned_data["customer"].subscription is None:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! You need to be subscribed to do that."),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)

        response = super().form_valid(form=form)
        customer = form.cleaned_data["customer"]
        price_sum = customer.packages.aggregate(Sum("price")).get("price__sum")
        executions_sum = customer.packages.aggregate(Sum("executions")).get(
            "executions__sum"
        )
        new_amount = customer.subtotal_base + price_sum
        new_executions = customer.executions_max_base + executions_sum
        customer.subtotal = new_amount
        customer.executions_max = new_executions
        customer.save()
        contract = apicontractsv1.ARBSubscriptionType()
        contract.amount = new_amount
        service = AuthorizenetService()
        service.update_subscription(customer.subscription, contract)
        customer.subscription.amount = customer.subtotal
        customer.subscription.save()
        return response


class ExtensionPackageDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {"title": "Extension Package Details"}
    http_method_names = ["get"]
    model = ExtensionPackage
    partial_template_name = "terminusgps_notifications/subscriptions/packages/partials/_detail.html"
    pk_url_kwarg = "package_pk"
    template_name = (
        "terminusgps_notifications/subscriptions/packages/detail.html"
    )

    def get_queryset(self) -> QuerySet:
        if not hasattr(self.request, "user"):
            return ExtensionPackage.objects.none()
        return super().get_queryset().filter(customer__user=self.request.user)


class ExtensionPackageDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    extra_context = {"title": "Delete Extension Package"}
    http_method_names = ["post"]
    model = ExtensionPackage
    partial_template_name = "terminusgps_notifications/subscriptions/packages/partials/_delete.html"
    pk_url_kwarg = "package_pk"
    success_url = reverse_lazy("terminusgps_notifications:list packages")
    template_name = (
        "terminusgps_notifications/subscriptions/packages/delete.html"
    )

    def get_queryset(self) -> QuerySet:
        if not hasattr(self.request, "user"):
            return ExtensionPackage.objects.none()
        return super().get_queryset().filter(customer__user=self.request.user)

    def form_valid(self, form) -> HttpResponse:
        customer = self.object.customer
        new_amount = customer.subtotal - self.object.price
        customer.subtotal = new_amount
        customer.save(update_fields=["subtotal"])
        return super().form_valid(form=form)


class CustomerSubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {
        "title": "Create Subscription",
        "setup_fee": settings.NOTIFICATIONS_SETUP_FEE,
    }
    form_class = CustomerSubscriptionCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_notifications/customers/partials/_create_subscription.html"
    template_name = (
        "terminusgps_notifications/customers/create_subscription.html"
    )

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Adds :py:attr:`customer` and :py:attr:`anet_service` to the view."""
        customer = (
            services.get_customer(request.user)
            if hasattr(request, "user")
            else None
        )
        self.customer = customer
        self.anet_service = AuthorizenetService()
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds :py:attr:`customer` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["total"] = self.customer.subtotal + context["setup_fee"]
        return context

    def get_form(self, form_class=None) -> CustomerSubscriptionCreationForm:
        """Sets customer payment profiles and address profiles in the form."""
        form = super().get_form(form_class=form_class)
        payment_qs = PaymentProfile.objects.for_user(self.request.user)
        address_qs = AddressProfile.objects.for_user(self.request.user)
        pprofile_field = form.fields["payment_profile"]
        aprofile_field = form.fields["address_profile"]
        pprofile_field.queryset = payment_qs
        pprofile_field.empty_label = None
        aprofile_field.queryset = address_qs
        aprofile_field.empty_label = None
        return form

    @transaction.atomic
    def form_valid(
        self, form: CustomerSubscriptionCreationForm
    ) -> HttpResponse:
        """Creates a subscription for the customer in Authorizenet."""
        if self.customer is None:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Your account doesn't have an associated customer. Please try again later"
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        customer_profile = services.get_customer_profile(self.request.user)
        if customer_profile is None:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Your account doesn't have an associated customer profile. Please try again later"
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)

        # Set subscription variables
        payment_profile = form.cleaned_data["payment_profile"]
        address_profile = form.cleaned_data["address_profile"]
        start_date = timezone.now()
        name = "Terminus GPS Notifications"
        amount = self.customer.subtotal
        trial_amount = decimal.Decimal("0.00")
        setup_fee = settings.NOTIFICATIONS_SETUP_FEE

        # Set once-per-month interval
        interval = apicontractsv1.paymentScheduleTypeInterval()
        interval.length = 1
        interval.unit = apicontractsv1.ARBSubscriptionUnitEnum.months

        # Set infinitely recurring payment schedule
        schedule = apicontractsv1.paymentScheduleType()
        schedule.startDate = start_date
        schedule.totalOccurrences = 9999
        schedule.trialOccurrences = 1
        schedule.interval = interval

        # Set customer payment information
        profile = apicontractsv1.customerProfileIdType()
        profile.customerProfileId = str(customer_profile.pk)
        profile.customerPaymentProfileId = str(payment_profile.pk)
        profile.customerAddressId = str(address_profile.pk)

        # Set Authorizenet subscription contract
        contract = apicontractsv1.ARBSubscriptionType()
        contract.name = name
        contract.amount = amount
        contract.trialAmount = trial_amount
        contract.profile = profile
        contract.paymentSchedule = schedule

        line_item_1 = apicontractsv1.lineItemType()
        line_item_1.itemId = "1"
        line_item_1.name = "Setup Fee"
        line_item_1.description = "One-time setup fee"
        line_item_1.quantity = "1"
        line_item_1.unitPrice = setup_fee

        line_item_2 = apicontractsv1.lineItemType()
        line_item_2.itemId = "2"
        line_item_2.name = "First Month"
        line_item_2.description = "First month of service"
        line_item_2.quantity = "1"
        line_item_2.unitPrice = amount

        line_items = apicontractsv1.ArrayOfLineItem()
        line_items.lineItem.append(line_item_1)
        line_items.lineItem.append(line_item_2)

        try:
            # Collect setup fee + month 1
            self.anet_service.charge_customer_profile(
                customer_profile,
                payment_profile,
                amount + setup_fee,
                line_items,
            )

            # Create subscription locally and in Authorizenet
            subscription = Subscription(
                name=name,
                amount=amount,
                customer_profile=customer_profile,
                payment_profile=payment_profile,
                address_profile=address_profile,
            )
            anet_response = self.anet_service.create_subscription(
                subscription, contract
            )
            subscription.pk = int(anet_response.subscriptionId)
            subscription.save()
            self.customer.subscription = subscription
            self.customer.save()
            tasks.reset_executions_count.enqueue_at(
                start_date + relativedelta(months=1)
            )
            return HttpResponseRedirect(
                reverse("terminusgps_notifications:subscription")
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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Adds :py:attr:`customer` and :py:attr:`has_token` to the view."""
        customer = (
            services.get_customer(request.user)
            if hasattr(request, "user")
            else None
        )
        token = (
            services.get_wialon_token(request.user)
            if hasattr(request, "user")
            else None
        )
        self.customer = customer
        self.has_token = bool(token)
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds :py:attr:`customer` and :py:attr:`has_token` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["has_token"] = self.has_token
        return context


class WialonLoginView(LoginRequiredMixin, RedirectView):
    http_method_names = ["get"]
    permanent = True
    query_string = True
    url = "https://hosting.terminusgps.com/login.html"
