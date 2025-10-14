from django import forms

from terminusgps_notifications.models import WialonNotification


class WialonNotificationCreationForm(forms.ModelForm):
    class Meta:
        model = WialonNotification
        fields = [
            "name",
            "method",
            "deactivation_time",
            "max_alarms",
            "max_message_interval",
            "alarm_timeout",
            "control_period",
            "min_duration_alarm",
            "min_duration_prev",
            "language",
            "flags",
        ]
        widgets = {
            "name": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 invalid:bg-red-50 invalid:text-red-600"
                }
            ),
            "deactivation_time": forms.widgets.DateTimeInput(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
                }
            ),
            "method": forms.widgets.Select(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
                }
            ),
            "max_alarms": forms.widgets.TextInput(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600",
                    "size": 1,
                    "maxlength": 4,
                }
            ),
            "max_message_interval": forms.widgets.Select(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
                }
            ),
            "alarm_timeout": forms.widgets.TextInput(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600",
                    "size": 1,
                    "maxlength": 4,
                }
            ),
            "control_period": forms.widgets.Select(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
                }
            ),
            "min_duration_alarm": forms.widgets.TextInput(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600",
                    "size": 1,
                    "maxlength": 4,
                }
            ),
            "min_duration_prev": forms.widgets.TextInput(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600",
                    "size": 1,
                    "maxlength": 4,
                }
            ),
            "language": forms.widgets.Select(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
                }
            ),
            "flags": forms.widgets.Select(
                attrs={
                    "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
                }
            ),
        }
