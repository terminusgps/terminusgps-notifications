import json
import logging
import typing
from urllib.parse import urlencode, urljoin

from django.conf import settings
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
from terminusgps.wialon import flags
from terminusgps.wialon.session import WialonAPIError, WialonSession

from terminusgps_notifications import constants, forms, models

logger = logging.getLogger(__name__)


@method_decorator(cache_page(timeout=60 * 15), name="get")
@method_decorator(cache_control(private=True), name="get")
class WialonNotificationUnitSelectFormView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    form_class = forms.WialonUnitSelectionForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_notifications/units/partials/_select.html"
    )
    template_name = "terminusgps_notifications/units/select.html"

    def get_success_url(self, form) -> str:
        return reverse(
            "terminusgps_notifications:select triggers",
            query={"un": str(form.cleaned_data["units"])},
        )

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url(form))

    def get_form(self, form_class=None) -> forms.WialonUnitSelectionForm:
        form = super().get_form(form_class=form_class)
        customer = models.Customer.objects.get(user=self.request.user)
        if hasattr(customer, "token"):
            try:
                token = getattr(customer, "token").name
                with WialonSession(token=token) as session:
                    unit_list = [
                        (int(unit["id"]), str(unit["nm"]))
                        for unit in customer.get_units_from_wialon(session)
                    ]
                    form.fields["units"].choices = unit_list
            except WialonAPIError as e:
                logger.warning(e)
        return form


class WialonNotificationTriggerSelectFormView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    form_class = forms.TriggerForm
    http_method_names = ["get", "post"]
    initial = {"t": constants.WialonNotificationTriggerType.SENSOR}
    partial_template_name = (
        "terminusgps_notifications/triggers/partials/_select.html"
    )
    template_name = "terminusgps_notifications/triggers/select.html"

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["un"] = self.request.GET.get("un")
        return initial

    def form_valid(self, form: forms.TriggerForm) -> HttpResponse:
        return HttpResponseRedirect(
            reverse(
                "terminusgps_notifications:create notifications",
                query={
                    "un": form.cleaned_data["un"],
                    "p": json.dumps(form.cleaned_data["p"]),
                    "t": form.cleaned_data["t"],
                },
            )
        )


class WialonNotificationTriggerParametersFormSuccessView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = (
        "terminusgps_notifications/triggers/parameters_success.html"
    )
    partial_template_name = (
        "terminusgps_notifications/triggers/partials/_parameters_success.html"
    )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["value"] = self.request.GET.get("p")
        return context


class WialonNotificationTriggerParametersFormView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_notifications/triggers/partials/_parameters.html"
    )
    template_name = "terminusgps_notifications/triggers/parameters.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.trigger = None
        if t := self.request.GET.get("t"):
            self.trigger = t
        elif t := self.request.POST.get("t"):
            self.trigger = t

    def get_form_class(self):
        if self.trigger is None:
            return Form
        return forms.triggers.TRIGGER_FORM_MAP.get(self.trigger)

    def form_valid(self, form):
        return HttpResponseRedirect(
            reverse(
                "terminusgps_notifications:trigger parameters success",
                query={"p": form.as_json()},
            )
        )


class WialonNotificationCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    extra_context = {
        "message_tags": constants.WialonNotificationMessageTag.choices
    }
    content_type = "text/html"
    form_class = forms.WialonNotificationCreationForm
    http_method_names = ["get", "post"]
    model = models.WialonNotification
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_create.html"
    )
    success_url = reverse_lazy("terminusgps_notifications:list notifications")
    template_name = "terminusgps_notifications/notifications/create.html"

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        schedule = {"f1": 0, "f2": 0, "t1": 0, "t2": 0, "m": 0, "w": 0, "y": 0}
        customer, _ = models.Customer.objects.get_or_create(
            user=self.request.user
        )
        trigger = {
            "t": self.request.GET.get("t", ""),
            "p": json.loads(self.request.GET.get("p", "{}")),
        }

        initial["name"] = "New Notification"
        initial["message"] = "%NOTIFICATION%"
        initial["timezone"] = 0
        initial["customer"] = customer
        initial["unit_list"] = self.request.GET.get("un")
        initial["trigger"] = trigger
        initial["schedule"] = schedule.copy()
        initial["control_schedule"] = schedule.copy()
        return initial

    @transaction.atomic
    def form_valid(
        self, form: forms.WialonNotificationCreationForm
    ) -> HttpResponse:
        try:
            customer = form.cleaned_data["customer"]
            token = getattr(customer, "token").name
            with WialonSession(token=token) as session:
                if not customer.resource_id:
                    api_response = session.wialon_api.core_create_resource(
                        **{
                            "creatorId": session.uid,
                            "name": "Terminus GPS Notifications",
                            "dataFlags": flags.DataFlag.RESOURCE_BASE,
                            "skipCreatorCheck": int(True),
                        }
                    )
                    customer.resource_id = int(api_response["item"]["id"])
                    customer.save()
                notification = form.save(commit=False)
                notification.actions = notification.get_actions()
                notification.text = notification.get_text()
                api_response = notification.create_in_wialon(session)
                notification.wialon_id = int(api_response[0])
                notification.save()
            return super().form_valid(form=form)
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


class WialonNotificationDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.WialonNotification
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_detail.html"
    )
    pk_url_kwarg = "notification_pk"
    template_name = "terminusgps_notifications/notifications/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["title"] = self.get_object().name
        return context

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
        token = getattr(notification.customer, "token").name
        if form.changed_data:
            try:
                with WialonSession(token=token) as session:
                    if "method" in form.changed_data:
                        notification.actions = notification.get_actions()
                    if "message" in form.changed_data:
                        notification.text = notification.get_text()
                    notification.update_in_wialon(session)
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
        return HttpResponseRedirect(
            notification.get_absolute_url(), headers={"HX-Refresh": "true"}
        )


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
            token = getattr(self.object.customer, "token").name
            with WialonSession(token=token) as session:
                self.object.delete_in_wialon(session)
            return super().form_valid(form=form)
        except (ValueError, WialonAPIError):
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

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer, _ = models.Customer.objects.get_or_create(
            user=self.request.user
        )

        context["has_token"] = hasattr(customer, "token")
        context["login_params"] = urlencode(
            {
                "client_id": "Terminus GPS Notifications",
                "access_type": settings.WIALON_TOKEN_ACCESS_TYPE,
                "activation_time": 0,
                "duration": 2_592_000,
                "lang": "en",
                "flags": 0x1,
                "user": self.request.user.username,
                "redirect_uri": urljoin(
                    "https://api.terminusgps.com/v3/"
                    if not settings.DEBUG
                    else "http://127.0.0.1:8000/",
                    reverse("terminusgps_notifications:notifications"),
                ),
                "response_type": "token",
            }
        )
        return context

    def get_ordering(self) -> str:
        if user_input := self.request.GET.get("order"):
            if user_input in ("name", "date_created"):
                return user_input
        return self.ordering

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(customer__user=self.request.user)
            .order_by(self.get_ordering())
        )
