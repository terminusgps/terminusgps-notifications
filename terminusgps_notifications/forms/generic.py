from django import forms
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm
from django.core.validators import validate_email


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
