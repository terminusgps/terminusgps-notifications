import json
import logging
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
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
    template_name = "terminusgps_notifications/triggers/form.html"
    success_url = reverse_lazy(
        "terminusgps_notifications:create notifications"
    )

    def form_valid(self, form: forms.TriggerForm) -> HttpResponse:
        """Adds ``t`` and ``p`` to the request session before redirecting the client."""
        self.request.session["t"] = form.cleaned_data["t"]
        self.request.session["p"] = form.cleaned_data["p"]
        return super().form_valid(form=form)


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
            self.request.session["t"] = self.request.GET["t"]
        return forms.TRIGGER_FORM_MAP.get(
            self.request.session.get("t", "sensor_value")
        )

    def form_valid(self, form):
        self.request.session["p"] = json.dumps(form.cleaned_data)
        return super().form_valid(form=form)


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
        context["value"] = self.request.session.get("p", "{}")
        return context


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
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

    def get_form(self, form_class=None) -> forms.WialonUnitSelectForm:
        form = super().get_form(form_class=form_class)
        customer = services.get_customer(self.request.user)
        token = services.get_wialon_token(self.request.user)
        if customer and token:
            with WialonSession(token=token) as session:
                resource_id_choices = self.get_resource_id_choices(
                    customer, session
                )
                if self.request.session.get("resource_id"):
                    resource_id = self.request.session["resource_id"]
                else:
                    resource_id = (
                        self.request.GET["resource_id"]
                        if self.request.GET.get("resource_id")
                        else resource_id_choices[0][0]
                    )
                    self.request.session["resource_id"] = resource_id
                unit_list_choices = self.get_unit_list_choices(
                    customer,
                    resource_id,
                    session,
                    self.request.session.get("items_type", "avl_unit"),
                )
                form.fields["resource_id"].choices = resource_id_choices
                form.fields["unit_list"].choices = unit_list_choices
        return form

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        request.session["resource_id"] = request.GET.get("resource_id")
        request.session["items_type"] = request.GET.get(
            "items_type", "avl_unit"
        )
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: forms.WialonUnitSelectForm) -> HttpResponse:
        self.request.session["resource_id"] = form.cleaned_data["resource_id"]
        self.request.session["unit_list"] = form.cleaned_data["unit_list"]
        return super().form_valid(form=form)

    def get_resource_id_choices(
        self,
        customer: models.TerminusgpsNotificationsCustomer,
        session: WialonSession,
    ) -> list[tuple[int, str]]:
        return [
            (int(resource["id"]), str(resource["nm"]))
            for resource in customer.get_resources_from_wialon(session)
        ]

    def get_unit_list_choices(
        self,
        customer: models.TerminusgpsNotificationsCustomer,
        resource_id: int,
        session: WialonSession,
        items_type: str,
    ) -> list[tuple[int, str]]:
        return [
            (int(unit["id"]), str(unit["nm"]))
            for unit in customer.get_units_from_wialon(
                resource_id, session, items_type
            )
        ]


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
                notification.trigger_type = self.request.session["t"]
                notification.trigger_parameters = self.request.session["p"]
                notification.resource_id = self.request.session["resource_id"]
                notification.unit_list = self.request.session["unit_list"]
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
    paginate_by = 12

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds ``customer``, ``has_token`` and ``login_params`` to the view context."""
        customer = services.get_customer(self.request.user)
        has_token = hasattr(customer, "token") if customer else False
        login_params = (
            services.get_wialon_login_parameters(self.request.user.username)
            if hasattr(self.request, "user")
            else {}
        )

        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = customer
        context["has_token"] = has_token
        context["login_params"] = login_params
        return context

    def get_ordering(self) -> str:
        """Returns ordering based on the ``order`` query parameter."""
        if user_input := self.request.GET.get("order"):
            if user_input in ("name", "-date_created"):
                return user_input
        return self.ordering

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(customer__user=self.request.user)
            .order_by(self.get_ordering())
        )
