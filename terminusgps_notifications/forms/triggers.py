from django import forms
from django.utils.translation import gettext_lazy as _

from ..constants import WialonUnitSensor


class GeofenceTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class AddressTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class SpeedTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class AlarmTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class DigitalTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class ParameterTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class SensorValueTriggerForm(forms.Form):
    lower_bound = forms.DecimalField(label="Sensor value upper bound:")
    upper_bound = forms.DecimalField(label="Sensor value lower bound:")
    merge = forms.ChoiceField(
        label="Similar sensors:",
        choices={(0, _("Calculate separately")), (1, _("Sum up values"))},
    )
    prev_msg_diff = forms.ChoiceField(
        label="Form boundaries according to previous or absolute value?",
        choices={
            (0, _("Relative to absolute value")),
            (1, _("Relative to previous value")),
        },
    )
    sensor_name_mask = forms.CharField(label="Sensor name mask")
    sensor_type = forms.ChoiceField(
        label="Sensor type:", choices=WialonUnitSensor.choices
    )
    type = forms.ChoiceField(
        label="Trigger when:",
        choices={(0, _("In Range")), (1, _("Out of Range"))},
    )


class OutageTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class InterpositionTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class ExcessTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class RouteTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class DriverTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class TrailerTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class MaintenanceTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class FuelTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class FuelDrainTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class HealthTriggerForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError()
