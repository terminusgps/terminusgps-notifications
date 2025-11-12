from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from terminusgps_notifications.models import ExtensionPackage

WIDGET_CSS_CLASS = (
    settings.WIDGET_CSS_CLASS
    if hasattr(settings, "WIDGET_CSS_CLASS")
    else "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600"
)


class ExtensionPackageCreationForm(forms.ModelForm):
    class Meta:
        model = ExtensionPackage
        fields = ["customer"]
        widgets = {"customer": forms.widgets.HiddenInput()}


class TerminusgpsNotificationsAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].widget = forms.widgets.EmailInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "email@terminusgps.com",
                "autofocus": True,
                "enterkeyhint": "next",
                "inputmode": "email",
            }
        )
        self.fields["password"].widget = forms.widgets.PasswordInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "autocomplete": False,
                "inputmode": "text",
                "enterkeyhint": "done",
            }
        )


class TerminusgpsNotificationsRegistrationForm(BaseUserCreationForm):
    first_name = forms.CharField(
        help_text=_(
            "Required. 64 characters or fewer. Letters and digits only."
        ),
        label=_("First Name"),
        widget=forms.widgets.TextInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "First",
                "enterkeyhint": "next",
            }
        ),
    )
    last_name = forms.CharField(
        help_text=_(
            "Required. 64 characters or fewer. Letters and digits only."
        ),
        label=_("Last Name"),
        widget=forms.widgets.TextInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "Last",
                "enterkeyhint": "next",
            }
        ),
    )
    company_name = forms.CharField(
        label=_("Company Name"),
        help_text=_(
            "Optional. 64 characters or fewer. Letters and digits only."
        ),
        required=False,
        widget=forms.widgets.TextInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "Terminus GPS",
                "enterkeyhint": "next",
            }
        ),
    )
    consent = forms.BooleanField(
        initial=False,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700"}
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].validators.append(validate_email)
        self.fields["username"].widget = forms.widgets.TextInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "email@terminusgps.com",
                "enterkeyhint": "next",
            }
        )
        self.fields["password1"].widget = forms.widgets.PasswordInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "enterkeyhint": "next",
                "autocomplete": False,
            }
        )
        self.fields["password2"].widget = forms.widgets.PasswordInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "enterkeyhint": "done",
                "autocomplete": False,
            }
        )
