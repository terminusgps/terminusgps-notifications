import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError, WialonSession

from terminusgps_notifications import constants, forms, models

logger = logging.getLogger(__name__)


class WialonNotificationUnitSelectFormView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    form_class = forms.WialonUnitSelectionForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_select_unit.html"
    )
    template_name = "terminusgps_notifications/notifications/select_unit.html"
    success_url = reverse_lazy(
        "terminusgps_notifications:select notification trigger"
    )

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
        "terminusgps_notifications/notifications/partials/_select_trigger.html"
    )
    template_name = (
        "terminusgps_notifications/notifications/select_trigger.html"
    )


class WialonNotificationTriggerParametersFormView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_params_trigger.html"
    )
    template_name = (
        "terminusgps_notifications/notifications/params_trigger.html"
    )

    def form_valid(self, form):
        pass

    def get_form_class(self):
        if trg := self.request.GET.get("t"):
            return forms.triggers.TRIGGER_FORM_MAP.get(trg)
        elif trg := self.request.POST.get("t"):
            return forms.triggers.TRIGGER_FORM_MAP.get(trg)


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
