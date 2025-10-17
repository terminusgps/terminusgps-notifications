import decimal
import json

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .. import constants


class JSONDecimalEncoder(json.JSONEncoder):
    """Casts :py:type:`~decimal.Decimal` objects to :py:type:`float` before encoding."""

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)


class TriggerForm(forms.Form):
    """Parent form for selecting/saving a notification trigger configuration."""

    un = forms.CharField(widget=forms.widgets.HiddenInput())
    """List of Wialon units."""
    p = forms.JSONField(encoder=JSONDecimalEncoder)
    """Trigger parameters."""
    t = forms.ChoiceField(
        choices=constants.WialonNotificationTriggerType.choices,
        help_text=_("Please select a trigger from the list."),
        initial=constants.WialonNotificationTriggerType.SENSOR,
        widget=forms.widgets.Select(
            {
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600",
                "hx-target": "#id_trigger_parameters",
                "hx-trigger": "load once, change",
                "hx-swap": "outerHTML",
                "hx-get": reverse_lazy(
                    "terminusgps_notifications:trigger parameters"
                ),
            }
        ),
    )
    """Trigger type."""


class TriggerParametersForm(forms.Form):
    """Base class for notification trigger parameter forms."""

    def as_json(self) -> str:
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
    prev_msg_diff = forms.TypedChoiceField(
        choices=[
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ],
        coerce=int,
    )
    merge = forms.TypedChoiceField(
        label="Similar sensors",
        initial=0,
        choices=[(0, _("Calculate separately")), (1, _("Sum up values"))],
        coerce=int,
    )
    reversed = forms.TypedChoiceField(
        label="Boundaries",
        initial=0,
        choices=[
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ],
        coerce=int,
    )
    type = forms.TypedChoiceField(
        label="Trigger when",
        initial=0,
        choices=[
            (0, _("Entering geofence(s)")),
            (1, _("Exiting geofence(s)")),
        ],
        coerce=int,
    )
    include_lbs = forms.BooleanField(
        initial=False, label="Process LBS messages", required=False
    )
    lo = forms.ChoiceField(
        choices=[("", "None"), ("AND", _("AND")), ("OR", _("OR"))],
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
    prev_msg_diff = forms.TypedChoiceField(
        initial=0,
        choices=[
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ],
        coerce=int,
    )
    radius = forms.IntegerField()
    region = forms.CharField()
    reversed = forms.TypedChoiceField(
        label="Boundaries",
        initial=0,
        choices=[
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ],
        coerce=int,
    )
    sensor_name_mask = forms.CharField(label="Sensor mask", initial="*")
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices,
        initial=constants.WialonUnitSensorType.ANY,
    )
    street = forms.CharField()
    type = forms.ChoiceField()
    upper_bound = forms.DecimalField()


class SpeedTriggerParametersForm(TriggerParametersForm):
    lower_bound = forms.DecimalField()
    max_speed = forms.IntegerField()
    merge = forms.ChoiceField()
    min_speed = forms.IntegerField()
    prev_msg_diff = forms.TypedChoiceField(
        choices=[
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ],
        coerce=int,
    )
    reversed = forms.TypedChoiceField(
        label="Boundaries",
        initial=0,
        choices=[
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ],
        coerce=int,
    )
    sensor_name_mask = forms.CharField()
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices,
        initial=constants.WialonUnitSensorType.ANY,
    )
    upper_bound = forms.IntegerField(initial=1)


class AlarmTriggerParametersForm(TriggerParametersForm):
    pass


class DigitalTriggerParametersForm(TriggerParametersForm):
    input_index = forms.IntegerField(min_value=1, max_value=32)
    type = forms.TypedChoiceField(
        choices=[
            (0, _("Check for activation")),
            (1, _("Check for deactivation")),
        ],
        coerce=int,
    )


class ParameterTriggerParametersForm(TriggerParametersForm):
    kind = forms.TypedChoiceField(
        choices=[
            (0, _("Value range")),
            (1, _("Text mask")),
            (2, _("Parameter availability")),
            (3, _("Parameter lack")),
        ],
        coerce=int,
    )
    lower_bound = forms.DecimalField()
    param = forms.CharField()
    text_mask = forms.CharField()
    type = forms.TypedChoiceField(
        choices=[
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ],
        coerce=int,
    )
    upper_bound = forms.DecimalField()


class SensorValueTriggerParametersForm(TriggerParametersForm):
    lower_bound = forms.DecimalField(
        label="Lower bound",
        initial=-1,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
            }
        ),
    )
    upper_bound = forms.DecimalField(
        label="Upper bound",
        initial=1,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
            }
        ),
    )
    merge = forms.TypedChoiceField(
        label="Similar sensors",
        initial=0,
        choices=[(0, _("Calculate separately")), (1, _("Sum up values"))],
        coerce=int,
        widget=forms.widgets.Select(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
            }
        ),
    )
    prev_msg_diff = forms.TypedChoiceField(
        label="Boundaries",
        choices=[
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ],
        coerce=int,
        widget=forms.widgets.Select(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
            }
        ),
    )
    sensor_name_mask = forms.CharField(
        label="Sensor mask",
        initial="*",
        widget=forms.widgets.TextInput(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
            }
        ),
    )
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices,
        initial="",
        label="Sensor type",
        required=False,
        widget=forms.widgets.Select(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
            }
        ),
    )
    type = forms.TypedChoiceField(
        label="Trigger when",
        initial=0,
        choices=[
            (0, _("Sensor value in-range")),
            (1, _("Sensor value out-of-range")),
        ],
        coerce=int,
        widget=forms.widgets.Select(
            attrs={
                "class": "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 invalid:bg-red-50 invalid:text-red-600"
            }
        ),
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


class OutageTriggerParametersForm(TriggerParametersForm):
    check_restore = forms.TypedChoiceField(
        choices=[
            (0, _("Connection lost")),
            (1, _("Connection lost and restored")),
            (2, _("Connection restored")),
        ],
        coerce=int,
    )
    geozones_list = forms.CharField()
    geozones_type = forms.TypedChoiceField(
        choices=[(0, _("Out of geofence")), (1, _("In geofence"))], coerce=int
    )
    include_lbs = forms.BooleanField()
    time = forms.IntegerField()
    type = forms.TypedChoiceField(
        choices=[(0, _("Coordinates loss")), (1, _("Connection loss"))],
        coerce=int,
    )


class InterpositionTriggerParametersForm(TriggerParametersForm):
    include_lbs = forms.BooleanField()
    lo = forms.ChoiceField(
        choices=[("AND", _("Logical AND")), ("OR", _("Logical OR"))]
    )
    lower_bound = forms.DecimalField()
    max_speed = forms.IntegerField()
    merge = forms.TypedChoiceField(
        choices=[(0, _("Calculate separately")), (1, _("Sum up values"))],
        coerce=int,
    )
    min_speed = forms.IntegerField()
    prev_msg_diff = forms.TypedChoiceField(
        choices=[
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        ],
        coerce=int,
    )
    radius = forms.IntegerField()
    reversed = forms.TypedChoiceField(
        label="Boundaries",
        initial=0,
        choices=[
            (0, _("In the specified range")),
            (1, _("Out of the specified range")),
        ],
        coerce=int,
    )
    sensor_name_mask = forms.CharField(label="Sensor mask", initial="*")
    sensor_type = forms.ChoiceField(
        choices=constants.WialonUnitSensorType.choices,
        initial=constants.WialonUnitSensorType.ANY,
    )
    type = forms.TypedChoiceField(
        choices=[
            (0, _("Control approaching to units")),
            (1, _("Control moving away from units")),
        ],
        coerce=int,
    )
    unit_guids = forms.CharField()
    upper_bound = forms.DecimalField()


class ExcessTriggerParametersForm(TriggerParametersForm):
    flags = forms.TypedChoiceField(
        choices=[(1, _("Data messages")), (2, _("SMS messages"))], coerce=int
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
    flags = forms.TypedChoiceField(
        choices=[(1, _("Driver assignment")), (2, _("Driver separation"))],
        coerce=int,
    )


class TrailerTriggerParametersForm(TriggerParametersForm):
    driver_code_mask = forms.CharField()
    flags = forms.TypedChoiceField(
        choices=[(1, _("Trailer assignment")), (2, _("Trailer separation"))],
        coerce=int,
    )


class MaintenanceTriggerParametersForm(TriggerParametersForm):
    days = forms.IntegerField()
    engine_hours = forms.IntegerField()
    flags = forms.TypedChoiceField(
        choices=[
            (0, _("Control all service intervals")),
            (1, _("Mileage interval")),
            (2, _("Engine hours interval")),
            (4, _("Days interval")),
        ],
        coerce=int,
    )
    mask = forms.CharField()
    mileage = forms.IntegerField()
    val = forms.TypedChoiceField(
        choices=[
            (1, _("Notify when service term approaches")),
            (-1, _("Notify when service term is expired")),
        ],
        coerce=int,
    )


class FuelTriggerParametersForm(TriggerParametersForm):
    sensor_name_mask = forms.CharField(label="Sensor mask", initial="*")
    geozones_type = forms.TypedChoiceField(
        choices=[
            (0, _("Disabled/outside geofence")),
            (1, _("Inside geofence")),
        ],
        coerce=int,
    )
    geozones_list = forms.CharField()
    realtime_only = forms.BooleanField()


class FuelDrainTriggerParametersForm(TriggerParametersForm):
    sensor_name_mask = forms.CharField(label="Sensor mask", initial="*")
    geozones_type = forms.TypedChoiceField(
        choices=[
            (0, _("Disabled/outside geofence")),
            (1, _("Inside geofence")),
        ],
        coerce=int,
    )
    geozones_list = forms.CharField()
    realtime_only = forms.BooleanField()


class HealthTriggerParametersForm(TriggerParametersForm):
    healthy = forms.TypedChoiceField(
        choices=[
            (0, _("Don't trigger when the device is healthy")),
            (1, _("Trigger when the device is healthy")),
        ],
        coerce=int,
    )
    unhealthy = forms.TypedChoiceField(
        choices=[
            (0, _("Don't trigger when the device is unhealthy")),
            (1, _("Trigger when the device is unhealthy")),
        ],
        coerce=int,
    )
    needAttention = forms.TypedChoiceField(
        choices=[
            (0, _("Don't trigger when the device needs attention")),
            (1, _("Trigger when the device needs attention")),
        ],
        coerce=int,
    )
    triggerForEachIncident = forms.TypedChoiceField(
        choices=[
            (0, _("Don't trigger for each incident")),
            (1, _("Trigger for each incident")),
        ],
        coerce=int,
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
