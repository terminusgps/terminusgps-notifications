from django import forms

from terminusgps_notifications.models import WialonNotification


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
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 order-2 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
                }
            ),
            "method": forms.widgets.Select(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 order-2 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
                }
            ),
            "units": forms.widgets.SelectMultiple(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 order-2 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
                }
            ),
        }
