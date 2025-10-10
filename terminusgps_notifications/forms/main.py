from django import forms
from django.utils.translation import gettext_lazy as _
from terminusgps_payments.models import AddressProfile, PaymentProfile

from terminusgps_notifications.constants import WialonUnitSensor
from terminusgps_notifications.models import WialonNotification


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


class SensorTriggerForm(forms.Form):
    lower_bound = forms.DecimalField(
        label="Lower bound",
        widget=forms.widgets.TextInput(
            attrs={"class": "p-2 border rounded bg-gray-50"}
        ),
    )
    merge = forms.ChoiceField(
        label="Similar sensors?",
        choices={(0, _("Calculate seperately")), (1, _("Sum up values"))},
        widget=forms.widgets.Select(
            attrs={"class": "p-2 border rounded bg-gray-50"}
        ),
    )
    prev_msg_diff = forms.BooleanField(
        label="Form boundaries according to the previous sensor value?",
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "terminusgps-red-700"}
        ),
        help_text="Check this box if you want boundaries calculated relative to the previous sensor value instead of the current sensor value.",
        required=False,
    )
    sensor_name_mask = forms.CharField(
        label="Sensor name",
        widget=forms.widgets.TextInput(
            attrs={"class": "p-2 border rounded bg-gray-50"}
        ),
    )
    sensor_type = forms.ChoiceField(
        label="Sensor type",
        choices=WialonUnitSensor.choices,
        widget=forms.widgets.Select(
            attrs={"class": "p-2 border rounded bg-gray-50"}
        ),
        required=False,
    )
    type = forms.ChoiceField(
        label="Trigger when",
        choices={(0, _("Value in range")), (1, _("Value out of range"))},
        widget=forms.widgets.Select(
            attrs={"class": "p-2 border rounded bg-gray-50"}
        ),
    )
    upper_bound = forms.CharField(
        label="Upper bound",
        widget=forms.widgets.TextInput(
            attrs={"class": "p-2 border rounded bg-gray-50"}
        ),
    )


class WialonNotificationCreationForm(forms.ModelForm):
    class Meta:
        model = WialonNotification
        fields = [
            "name",
            "method",
            "trigger",
            "activation_time",
            "deactivation_time",
            "max_alarms",
            "max_message_interval",
            "alarm_timeout",
            "control_period",
            "min_duration_alarm",
            "min_duration_prev",
            "language",
            "flags",
            "units",
        ]
        widgets = {
            "name": forms.widgets.TextInput(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "method": forms.widgets.Select(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "trigger": forms.widgets.Select(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "activation_time": forms.widgets.DateTimeInput(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "deactivation_time": forms.widgets.DateTimeInput(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "max_alarms": forms.widgets.NumberInput(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "max_message_interval": forms.widgets.Select(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "alarm_timeout": forms.widgets.NumberInput(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "control_period": forms.widgets.Select(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "min_duration_alarm": forms.widgets.NumberInput(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "min_duration_prev": forms.widgets.NumberInput(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "language": forms.widgets.Select(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
            "flags": forms.widgets.Select(
                attrs={"class": "p-2 border rounded bg-gray-50"}
            ),
        }


class CustomerSubscriptionCreationForm(forms.Form):
    payment_profile = PaymentProfileChoiceField(
        queryset=PaymentProfile.objects.all(),
        widget=forms.widgets.Select(
            attrs={"class": "border bg-gray-50 rounded p-2"}
        ),
    )
    address_profile = AddressProfileChoiceField(
        queryset=AddressProfile.objects.all(),
        widget=forms.widgets.Select(
            attrs={"class": "border bg-gray-50 rounded p-2"}
        ),
    )
    consent = forms.BooleanField(
        initial=False,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700"}
        ),
    )
