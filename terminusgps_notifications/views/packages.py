import decimal
import typing

from authorizenet import apicontractsv1
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import PaymentProfile
from terminusgps_payments.services import AuthorizenetService

from terminusgps_notifications import forms, models, services


class MessagePackageCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    extra_context = {"title": "Create Package"}
    form_class = forms.MessagePackageCreationForm
    http_method_names = ["get", "post"]
    model = models.MessagePackage
    partial_template_name = (
        "terminusgps_notifications/packages/partials/_create.html"
    )
    template_name = "terminusgps_notifications/packages/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer = (
            services.get_customer(request.user)
            if hasattr(request, "user")
            else None
        )
        self.customer_profile = (
            services.get_customer_profile(request.user)
            if hasattr(request, "user")
            else None
        )

    def get_form(self, form_class=None) -> forms.MessagePackageCreationForm:
        form = super().get_form(form_class=form_class)
        form.fields["payment"].empty_label = None
        form.fields["payment"].queryset = (
            PaymentProfile.objects.for_user(self.request.user)
            if hasattr(self.request, "user")
            else PaymentProfile.objects.none()
        )
        return form

    @transaction.atomic
    def form_valid(
        self, form: forms.MessagePackageCreationForm
    ) -> HttpResponse:
        if self.customer is None:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! You don't have a customer associated with your account. Please try again later."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        if self.customer_profile is None:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! You don't have a customer profile associated with your account. Please try again later."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        if int(form.cleaned_data["count"]) % 500 != 0:
            form.add_error(
                "count",
                ValidationError(
                    _(
                        "Whoops! You can only purchase messages in 500 message blocks. Please enter a number divisible by 500 and try again."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        package = models.MessagePackage()
        package.customer = self.customer
        package.max = int(form.cleaned_data["count"])
        package.price = round(
            decimal.Decimal(package.max / 500) * decimal.Decimal("40.00"),
            ndigits=2,
        )

        line_item = apicontractsv1.lineItemType()
        line_item.itemId = "1"
        line_item.name = f"x{package.max} messages package"
        line_item.description = (
            "Message package for Terminus GPS Notifications platform"
        )
        line_item.quantity = "1"
        line_item.unitPrice = package.price
        line_items = apicontractsv1.ArrayOfLineItem()
        line_items.lineItem.append(line_item)

        service = AuthorizenetService()
        service.charge_customer_profile(
            customer_profile=self.customer_profile,
            payment_profile=form.cleaned_data["payment"],
            amount=package.price,
            line_items=line_items,
        )
        package.save()
        return HttpResponseRedirect(
            reverse("terminusgps_notifications:list packages")
        )


class MessagePackageListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    extra_context = {"title": "List Packages"}
    http_method_names = ["get"]
    model = models.MessagePackage
    partial_template_name = (
        "terminusgps_notifications/packages/partials/_list.html"
    )
    template_name = "terminusgps_notifications/packages/list.html"
    ordering = ["price"]

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(customer__user=self.request.user)
            .order_by(self.get_ordering())
        )


class MessagePackagePriceView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Package Price"}
    http_method_names = ["get"]
    template_name = "terminusgps_notifications/packages/price.html"
    partial_template_name = (
        "terminusgps_notifications/packages/partials/_price.html"
    )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not hasattr(request, "GET") or not request.GET.get("count"):
            return HttpResponse(status=406)
        elif (
            isinstance(request.GET["count"], str)
            and not request.GET["count"].isdigit()
        ):
            return HttpResponse(status=406)
        self.count = int(request.GET["count"])
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["price"] = (
            decimal.Decimal(self.count / 500) * decimal.Decimal("40.00")
            if self.count % 500 == 0
            else None
        )
        return context
