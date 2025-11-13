import json
import logging
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError, WialonSession

from terminusgps_notifications import constants, forms, models, services

logger = logging.getLogger(__name__)


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class WialonNotificationTriggerFormView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    form_class = forms.TriggerForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_notifications/triggers/partials/_form.html"
    )
    success_url = reverse_lazy(
        "terminusgps_notifications:create notifications"
    )
    template_name = "terminusgps_notifications/triggers/form.html"

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["unit_list"] = self.request.GET.getlist("unit_list")
        initial["resource_id"] = self.request.GET.get("resource_id")
        return initial

    def form_valid(self, form: forms.TriggerForm) -> HttpResponse:
        return HttpResponseRedirect(
            reverse(
                "terminusgps_notifications:create notifications",
                query={
                    "trigger_type": form.cleaned_data["t"],
                    "trigger_parameters": json.dumps(form.cleaned_data["p"]),
                    "resource_id": form.cleaned_data["resource_id"],
                    "unit_list": form.cleaned_data["unit_list"],
                },
            )
        )


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class WialonNotificationTriggerParametersFormView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_notifications/triggers/partials/_parameters_form.html"
    )
    success_url = reverse_lazy(
        "terminusgps_notifications:trigger parameters success"
    )
    template_name = "terminusgps_notifications/triggers/parameters_form.html"

    def get_form_class(self):
        if self.request.GET.get("t"):
            trigger_type = self.request.GET["t"]
        elif self.request.POST.get("t"):
            trigger_type = self.request.POST["t"]
        return forms.TRIGGER_FORM_MAP.get(trigger_type)

    def form_valid(self, form):
        return HttpResponseRedirect(
            reverse(
                "terminusgps_notifications:trigger parameters success",
                query={"p": json.dumps(form.cleaned_data)},
            )
        )


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class WialonNotificationTriggerParametersSuccessView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/triggers/partials/_parameters_success.html"
    )
    template_name = (
        "terminusgps_notifications/triggers/parameters_success.html"
    )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["value"] = self.request.GET.get("p", "{}")
        return context


@method_decorator(cache_page(timeout=60 * 15), name="get")
@method_decorator(cache_control(private=True), name="get")
class WialonNotificationUnitSelectFormView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Select Units"}
    form_class = forms.WialonUnitSelectForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_notifications/units/partials/_form.html"
    )
    template_name = "terminusgps_notifications/units/form.html"
    success_url = reverse_lazy("terminusgps_notifications:triggers form")

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if "resource_id" not in request.GET or "items_type" not in request.GET:
            return HttpResponse(status=406)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if (
            "resource_id" not in request.POST
            or "items_type" not in request.POST
        ):
            return HttpResponse(status=406)
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None) -> forms.WialonUnitSelectForm:
        form = super().get_form(form_class=form_class)
        customer = services.get_customer(self.request.user)
        token = services.get_wialon_token(self.request.user)
        if customer and token:
            with WialonSession(token=token) as session:
                resource_id = self.request.GET.get(
                    "resource_id", self.request.POST.get("resource_id")
                )
                items_type = self.request.GET.get(
                    "items_type", self.request.POST.get("items_type")
                )
                form.fields["resource_id"].choices = [
                    (int(resource["id"]), str(resource["nm"]))
                    for resource in customer.get_resources_from_wialon(session)
                ]
                form.fields["unit_list"].choices = [
                    (int(unit["id"]), str(unit["nm"]))
                    for unit in customer.get_units_from_wialon(
                        resource_id=resource_id,
                        session=session,
                        items_type=items_type,
                    )
                ]
        return form

    def form_valid(self, form: forms.WialonUnitSelectForm) -> HttpResponse:
        return HttpResponseRedirect(
            reverse(
                "terminusgps_notifications:triggers form",
                query={
                    "resource_id": form.cleaned_data["resource_id"],
                    "unit_list": form.cleaned_data["unit_list"],
                },
            )
        )


class WialonNotificationCreateSuccessView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Created Notification"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_create_success.html"
    )
    template_name = (
        "terminusgps_notifications/notifications/create_success.html"
    )


class WialonNotificationCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    extra_context = {
        "title": "Create Notification",
        "message_tags": constants.WialonNotificationMessageTag.choices,
    }
    content_type = "text/html"
    form_class = forms.WialonNotificationCreationForm
    http_method_names = ["get", "post"]
    model = models.WialonNotification
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_create.html"
    )
    success_url = reverse_lazy(
        "terminusgps_notifications:create notifications success"
    )
    template_name = "terminusgps_notifications/notifications/create.html"

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        schedule = {"f1": 0, "f2": 0, "t1": 0, "t2": 0, "m": 0, "w": 0, "y": 0}
        initial["timezone"] = 0  # TODO: Retrieve client timezone
        initial["schedule"] = schedule.copy()
        initial["control_schedule"] = schedule.copy()
        initial["resource_id"] = self.request.GET.get("resource_id")
        initial["unit_list"] = self.request.GET.getlist("unit_list")
        initial["trigger_type"] = self.request.GET.get("trigger_type")
        initial["trigger_parameters"] = json.loads(
            self.request.GET.get("trigger_parameters", "{}")
        )
        return initial

    @transaction.atomic
    def form_valid(
        self, form: forms.WialonNotificationCreationForm
    ) -> HttpResponse:
        try:
            customer = services.get_customer(self.request.user)
            token = services.get_wialon_token(self.request.user)
            if token is None:
                raise ValueError("Invalid/non-existent Wialon API token.")
            if customer is None:
                raise ValueError("Invalid/non-existent customer.")
            with WialonSession(token=token) as session:
                notification = form.save(commit=False)
                notification.customer = customer
                notification.text = notification.get_text()
                notification.actions = notification.get_actions()
                notification.trigger_type = form.cleaned_data["trigger_type"]
                notification.resource_id = form.cleaned_data["resource_id"]
                notification.unit_list = form.cleaned_data["unit_list"]
                notification.trigger_parameters = form.cleaned_data[
                    "trigger_parameters"
                ]

                api_response = notification.update_in_wialon("create", session)
                notification.wialon_id = int(api_response[0])
                notification.save()
                self.object = notification
                return HttpResponseRedirect(self.get_success_url())
        except WialonAPIError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! '%(error_message)s'"),
                    code="invalid",
                    params={"error_message": str(e)},
                ),
            )
            return self.form_invalid(form=form)
        except ValueError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! '%(error_message)s'"),
                    code="invalid",
                    params={"error_message": str(e)},
                ),
            )
            return self.form_invalid(form=form)


class WialonNotificationDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Notification Details"}
    model = models.WialonNotification
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_detail.html"
    )
    pk_url_kwarg = "notification_pk"
    template_name = "terminusgps_notifications/notifications/detail.html"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(customer__user=self.request.user)


class WialonNotificationUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    extra_context = {
        "message_tags": constants.WialonNotificationMessageTag.choices
    }
    content_type = "text/html"
    http_method_names = ["get", "post"]
    form_class = forms.WialonNotificationUpdateForm
    model = models.WialonNotification
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_update.html"
    )
    pk_url_kwarg = "notification_pk"
    template_name = "terminusgps_notifications/notifications/update.html"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(customer__user=self.request.user)

    def form_valid(
        self, form: forms.WialonNotificationUpdateForm
    ) -> HttpResponse:
        notification = form.save(commit=True)
        token = services.get_wialon_token(notification.customer.user)
        if token and form.changed_data:
            try:
                with WialonSession(token=token) as session:
                    if "method" in form.changed_data:
                        notification.actions = notification.get_actions()
                    if "message" in form.changed_data:
                        notification.text = notification.get_text()
                    notification.update_in_wialon("update", session)
            except (ValueError, WialonAPIError) as e:
                form.add_error(
                    None,
                    ValidationError(
                        _("Whoops! %(error)s"),
                        code="invalid",
                        params={"error": str(e)},
                    ),
                )
                return self.form_invalid(form=form)
        return HttpResponseRedirect(notification.get_absolute_url())


class WialonNotificationDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    model = models.WialonNotification
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_delete.html"
    )
    pk_url_kwarg = "notification_pk"
    template_name = "terminusgps_notifications/notifications/delete.html"
    success_url = reverse_lazy("terminusgps_notifications:list notifications")

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(customer__user=self.request.user)

    def form_valid(self, form: Form) -> HttpResponse:
        try:
            token = services.get_wialon_token(self.request.user)
            if not token:
                raise ValueError("Invalid Wialon API token.")
            with WialonSession(token=token) as session:
                self.object.update_in_wialon("delete", session)
            return super().form_valid(form=form)
        except (ValueError, WialonAPIError) as e:
            logger.warning(e)
            return HttpResponse(status=406)


class WialonNotificationListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.WialonNotification
    ordering = "name"
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_list.html"
    )
    template_name = "terminusgps_notifications/notifications/list.html"
    paginate_by = 8

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        customer = (
            services.get_customer(self.request.user)
            if hasattr(self.request, "user")
            else None
        )
        login_params = (
            services.get_wialon_login_parameters(self.request.user.username)
            if hasattr(self.request, "user")
            else {}
        )
        has_token = (
            hasattr(customer, "token")
            if customer and customer is not None
            else False
        )
        has_subscription = (
            hasattr(customer, "subscription")
            if customer and customer is not None
            else False
        )
        self.customer = customer
        self.login_params = login_params
        self.has_token = has_token
        self.has_subscription = has_subscription

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds :py:attr:`customer`, :py:attr:`has_token`, :py:attr:`has_subscription`, :py:attr:`resource_id` and :py:attr:`login_params` to the view context."""
        resource_id = None
        if self.customer and self.has_token:
            session_key = f"{self.customer.pk}_resource_id"
            if self.request.session.get(session_key):
                resource_id = self.request.session[session_key]
            else:
                token = services.get_wialon_token(self.request.user)
                with WialonSession(token=token) as session:
                    resources = self.customer.get_resources_from_wialon(
                        session
                    )
                    resource_id = int(resources[0]["id"])
                    self.request.session[session_key] = resource_id
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["has_token"] = self.has_token
        context["login_params"] = self.login_params
        context["resource_id"] = resource_id
        return context

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(customer__user=self.request.user)
            .order_by(self.get_ordering())
        )
