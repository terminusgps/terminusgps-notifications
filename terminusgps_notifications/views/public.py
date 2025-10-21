import logging

from django import forms
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm
from django.contrib.auth.views import LoginView as LoginViewBase
from django.contrib.auth.views import LogoutView as LogoutViewBase
from django.core.validators import validate_email
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import FormView, RedirectView, TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_notifications.models import TerminusgpsNotificationsCustomer

logger = logging.getLogger(__name__)


class TerminusgpsNotificationsAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].widget = forms.widgets.EmailInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600",
                "placeholder": "email@terminusgps.com",
                "autofocus": True,
                "enterkeyhint": "next",
                "inputmode": "email",
            }
        )
        self.fields["password"].widget = forms.widgets.PasswordInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600",
                "placeholder": "••••••••••••••••",
                "autocomplete": False,
                "inputmode": "text",
                "enterkeyhint": "done",
            }
        )


class TerminusgpsNotificationsRegistrationForm(BaseUserCreationForm):
    first_name = forms.CharField(
        help_text="Required. 64 characters or fewer. Letters and digits only.",
        widget=forms.widgets.TextInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600",
                "placeholder": "First",
                "enterkeyhint": "next",
            }
        ),
    )
    last_name = forms.CharField(
        help_text="Required. 64 characters or fewer. Letters and digits only.",
        widget=forms.widgets.TextInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600",
                "placeholder": "Last",
                "enterkeyhint": "next",
            }
        ),
    )
    company_name = forms.CharField(
        required=False,
        help_text="<span class='italic'>Optional</span>. 64 characters or fewer. Letters and digits only.",
        widget=forms.widgets.TextInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600",
                "placeholder": "Company",
                "enterkeyhint": "next",
            }
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].validators.append(validate_email)
        self.fields["username"].widget = forms.widgets.TextInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600",
                "placeholder": "email@terminusgps.com",
                "enterkeyhint": "next",
            }
        )
        self.fields["password1"].widget = forms.widgets.PasswordInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600",
                "placeholder": "••••••••••••••••",
                "enterkeyhint": "next",
                "autocomplete": False,
            }
        )
        self.fields["password2"].widget = forms.widgets.PasswordInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600",
                "placeholder": "••••••••••••••••",
                "enterkeyhint": "done",
                "autocomplete": False,
            }
        )


class SourceCodeView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://github.com/terminusgps/terminusgps-notifications/"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class NavbarView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_notifications/partials/_navbar.html"
    template_name = "terminusgps_notifications/navbar.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class HomeView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Terminus GPS Notifications",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_notifications/partials/_home.html"
    template_name = "terminusgps_notifications/home.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class TermsView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {
        "title": "Terms & Conditions",
        "subtitle": "You agree to these by using Terminus GPS services",
    }
    template_name = "terminusgps_notifications/terms.html"
    partial_template_name = "terminusgps_notifications/partials/_terms.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class PrivacyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Privacy Policy",
        "subtitle": "How we use your data",
    }
    http_method_names = ["get"]
    template_name = "terminusgps_notifications/privacy.html"
    partial_template_name = "terminusgps_notifications/partials/_privacy.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class LoginView(HtmxTemplateResponseMixin, LoginViewBase):
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
    }
    form_class = TerminusgpsNotificationsAuthenticationForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_notifications/partials/_login.html"
    success_url = reverse_lazy("terminusgps_notifications:dashboard")
    template_name = "terminusgps_notifications/login.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class LogoutView(HtmxTemplateResponseMixin, LogoutViewBase):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    template_name = "terminusgps_notifications/logged_out.html"
    partial_template_name = (
        "terminusgps_notifications/partials/_logged_out.html"
    )


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
class RegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
    }
    form_class = TerminusgpsNotificationsRegistrationForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_notifications/partials/_register.html"
    success_url = reverse_lazy("terminusgps_notifications:login")
    template_name = "terminusgps_notifications/register.html"

    @transaction.atomic
    def form_valid(
        self, form: TerminusgpsNotificationsRegistrationForm
    ) -> HttpResponse:
        user = form.save(commit=False)
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.email = form.cleaned_data["username"]
        user.save()
        customer = TerminusgpsNotificationsCustomer(user=user)
        if company := form.cleaned_data["company_name"]:
            customer.company = company
        customer.save()
        return HttpResponseRedirect(self.get_success_url())
