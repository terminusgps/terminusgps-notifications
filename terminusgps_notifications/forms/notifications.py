from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from terminusgps_notifications import constants
from terminusgps_notifications.models import WialonNotification

WIDGET_CSS_CLASS = (
    settings.WIDGET_CSS_CLASS
    if hasattr(settings, "WIDGET_CSS_CLASS")
    else "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600"
)


class WialonUnitSelectForm(forms.Form):
    resource_id = forms.TypedChoiceField(
        choices=[],
        coerce=int,
        help_text=_("Select a resource from the list."),
        label=_("Resource"),
        widget=forms.widgets.Select(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "autofocus": True,
                "hx-get": reverse_lazy("terminusgps_notifications:units form"),
                "hx-indicator": "#unit_list_indicator",
                "hx-select": "#id_unit_list",
                "hx-swap": "outerHTML",
                "hx-target": "#id_unit_list",
                "hx-trigger": "change",
                "hx-include": "this,[name='items_type']",
            }
        ),
    )
    unit_list = forms.TypedMultipleChoiceField(
        choices=[],
        coerce=int,
        help_text=_(
            "Select units or unit groups from the list. Ctrl+click to select multiple. Cmd+click on Mac."
        ),
        label=_("Units/Unit Groups"),
        widget=forms.widgets.SelectMultiple(attrs={"class": WIDGET_CSS_CLASS}),
    )


class WialonNotificationUpdateForm(forms.ModelForm):
    class Meta:
        model = WialonNotification
        fields = [
            "name",
            "message",
            "method",
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
        ]
        help_texts = {
            "message": "Provide a message to send to the destination phone number."
        }
        widgets = {
            # Required fields
            "name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "New Notification",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                }
            ),
            "message": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "Hello, there!",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                }
            ),
            "method": forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
            # Advanced fields
            "activation_time": forms.widgets.DateTimeInput(
                attrs={"class": WIDGET_CSS_CLASS}
            ),
            "deactivation_time": forms.widgets.DateTimeInput(
                attrs={"class": WIDGET_CSS_CLASS}
            ),
            "max_alarms": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "max_message_interval": forms.widgets.Select(
                attrs={"class": WIDGET_CSS_CLASS}
            ),
            "alarm_timeout": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "control_period": forms.widgets.Select(
                attrs={"class": WIDGET_CSS_CLASS}
            ),
            "min_duration_alarm": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "min_duration_prev": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "language": forms.widgets.Select(
                attrs={"class": WIDGET_CSS_CLASS}
            ),
            "flags": forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
        }


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
            "schedule",
            "control_schedule",
            "unit_list",
            "resource_id",
            "trigger_type",
            "trigger_parameters",
        ]
        help_texts = {
            "method": "Select whether to text the message (sms) or read the message aloud (voice) on notification trigger.",
            "message": "Provide a message to send to the destination phone number.",
        }
        widgets = {
            # Required fields
            "name": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "New Notification",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                }
            ),
            "message": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "placeholder": "Hello, there!",
                    "enterkeyhint": "next",
                    "inputmode": "text",
                }
            ),
            "method": forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
            # Advanced fields
            "activation_time": forms.widgets.DateTimeInput(
                attrs={"class": WIDGET_CSS_CLASS}
            ),
            "deactivation_time": forms.widgets.DateTimeInput(
                attrs={"class": WIDGET_CSS_CLASS}
            ),
            "max_alarms": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "max_message_interval": forms.widgets.Select(
                attrs={"class": WIDGET_CSS_CLASS}
            ),
            "alarm_timeout": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "control_period": forms.widgets.Select(
                attrs={"class": WIDGET_CSS_CLASS}
            ),
            "min_duration_alarm": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "min_duration_prev": forms.widgets.TextInput(
                attrs={
                    "class": WIDGET_CSS_CLASS,
                    "size": 1,
                    "maxlength": 4,
                    "inputmode": "decimal",
                }
            ),
            "language": forms.widgets.Select(
                attrs={"class": WIDGET_CSS_CLASS}
            ),
            "flags": forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
            # Hidden fields
            "schedule": forms.widgets.HiddenInput(),
            "control_schedule": forms.widgets.HiddenInput(),
            "timezone": forms.widgets.HiddenInput(),
            "unit_list": forms.widgets.HiddenInput(),
            "resource_id": forms.widgets.HiddenInput(),
            "trigger_type": forms.widgets.HiddenInput(),
            "trigger_parameters": forms.widgets.HiddenInput(),
        }


class TriggerForm(forms.Form):
    """Parent form for selecting/saving a notification trigger configuration."""

    t = forms.ChoiceField(
        choices=constants.WialonNotificationTriggerType.choices,
        help_text=_("Select a trigger from the list."),
        initial=constants.WialonNotificationTriggerType.SENSOR,
        label=_("Trigger type"),
        widget=forms.widgets.Select(
            {
                "class": WIDGET_CSS_CLASS,
                "hx-target": "#id_p",
                "hx-trigger": "load once, change",
                "hx-swap": "outerHTML",
                "hx-get": reverse_lazy(
                    "terminusgps_notifications:trigger parameters form"
                ),
            }
        ),
    )
    """Trigger type."""
    p = forms.JSONField(
        widget=forms.widgets.Textarea(attrs={"class": "hidden"})
    )
    """Trigger parameters."""
    resource_id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    unit_list = forms.JSONField(widget=forms.widgets.HiddenInput())


class GeofenceTriggerParametersForm(forms.Form):
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices,
        help_text=_("Select the sensor type from the list."),
        initial=constants.WialonUnitSensorType.ANY,
        label=_("Sensor type"),
        required=False,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    sensor_name_mask = forms.CharField(
        help_text=_("Enter a mask for the sensor name. Ex: *IGNITION*"),
        initial="*",
        label=_("Sensor mask"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    lower_bound = forms.FloatField(
        help_text=_(
            "Enter a lower bound for the sensor value. Decimal places are allowed."
        ),
        initial=-1.0,
        label=_("Lower bound"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    upper_bound = forms.FloatField(
        help_text=_(
            "Enter an upper bound for the sensor value. Decimal places are allowed."
        ),
        initial=1.0,
        label=_("Upper bound"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    prev_msg_diff = forms.TypedChoiceField(
        choices=[
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ],
        coerce=int,
        label=_("Boundary formation"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    geozone_ids = forms.CharField(
        help_text=_("Enter a comma-separated list of geofence IDs."),
        label=_("Geofence IDs"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    min_speed = forms.IntegerField(
        help_text=_("Enter a minimum speed in kilometers per hour."),
        initial=0,
        label=_("Minimum speed (km/h)"),
        max_value=256,
        min_value=0,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    max_speed = forms.IntegerField(
        help_text=_("Enter a maximum speed in kilometers per hour."),
        initial=256,
        label=_("Maximum speed (km/h)"),
        max_value=256,
        min_value=0,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    merge = forms.TypedChoiceField(
        choices=[(0, _("Calculate separately")), (1, _("Sum up values"))],
        coerce=int,
        initial=0,
        label=_("Similar sensors"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    reversed = forms.TypedChoiceField(
        choices=[
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ],
        coerce=int,
        initial=0,
        label=_("Boundaries"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    type = forms.TypedChoiceField(
        choices=[
            (0, _("Entering geofence(s)")),
            (1, _("Exiting geofence(s)")),
        ],
        coerce=int,
        initial=0,
        label=_("Trigger when"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    include_lbs = forms.TypedChoiceField(
        choices=[(0, _("Disabled")), (1, _("Enabled"))],
        coerce=int,
        initial=0,
        label=_("Process LBS messages"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    lo = forms.ChoiceField(
        choices=[("", "None"), ("AND", _("AND")), ("OR", _("OR"))],
        initial="",
        label=_("Logical operator"),
        required=False,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


class AddressTriggerParametersForm(forms.Form):
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices,
        help_text=_("Select the sensor type from the list."),
        initial=constants.WialonUnitSensorType.ANY,
        label=_("Sensor type"),
        required=False,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    sensor_name_mask = forms.CharField(
        label=_("Sensor mask"),
        initial="*",
        help_text=_("Enter a mask for the sensor name. Ex: *IGNITION*"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    lower_bound = forms.FloatField(
        help_text=_(
            "Enter a lower bound for the sensor value. Decimal places are allowed."
        ),
        initial=-1,
        label=_("Lower bound"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    upper_bound = forms.FloatField(
        help_text=_(
            "Enter an upper bound for the sensor value. Decimal places are allowed."
        ),
        initial=1,
        label=_("Upper bound"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    prev_msg_diff = forms.TypedChoiceField(
        choices=[
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ],
        coerce=int,
        label=_("Boundary formation"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    merge = forms.TypedChoiceField(
        choices=[(0, _("Calculate separately")), (1, _("Sum up values"))],
        coerce=int,
        initial=0,
        label=_("Similar sensors"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    reversed = forms.TypedChoiceField(
        choices=[
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ],
        coerce=int,
        initial=0,
        label=_("Boundaries"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    radius = forms.IntegerField(
        initial=500,
        label=_("Radius (m)"),
        help_text=_("Enter a radius in meters originating from the address."),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    type = forms.TypedChoiceField(
        choices=[
            (0, _("In the address radius")),
            (1, _("Out of the address radius")),
        ],
        coerce=int,
        initial=0,
        label=_("Control type"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    min_speed = forms.IntegerField(
        help_text=_("Enter a minimum speed in kilometers per hour."),
        initial=0,
        label=_("Minimum speed (km/h)"),
        max_value=256,
        min_value=0,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    max_speed = forms.IntegerField(
        help_text=_("Enter a maximum speed in kilometers per hour."),
        initial=256,
        label=_("Maximum speed (km/h)"),
        max_value=256,
        min_value=0,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    country = forms.CharField(
        help_text=_("Enter a country."),
        label=_("Country"),
        max_length=64,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    region = forms.CharField(
        help_text=_("Enter a region (state/province)."),
        label=_("Region"),
        max_length=64,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    city = forms.CharField(
        help_text=_("Enter a city."),
        label=_("City"),
        max_length=64,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    street = forms.CharField(
        help_text=_("Enter a street."),
        label=_("Street"),
        max_length=64,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    house = forms.CharField(
        help_text=_("Enter a house/street number."),
        label=_("House"),
        max_length=64,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    include_lbs = forms.TypedChoiceField(
        choices=[(0, _("Disabled")), (1, _("Enabled"))],
        coerce=int,
        initial=0,
        label=_("Process LBS messages"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


class SpeedTriggerParametersForm(forms.Form):
    lower_bound = forms.FloatField(
        help_text=_(
            "Enter a lower bound for the sensor value. Decimal places are allowed."
        ),
        initial=-1,
        label=_("Lower bound"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    max_speed = forms.IntegerField(
        help_text=_("Enter a maximum speed in kilometers per hour."),
        initial=256,
        label=_("Maximum speed"),
        max_value=256,
        min_value=0,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    merge = forms.TypedChoiceField(
        label=_("Similar sensors"),
        initial=0,
        choices=[(0, _("Calculate separately")), (1, _("Sum up values"))],
        coerce=int,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    min_speed = forms.IntegerField(
        help_text=_("Enter a minimum speed in kilometers per hour."),
        initial=0,
        label=_("Minimum speed (km/h)"),
        max_value=256,
        min_value=0,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    prev_msg_diff = forms.TypedChoiceField(
        label=_("Boundaries"),
        choices=[
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ],
        coerce=int,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    reversed = forms.TypedChoiceField(
        choices=[
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ],
        coerce=int,
        initial=0,
        label=_("Boundaries"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    sensor_name_mask = forms.CharField(
        help_text=_("Enter a mask for the sensor name. Ex: *IGNITION*"),
        initial="*",
        label=_("Sensor mask"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices,
        help_text=_("Select the sensor type from the list."),
        initial=constants.WialonUnitSensorType.ANY,
        label=_("Sensor type"),
        required=False,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    upper_bound = forms.FloatField(
        help_text=_(
            "Enter an upper bound for the sensor value. Decimal places are allowed."
        ),
        initial=1,
        label=_("Upper bound"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )


class AlarmTriggerParametersForm(forms.Form):
    pass


class DigitalTriggerParametersForm(forms.Form):
    input_index = forms.IntegerField(
        help_text=_(
            "Enter the index of the digital input. Digits 1-32 are allowed."
        ),
        label=_("Digital input"),
        max_value=32,
        min_value=1,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    type = forms.TypedChoiceField(
        choices=[(0, _("On activation")), (1, _("On deactivation"))],
        coerce=int,
        label=_("Trigger when"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


class ParameterTriggerParametersForm(forms.Form):
    kind = forms.TypedChoiceField(
        choices=[
            (0, _("Value range")),
            (1, _("Text mask")),
            (2, _("Parameter availability")),
            (3, _("Parameter lack")),
        ],
        coerce=int,
        help_text=_("Select a parameter type from the list."),
        initial=0,
        label=_("Control type"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    lower_bound = forms.FloatField(
        help_text=_(
            "Enter a lower bound for the sensor value. Decimal places are allowed."
        ),
        label=_("Lower bound"),
        initial=-1,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    param = forms.CharField(
        label=_("Parameter name"),
        help_text=_("Enter the name of the parameter."),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    text_mask = forms.CharField(
        initial="*",
        label=_("Parameter text mask"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
        help_text=_("Enter a wildcard based text mask."),
    )
    type = forms.TypedChoiceField(
        choices=[
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ],
        coerce=int,
        initial=0,
        label=_("Trigger when"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    upper_bound = forms.FloatField(
        help_text=_(
            "Enter an upper bound for the sensor value. Decimal places are allowed."
        ),
        label=_("Upper bound"),
        initial=1,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )


class SensorValueTriggerParametersForm(forms.Form):
    lower_bound = forms.FloatField(
        help_text=_(
            "Enter a lower bound for the sensor value. Decimal places are allowed."
        ),
        label=_("Lower bound"),
        initial=-1,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    upper_bound = forms.FloatField(
        help_text=_(
            "Enter an upper bound for the sensor value. Decimal places are allowed."
        ),
        label=_("Upper bound"),
        initial=1,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    merge = forms.TypedChoiceField(
        label=_("Similar sensors"),
        initial=0,
        choices=[(0, _("Calculate separately")), (1, _("Sum up values"))],
        coerce=int,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    prev_msg_diff = forms.TypedChoiceField(
        choices=[
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ],
        coerce=int,
        initial=0,
        label=_("Boundaries"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    sensor_name_mask = forms.CharField(
        help_text=_("Enter a mask for the sensor name. Ex: *IGNITION*"),
        initial="*",
        label=_("Sensor mask"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices,
        help_text=_("Select the sensor type from the list."),
        initial=constants.WialonUnitSensorType.ANY,
        label=_("Sensor type"),
        required=False,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    type = forms.TypedChoiceField(
        coerce=int,
        initial=0,
        choices=[
            (0, _("Sensor value in-range")),
            (1, _("Sensor value out-of-range")),
        ],
        label=_("Trigger when"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )

    def clean(self) -> None:
        cleaned_data = super().clean()
        upper_bound = cleaned_data.get("upper_bound")
        lower_bound = cleaned_data.get("lower_bound")
        if upper_bound is not None and lower_bound is not None:
            if lower_bound > upper_bound:
                self.add_error(
                    "lower_bound",
                    ValidationError(
                        _(
                            "Lower bound cannot be greater than upper bound (%(lower_bound)s > %(upper_bound)s)."
                        ),
                        params={
                            "lower_bound": float(lower_bound),
                            "upper_bound": float(upper_bound),
                        },
                    ),
                )
            elif upper_bound < lower_bound:
                self.add_error(
                    "upper_bound",
                    ValidationError(
                        _(
                            "Upper bound cannot be less than lower bound (%(upper_bound)s < %(lower_bound)s)."
                        ),
                        params={
                            "lower_bound": float(lower_bound),
                            "upper_bound": float(upper_bound),
                        },
                    ),
                )


class OutageTriggerParametersForm(forms.Form):
    time = forms.IntegerField(
        help_text=_("Enter the time (in seconds) between outages."),
        initial=3,
        label=_("Time interval (sec)"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    type = forms.TypedChoiceField(
        label=_("Control type"),
        choices=[(0, _("Coordinates loss")), (1, _("Connection loss"))],
        coerce=int,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    include_lbs = forms.TypedChoiceField(
        choices=[(0, _("Disabled")), (1, _("Enabled"))],
        coerce=int,
        initial=0,
        label=_("Process LBS messages"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    check_restore = forms.TypedChoiceField(
        coerce=int,
        choices=[
            (0, _("Connection lost")),
            (1, _("Connection lost and restored")),
            (2, _("Connection restored")),
        ],
        label=_("Notify when"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    geozones_list = forms.CharField(
        label=_("Geofence IDs"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    geozones_type = forms.TypedChoiceField(
        choices=[(0, _("Out of geofence")), (1, _("In geofence"))],
        coerce=int,
        label=_("Geofence control type"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


class InterpositionTriggerParametersForm(forms.Form):
    sensor_name_mask = forms.CharField(
        help_text=_("Enter a mask for the sensor name. Ex: *IGNITION*"),
        initial="*",
        label=_("Sensor mask"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices,
        help_text=_("Select the sensor type from the list."),
        initial=constants.WialonUnitSensorType.ANY,
        label=_("Sensor type"),
        required=False,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    lower_bound = forms.FloatField(
        help_text=_(
            "Enter a lower bound for the sensor value. Decimal places are allowed."
        ),
        label=_("Lower bound"),
        initial=-1,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    upper_bound = forms.FloatField(
        help_text=_(
            "Enter an upper bound for the sensor value. Decimal places are allowed."
        ),
        label=_("Upper bound"),
        initial=1,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    merge = forms.TypedChoiceField(
        label=_("Similar sensors"),
        initial=0,
        choices=[(0, _("Calculate separately")), (1, _("Sum up values"))],
        coerce=int,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    max_speed = forms.IntegerField(
        help_text=_("Enter a maximum speed in kilometers per hour."),
        initial=256,
        label=_("Maximum speed (km/h)"),
        max_value=256,
        min_value=0,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    min_speed = forms.IntegerField(
        help_text=_("Enter a minimum speed in kilometers per hour."),
        initial=0,
        label=_("Minimum speed (km/h)"),
        max_value=256,
        min_value=0,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    reversed = forms.TypedChoiceField(
        choices=[
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ],
        coerce=int,
        initial=0,
        label=_("Boundaries"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    prev_msg_diff = forms.TypedChoiceField(
        choices=[
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ],
        coerce=int,
        label=_("Boundary formation"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    radius = forms.IntegerField(
        initial=500,
        label=_("Radius (m)"),
        help_text=_(
            "Enter a radius in meters originating from the interposition."
        ),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    type = forms.TypedChoiceField(
        choices=[
            (0, _("Moving toward unit(s)")),
            (1, _("Moving away from unit(s)")),
        ],
        coerce=int,
        initial=0,
        label=_("Trigger when"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    unit_guids = forms.CharField(
        label=_("Unit IDs"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
        help_text=_("Enter a comma-separated list of unit IDs."),
    )
    include_lbs = forms.TypedChoiceField(
        choices=[(0, _("Disabled")), (1, _("Enabled"))],
        coerce=int,
        initial=0,
        label=_("Process LBS messages"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    lo = forms.ChoiceField(
        choices=[("", "None"), ("AND", _("AND")), ("OR", _("OR"))],
        initial="",
        label=_("Logical operator"),
        required=False,
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


class ExcessTriggerParametersForm(forms.Form):
    flags = forms.TypedChoiceField(
        choices=[(1, _("Data messages")), (2, _("SMS messages"))],
        coerce=int,
        initial=1,
        label=_("Message type"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    msgs_limit = forms.IntegerField(
        label=_("Message limit"),
        initial=0,
        help_text=_(
            "Enter the maximum number of messages allowed before they're considered 'excess'."
        ),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    time_offset = forms.IntegerField(
        help_text=_(
            "Enter the interval (in seconds) to reset the counter on."
        ),
        initial=60,
        label=_("Reset interval (sec)"),
        max_value=86400,
        min_value=1,
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )


class RouteTriggerParametersForm(forms.Form):
    mask = forms.CharField(
        label=_("Route name mask"),
        initial="*",
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
        help_text=_("Enter a mask for the route name. Ex: *MY AWESOME ROUTE*"),
    )
    round_mask = forms.CharField(
        label=_("Ride name mask"),
        initial="*",
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
        help_text=_("Enter a mask for the ride name. Ex: *MY AWESOME RIDE*"),
    )
    schedule_mask = forms.CharField(
        label=_("Schedule name mask"),
        initial="*",
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
        help_text=_(
            "Enter a mask for the route schedule name. Ex: *MY AWESOME SCHEDULE*"
        ),
    )
    # TODO: forms.MultipleChoiceField implementation of the below field
    types = forms.CharField(
        label=_("Route control types"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )


class DriverTriggerParametersForm(forms.Form):
    driver_code_mask = forms.CharField(
        initial="*",
        label=_("Driver code mask"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
        help_text=_("Enter a mask for the driver code. Ex: *DRIVER NAME*"),
    )
    flags = forms.TypedChoiceField(
        choices=[(1, _("Driver assignment")), (2, _("Driver separation"))],
        coerce=int,
        initial=1,
        label=_("Trigger on"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


class TrailerTriggerParametersForm(forms.Form):
    driver_code_mask = forms.CharField(
        initial="*",
        label=_("Trailer code mask"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
        help_text=_("Enter a mask for the trailer code. Ex: *TRAILER NAME*"),
    )
    flags = forms.TypedChoiceField(
        choices=[(1, _("Trailer assignment")), (2, _("Trailer separation"))],
        coerce=int,
        initial=1,
        label=_("Trigger on"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


class MaintenanceTriggerParametersForm(forms.Form):
    days = forms.IntegerField(
        initial=1,
        label=_("Days interval"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    engine_hours = forms.IntegerField(
        help_text=_("Enter the engine hours interval in hours."),
        initial=1,
        label=_("Engine hours interval (h)"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    flags = forms.TypedChoiceField(
        choices=[
            (0, _("Control all service intervals")),
            (1, _("Mileage interval")),
            (2, _("Engine hours interval")),
            (4, _("Days interval")),
        ],
        coerce=int,
        initial=0,
        label=_("Control flags"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    mask = forms.CharField(
        help_text=_("Enter a wildcard based mask. Ex: *MAINTENANCE*"),
        initial="*",
        label=_("Mask"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    mileage = forms.IntegerField(
        help_text=_("Enter the mileage interval in kilometers."),
        initial=1,
        label=_("Mileage interval (km)"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    val = forms.TypedChoiceField(
        choices=[
            (1, _("Service term approaches")),
            (-1, _("Service term is expired")),
        ],
        coerce=int,
        initial=1,
        label=_("Notify when"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


class FuelTriggerParametersForm(forms.Form):
    sensor_name_mask = forms.CharField(
        help_text=_("Enter a mask for the sensor name. Ex: *IGNITION*"),
        initial="*",
        label=_("Sensor mask"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    geozones_type = forms.TypedChoiceField(
        choices=[(0, _("Disabled/Out of geofence")), (1, _("In geofence"))],
        coerce=int,
        label=_("Geofence control type"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    geozones_list = forms.CharField(
        help_text=_("Enter a comma-separated list of geofence IDs."),
        label=_("Geofence IDs"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    realtime_only = forms.TypedChoiceField(
        choices=[(0, _("Disable")), (1, _("Enable"))],
        coerce=int,
        initial=0,
        label=_("Ignore the recalculation of historical data?"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


class FuelDrainTriggerParametersForm(forms.Form):
    sensor_name_mask = forms.CharField(
        label=_("Sensor mask"),
        initial="*",
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    geozones_type = forms.TypedChoiceField(
        choices=[(0, _("Disabled/Out of geofence")), (1, _("In geofence"))],
        coerce=int,
        label=_("Geofence control type"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    geozones_list = forms.CharField(
        help_text=_("Enter a comma-separated list of geofence IDs."),
        label=_("Geofence IDs"),
        widget=forms.widgets.TextInput(attrs={"class": WIDGET_CSS_CLASS}),
    )
    realtime_only = forms.TypedChoiceField(
        choices=[(0, _("Disable")), (1, _("Enable"))],
        coerce=int,
        initial=0,
        label=_("Ignore the recalculation of historical data?"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


class HealthTriggerParametersForm(forms.Form):
    healthy = forms.TypedChoiceField(
        choices=[(0, _("Disabled")), (1, _("Enabled"))],
        coerce=int,
        help_text=_(
            "Enable this option to trigger the notification when the device is reported healthy."
        ),
        initial=1,
        label=_("Trigger when the device is healthy"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    unhealthy = forms.TypedChoiceField(
        choices=[(0, _("Disabled")), (1, _("Enabled"))],
        coerce=int,
        help_text=_(
            "Enable this option to trigger the notification when the device is reported unhealthy."
        ),
        initial=0,
        label=_("Trigger when the device is unhealthy"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    needAttention = forms.TypedChoiceField(
        choices=[(0, _("Disabled")), (1, _("Enabled"))],
        coerce=int,
        help_text=_(
            "Enable this option to trigger the notification when the device reports it needs attention."
        ),
        initial=0,
        label=_("Trigger when the device needs attention"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )
    triggerForEachIncident = forms.TypedChoiceField(
        choices=[(0, _("Disabled")), (1, _("Enabled"))],
        coerce=int,
        help_text=_(
            "Enable this option to trigger the notification when the device reports any incident."
        ),
        initial=0,
        label=_("Trigger for each incident"),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
    )


TRIGGER_FORM_MAP = {
    constants.WialonNotificationTriggerType.GEOFENCE: GeofenceTriggerParametersForm,
    constants.WialonNotificationTriggerType.ADDRESS: AddressTriggerParametersForm,
    constants.WialonNotificationTriggerType.SPEED: SpeedTriggerParametersForm,
    constants.WialonNotificationTriggerType.ALARM: AlarmTriggerParametersForm,
    constants.WialonNotificationTriggerType.DIGITAL: DigitalTriggerParametersForm,
    constants.WialonNotificationTriggerType.PARAMETER: ParameterTriggerParametersForm,
    constants.WialonNotificationTriggerType.SENSOR: SensorValueTriggerParametersForm,
    constants.WialonNotificationTriggerType.OUTAGE: OutageTriggerParametersForm,
    constants.WialonNotificationTriggerType.INTERPOSITION: InterpositionTriggerParametersForm,
    constants.WialonNotificationTriggerType.EXCESS: ExcessTriggerParametersForm,
    constants.WialonNotificationTriggerType.ROUTE: RouteTriggerParametersForm,
    constants.WialonNotificationTriggerType.DRIVER: DriverTriggerParametersForm,
    constants.WialonNotificationTriggerType.TRAILER: TrailerTriggerParametersForm,
    constants.WialonNotificationTriggerType.MAINTENANCE: MaintenanceTriggerParametersForm,
    constants.WialonNotificationTriggerType.FUEL: FuelTriggerParametersForm,
    constants.WialonNotificationTriggerType.FUEL_DRAIN: FuelDrainTriggerParametersForm,
    constants.WialonNotificationTriggerType.HEALTH: HealthTriggerParametersForm,
}
