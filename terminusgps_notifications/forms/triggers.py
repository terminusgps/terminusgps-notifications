import decimal
import json

from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .. import constants


class JSONDecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)


class TriggerForm(forms.Form):
    """Parent form for selecting/saving a notification trigger configuration."""

    t = forms.ChoiceField(
        choices=constants.WialonNotificationTriggerType.choices,
        help_text=_("Please select a trigger from the list."),
        initial=constants.WialonNotificationTriggerType.SENSOR,
        widget=forms.widgets.Select(
            {
                "class": "p-2 rounded border bg-gray-100",
                "hx-target": "#id_p",
                "hx-trigger": "load once, change",
                "hx-swap": "outerHTML",
                "hx-get": reverse_lazy(
                    "terminusgps_notifications:form trigger parameters"
                ),
            }
        ),
    )
    p = forms.JSONField()


class TriggerParametersForm(forms.Form):
    """Base class for notification trigger parameter forms."""

    def as_json(self) -> str:
        if not self.is_valid():
            raise ValueError(self.errors)
        return json.dumps(self.cleaned_data, cls=JSONDecimalEncoder)


class GeofenceTriggerParametersForm(TriggerParametersForm):
    lower_bound = forms.DecimalField(label="Lower bound", initial=-1)
    upper_bound = forms.DecimalField(label="Upper bound", initial=1)
    sensor_name_mask = forms.CharField(label="Sensor mask", initial="*")
    sensor_type = forms.ChoiceField(
        label="Sensor type",
        choices=constants.WialonUnitSensorType.choices,
        initial=constants.WialonUnitSensorType.ANY,
        required=False,
    )
    geozone_ids = forms.CharField()
    min_speed = forms.IntegerField(
        label="Min speed", min_value=0, max_value=256, initial=0
    )
    max_speed = forms.IntegerField(
        label="Max speed", min_value=0, max_value=256, initial=256
    )
    prev_msg_diff = forms.ChoiceField(
        choices=(
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        )
    )
    merge = forms.ChoiceField(
        label="Similar sensors",
        initial=0,
        choices=((0, _("Calculate separately")), (1, _("Sum up values"))),
    )
    reversed = forms.ChoiceField(
        label="Boundaries",
        initial=0,
        choices=(
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ),
    )
    type = forms.ChoiceField(
        label="Trigger when",
        initial=0,
        choices=(
            (0, _("Entering geofence(s)")),
            (1, _("Exiting geofence(s)")),
        ),
    )
    include_lbs = forms.BooleanField(
        initial=False, label="Process LBS messages", required=False
    )
    lo = forms.ChoiceField(
        choices=(("", "None"), ("AND", _("AND")), ("OR", _("OR"))),
        initial="",
        label="Logical operator",
        required=False,
    )


class AddressTriggerParametersForm(TriggerParametersForm):
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


class SpeedTriggerParametersForm(TriggerParametersForm):
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


class AlarmTriggerParametersForm(TriggerParametersForm):
    def save(self) -> str:
        return ""


class DigitalTriggerParametersForm(TriggerParametersForm):
    input_index = forms.IntegerField(min_value=1, max_value=32)
    type = forms.ChoiceField(
        choices=(
            (0, _("Check for activation")),
            (1, _("Check for deactivation")),
        )
    )


class ParameterTriggerParametersForm(TriggerParametersForm):
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


class SensorValueTriggerParametersForm(forms.Form):
    lower_bound = forms.DecimalField(label="Lower bound", initial=-1)
    upper_bound = forms.DecimalField(label="Upper bound", initial=1)
    merge = forms.ChoiceField(
        label="Similar sensors",
        initial=0,
        choices={(0, _("Calculate separately")), (1, _("Sum up values"))},
    )
    prev_msg_diff = forms.ChoiceField(
        label="Boundaries",
        choices=(
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ),
    )
    sensor_name_mask = forms.CharField(initial="*", label="Sensor mask")
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices,
        initial="",
        label="Sensor type",
        required=False,
    )
    type = forms.ChoiceField(
        label="Trigger when",
        initial=0,
        choices={
            (0, _("Sensor value in-range")),
            (1, _("Sensor value out-of-range")),
        },
    )


class OutageTriggerParametersForm(TriggerParametersForm):
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


class InterpositionTriggerParametersForm(TriggerParametersForm):
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


class ExcessTriggerParametersForm(TriggerParametersForm):
    flags = forms.ChoiceField(
        choices=((1, _("Data messages")), (2, _("SMS messages")))
    )
    msgs_limit = forms.IntegerField()
    time_offset = forms.IntegerField()


class RouteTriggerParametersForm(TriggerParametersForm):
    mask = forms.CharField()
    round_mask = forms.CharField()
    schedule_mask = forms.CharField()
    types = forms.CharField()


class DriverTriggerParametersForm(TriggerParametersForm):
    driver_code_mask = forms.CharField()
    flags = forms.ChoiceField(
        choices=((1, _("Driver assignment")), (2, _("Driver separation")))
    )


class TrailerTriggerParametersForm(TriggerParametersForm):
    driver_code_mask = forms.CharField()
    flags = forms.ChoiceField(
        choices=((1, _("Trailer assignment")), (2, _("Trailer separation")))
    )


class MaintenanceTriggerParametersForm(TriggerParametersForm):
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


class FuelTriggerParametersForm(TriggerParametersForm):
    sensor_name_mask = forms.CharField()
    geozones_type = forms.ChoiceField(
        choices=(
            (0, _("Disabled/outside geofence")),
            (1, _("Inside geofence")),
        )
    )
    geozones_list = forms.CharField()
    realtime_only = forms.BooleanField()


class FuelDrainTriggerParametersForm(TriggerParametersForm):
    sensor_name_mask = forms.CharField()
    geozones_type = forms.ChoiceField(
        choices=(
            (0, _("Disabled/outside geofence")),
            (1, _("Inside geofence")),
        )
    )
    geozones_list = forms.CharField()
    realtime_only = forms.BooleanField()


class HealthTriggerParametersForm(TriggerParametersForm):
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
