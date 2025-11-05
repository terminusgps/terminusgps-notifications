from django import forms
from django.conf import settings
from terminusgps_payments.models import AddressProfile, PaymentProfile

WIDGET_CSS_CLASS = (
    settings.WIDGET_CSS_CLASS
    if hasattr(settings, "WIDGET_CSS_CLASS")
    else "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600"
)


class PaymentProfileChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.credit_card is not None:
            cc = obj.credit_card
            return f"{cc.cardType} ending in {str(cc.cardNumber)[-4:]}"
        return str(obj)


class AddressProfileChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.address is not None:
            addr = obj.address
            return str(addr.address)
        return str(obj)


class CustomerSubscriptionCreationForm(forms.Form):
    payment_profile = PaymentProfileChoiceField(
        queryset=PaymentProfile.objects.all(),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    address_profile = AddressProfileChoiceField(
        queryset=AddressProfile.objects.all(),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    consent = forms.BooleanField(
        initial=False,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700"}
        ),
    )
