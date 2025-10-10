import json
import typing
import urllib.parse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.forms import Form
from django.urls import reverse_lazy
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

from terminusgps_notifications import constants, forms, models


class WialonNotificationTriggerFormSuccessView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_notifications/notifications/partials/_trigger_success.html"
    template_name = (
        "terminusgps_notifications/notifications/trigger_success.html"
    )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["value"] = json.dumps(self.request.GET)
        return context


class WialonNotificationTriggerFormView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_trigger_form.html"
    )
    success_url = reverse_lazy("terminusgps_notifications:trigger success")
    template_name = "terminusgps_notifications/notifications/trigger_form.html"

    # TODO: Move this map somewhere else, settings maybe?
    TRIGGERS_MAP = {
        constants.WialonNotificationTriggerType.SENSOR: {
            "initial": {
                "lower_bound": -1,
                "prev_msg_diff": 0,
                "sensor_name_mask": "*",
                "sensor_type": constants.WialonUnitSensorType.ANY,
                "type": 0,
                "upper_bound": 1,
            },
            "form_cls": forms.SensorValueTriggerForm,
        }
    }

    def get_success_url(self) -> str:
        """Adds the form data to the success url as path parameters before returning it."""
        url = super().get_success_url()
        params = self.request.POST.copy()
        params.pop("csrfmiddlewaretoken")
        return "%s?%s" % (url, urllib.parse.urlencode(params))

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["trigger"] = self.request.GET.get("trigger")
        return context

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        if trigger := self.request.GET.get("trigger"):
            if trigger in self.TRIGGERS_MAP:
                for k, v in self.TRIGGERS_MAP[trigger]["initial"].items():
                    initial[k] = v
        return initial

    def get_form_class(self) -> Form:
        """Returns the form class for the trigger based on path parameters."""
        if trigger := self.request.GET.get("trigger"):
            if trigger in self.TRIGGERS_MAP:
                return self.TRIGGERS_MAP[trigger]["form_cls"]
        return Form


class WialonNotificationCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    form_class = forms.WialonNotificationCreationForm
    http_method_names = ["get", "post"]
    model = models.WialonNotification
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_create.html"
    )
    success_url = reverse_lazy("terminusgps_notifications:list notification")
    template_name = "terminusgps_notifications/notifications/create.html"

    def get_form(
        self, form_class=None
    ) -> forms.WialonNotificationCreationForm:
        form = super().get_form(form_class=form_class)
        customer, _ = models.Customer.objects.get_or_create(
            user=self.request.user
        )
        form.fields["units"].queryset = models.WialonUnit.objects.filter(
            customer=customer
        )
        return form


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

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(customer__user=self.request.user)


class WialonNotificationUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    fields = ["method"]
    http_method_names = ["get", "post"]
    model = models.WialonNotification
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_update.html"
    )
    pk_url_kwarg = "notification_pk"
    template_name = "terminusgps_notifications/notifications/update.html"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(customer__user=self.request.user)


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

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(customer__user=self.request.user)


class WialonNotificationListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    http_method_names = ["get"]
    model = models.WialonNotification
    ordering = "pk"
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_list.html"
    )
    template_name = "terminusgps_notifications/notifications/list.html"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(customer__user=self.request.user)
            .order_by(self.get_ordering())
        )
