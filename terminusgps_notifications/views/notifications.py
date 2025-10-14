import json
import logging
import typing
from urllib.parse import quote

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
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

from terminusgps_notifications import constants, forms, models

logger = logging.getLogger(__name__)


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
            query={
                "un": str(form.cleaned_data["units"])
                if len(form.cleaned_data["units"]) <= 1
                else quote(",".join(form.cleaned_data["units"]))
            },
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
        print(f"{form.cleaned_data["p"] = }")
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

    def get_form_class(self):
        trigger = self.request.GET.get("t")
        trigger = self.request.POST.get("t", trigger)
        return forms.triggers.TRIGGER_FORM_MAP.get(trigger)

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
    content_type = "text/html"
    form_class = forms.WialonNotificationCreationForm
    http_method_names = ["get", "post"]
    model = models.WialonNotification
    partial_template_name = (
        "terminusgps_notifications/notifications/partials/_create.html"
    )
    success_url = reverse_lazy("terminusgps_notifications:list notification")
    template_name = "terminusgps_notifications/notifications/create.html"

    def form_valid(
        self, form: forms.WialonNotificationCreationForm
    ) -> HttpResponse:
        print(f"{form.cleaned_data = }")
        return super().form_valid(form=form)


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
