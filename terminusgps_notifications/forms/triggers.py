from django import forms
from django.utils.translation import gettext_lazy as _

from .. import constants


class GeofenceTriggerForm(forms.Form):
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices
    )
    sensor_name_mask = forms.CharField()
    lower_bound = forms.DecimalField()
    upper_bound = forms.DecimalField()
    prev_msg_diff = forms.ChoiceField(
        choices=(
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        )
    )
    merge = forms.ChoiceField()
    reversed = forms.ChoiceField()
    geozone_ids = forms.CharField()
    type = forms.ChoiceField()
    min_speed = forms.IntegerField()
    max_speed = forms.IntegerField()
    include_lbs = forms.ChoiceField()
    lo = forms.CharField()


class AddressTriggerForm(forms.Form):
    city = forms.CharField()
    country = forms.CharField()
    house = forms.CharField()
    include_lbs = forms.ChoiceField()
    lower_bound = forms.DecimalField()
    max_speed = forms.IntegerField()
    merge = forms.ChoiceField()
    min_speed = forms.IntegerField()
    prev_msg_diff = forms.ChoiceField(
        choices=(
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        )
    )
    radius = forms.IntegerField()
    region = forms.CharField()
    reversed = forms.ChoiceField()
    sensor_name_mask = forms.CharField()
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices
    )
    street = forms.CharField()
    type = forms.ChoiceField()
    upper_bound = forms.DecimalField()


class SpeedTriggerForm(forms.Form):
    lower_bound = forms.DecimalField()
    max_speed = forms.IntegerField()
    merge = forms.ChoiceField()
    min_speed = forms.IntegerField()
    prev_msg_diff = forms.ChoiceField(
        choices=(
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        )
    )
    reversed = forms.ChoiceField()
    sensor_name_mask = forms.CharField()
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices
    )
    upper_bound = forms.IntegerField()


class AlarmTriggerForm(forms.Form):
    pass


class DigitalTriggerForm(forms.Form):
    input_index = forms.IntegerField(min_value=1, max_value=32)
    type = forms.ChoiceField(
        choices=(
            (0, _("Check for activation")),
            (1, _("Check for deactivation")),
        )
    )


class ParameterTriggerForm(forms.Form):
    kind = forms.ChoiceField(
        choices=(
            (0, _("Value range")),
            (1, _("Text mask")),
            (2, _("Parameter availability")),
            (3, _("Parameter lack")),
        )
    )
    lower_bound = forms.DecimalField()
    param = forms.CharField()
    text_mask = forms.CharField()
    type = forms.ChoiceField(
        choices=(
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        )
    )
    upper_bound = forms.DecimalField()


class SensorValueTriggerForm(forms.Form):
    lower_bound = forms.DecimalField(
        label="Sensor value upper bound:",
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
            }
        ),
    )
    upper_bound = forms.DecimalField(
        label="Sensor value lower bound:",
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
            }
        ),
    )
    merge = forms.ChoiceField(
        label="Similar sensors:",
        choices={(0, _("Calculate separately")), (1, _("Sum up values"))},
        widget=forms.widgets.Select(
            attrs={
                "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
            }
        ),
    )
    prev_msg_diff = forms.ChoiceField(
        label="Form boundaries according to previous or absolute value?",
        choices=(
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ),
        widget=forms.widgets.Select(
            attrs={
                "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
            }
        ),
    )
    sensor_name_mask = forms.CharField(
        label="Sensor name mask",
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
            }
        ),
    )
    sensor_type = forms.ChoiceField(
        label="Sensor type:",
        choices=constants.WialonUnitSensorType.choices,
        required=False,
        widget=forms.widgets.Select(
            attrs={
                "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
            }
        ),
    )
    type = forms.ChoiceField(
        label="Trigger when:",
        choices={(0, _("In Range")), (1, _("Out of Range"))},
        widget=forms.widgets.Select(
            attrs={
                "class": "p-2 rounded border border-current bg-gray-50 group-has-[.errorlist]:bg-red-50 group-has-[.errorlist]:text-red-600"
            }
        ),
    )


class OutageTriggerForm(forms.Form):
    check_restore = forms.ChoiceField(
        choices=(
            (0, _("Connection lost")),
            (1, _("Connection lost and restored")),
            (2, _("Connection restored")),
        )
    )
    geozones_list = forms.CharField()
    geozones_type = forms.ChoiceField(
        choices=((0, _("Out of geofence")), (1, _("In geofence")))
    )
    include_lbs = forms.BooleanField()
    time = forms.IntegerField()
    type = forms.ChoiceField(
        choices=((0, _("Coordinates loss")), (1, _("Connection loss")))
    )


class InterpositionTriggerForm(forms.Form):
    include_lbs = forms.BooleanField()
    lo = forms.ChoiceField(
        choices=(("AND", _("Logical AND")), ("OR", _("Logical OR")))
    )
    lower_bound = forms.DecimalField()
    max_speed = forms.IntegerField()
    merge = forms.ChoiceField(
        choices=((0, _("Calculate separately")), (1, _("Sum up values")))
    )
    min_speed = forms.IntegerField()
    prev_msg_diff = forms.ChoiceField(
        choices=(
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        )
    )
    radius = forms.IntegerField()
    reversed = forms.ChoiceField(
        choices=(
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        )
    )
    sensor_name_mask = forms.CharField()
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices
    )
    type = forms.ChoiceField(
        choices=(
            (0, _("Control approaching to units")),
            (1, _("Control moving away from units")),
        )
    )
    unit_guids = forms.CharField()
    upper_bound = forms.DecimalField()


class ExcessTriggerForm(forms.Form):
    flags = forms.ChoiceField(
        choices=((1, _("Data messages")), (2, _("SMS messages")))
    )
    msgs_limit = forms.IntegerField()
    time_offset = forms.IntegerField()


class RouteTriggerForm(forms.Form):
    mask = forms.CharField()
    round_mask = forms.CharField()
    schedule_mask = forms.CharField()
    types = forms.CharField()


class DriverTriggerForm(forms.Form):
    driver_code_mask = forms.CharField()
    flags = forms.ChoiceField(
        choices=((1, _("Driver assignment")), (2, _("Driver separation")))
    )


class TrailerTriggerForm(forms.Form):
    driver_code_mask = forms.CharField()
    flags = forms.ChoiceField(
        choices=((1, _("Trailer assignment")), (2, _("Trailer separation")))
    )


class MaintenanceTriggerForm(forms.Form):
    days = forms.IntegerField()
    engine_hours = forms.IntegerField()
    flags = forms.ChoiceField(
        choices=(
            (0, _("Control all service intervals")),
            (1, _("Mileage interval")),
            (2, _("Engine hours interval")),
            (4, _("Days interval")),
        )
    )
    mask = forms.CharField()
    mileage = forms.IntegerField()
    val = forms.ChoiceField(
        choices=(
            (1, _("Notify when service term approaches")),
            (-1, _("Notify when service term is expired")),
        )
    )


class FuelTriggerForm(forms.Form):
    sensor_name_mask = forms.CharField()
    geozones_type = forms.ChoiceField(
        choices=(
            (0, _("Disabled/outside geofence")),
            (1, _("Inside geofence")),
        )
    )
    geozones_list = forms.CharField()
    realtime_only = forms.BooleanField()


class FuelDrainTriggerForm(forms.Form):
    sensor_name_mask = forms.CharField()
    geozones_type = forms.ChoiceField(
        choices=(
            (0, _("Disabled/outside geofence")),
            (1, _("Inside geofence")),
        )
    )
    geozones_list = forms.CharField()
    realtime_only = forms.BooleanField()


class HealthTriggerForm(forms.Form):
    healthy = forms.ChoiceField(
        choices=(
            (0, _("Don't trigger when the device is healthy")),
            (1, _("Trigger when the device is healthy")),
        )
    )
    unhealthy = forms.ChoiceField(
        choices=(
            (0, _("Don't trigger when the device is unhealthy")),
            (1, _("Trigger when the device is unhealthy")),
        )
    )
    needAttention = forms.ChoiceField(
        choices=(
            (0, _("Don't trigger when the device needs attention")),
            (1, _("Trigger when the device needs attention")),
        )
    )
    triggerForEachIncident = forms.ChoiceField(
        choices=(
            (0, _("Don't trigger for each incident")),
            (1, _("Trigger for each incident")),
        )
    )
