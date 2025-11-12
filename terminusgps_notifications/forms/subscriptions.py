from django import forms
from django.conf import settings
from terminusgps_payments.forms import (
    AddressProfileChoiceField,
    PaymentProfileChoiceField,
)
from terminusgps_payments.models import AddressProfile, PaymentProfile

WIDGET_CSS_CLASS = (
    settings.WIDGET_CSS_CLASS
    if hasattr(settings, "WIDGET_CSS_CLASS")
    else "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600"
)


class CustomerSubscriptionCreationForm(forms.Form):
    payment_profile = PaymentProfileChoiceField(
        queryset=PaymentProfile.objects.none(),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    address_profile = AddressProfileChoiceField(
        queryset=AddressProfile.objects.none(),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    consent = forms.BooleanField(
        initial=False,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700"}
        ),
    )
