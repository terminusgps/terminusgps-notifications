from django import forms

from terminusgps_notifications.models import WialonNotification


class WialonNotificationCreationForm(forms.ModelForm):
    class Meta:
        model = WialonNotification
        fields = [
            "name",
            "message",
            "method",
            "timezone",
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
            "customer",
            "trigger",
            "unit_list",
            "schedule",
            "control_schedule",
        ]
        help_texts = {
            "message": "Enter a message. You may use the Wialon tags detailed below."
        }
        widgets = {
            # Required fields
            "name": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600",
                    "placeholder": "New Notification",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                }
            ),
            "message": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600",
                    "placeholder": "Hello! At %MSG_TIME%, your vehicle %UNIT% entered %ZONE%.",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                }
            ),
            "method": forms.widgets.Select(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
                }
            ),
            # Advanced fields
            "activation_time": forms.widgets.DateTimeInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
                }
            ),
            "deactivation_time": forms.widgets.DateTimeInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
                }
            ),
            "max_alarms": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600",
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "max_message_interval": forms.widgets.Select(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
                }
            ),
            "alarm_timeout": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600",
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "control_period": forms.widgets.Select(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
                }
            ),
            "min_duration_alarm": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600",
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "min_duration_prev": forms.widgets.TextInput(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600",
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "language": forms.widgets.Select(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
                }
            ),
            "flags": forms.widgets.Select(
                attrs={
                    "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
                }
            ),
            # Hidden fields
            "customer": forms.widgets.HiddenInput(),
            "trigger": forms.widgets.HiddenInput(),
            "unit_list": forms.widgets.HiddenInput(),
            "schedule": forms.widgets.HiddenInput(),
            "control_schedule": forms.widgets.HiddenInput(),
            "timezone": forms.widgets.HiddenInput(),
        }
