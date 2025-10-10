from django.db import models
from django.utils.translation import gettext_lazy as _


class WialonNotificationTrigger(models.TextChoices):
    GEOFENCE = "geozone", _("Geofence")
    ADDRESS = "address", _("Address")
    SPEED = "speed", _("Speed")
    ALARM = "alarm", _("Alarm")
    DIGITAL = "digital_input", _("Digital input")
    PARAMETER = "msg_param", _("Parameter in a message")
    SENSOR = "sensor_value", _("Sensor value")
    OUTAGE = "outage", _("Connection loss")
    INTERPOSITION = "interposition", _("Interposition of units")
    EXCESS = "msgs_counter", _("Excess of messages")
    ROUTE = "route_control", _("Route progress")
    DRIVER = "driver", _("Driver")
    TRAILER = "trailer", _("Trailer")
    MAINTENANCE = "service_interals", _("Maintenance")
    FUEL = "fuel_filling", _("Fuel filling/battery charge")
    FUEL_DRAIN = "fuel_theft", _("Fuel drain/theft")
    HEALTH = "health_check", _("Health check")


class WialonUnitSensor(models.TextChoices):
    ANY = "", _("Any")
    # Mileage
    MILEAGE = "mileage", _("Mileage sensor")
    ODOMETER = "odometer", _("Relative odometer")
    # Digital
    IGNITION = "engine operation", _("Engine ignition sensor")
    ALARM = "alarm trigger", _("Alarm trigger")
    PRIVATE = "private mode", _("Private mode")
    RTMOTION = "real-time motion sensor", _("Real-time motion sensor")
    DIGITAL = "digital", _("Custom digital sensor")
    # Gauges
    VOLTAGE = "voltage", _("Voltage sensor")
    WEIGHT = "weight", _("Weight sensor")
    ACCELEROMETER = "accelerometer", _("Accelerometer")
    TEMPERATURE = "temperature", _("Temperature sensor")
    TEMPERATURE_COEF = "temperature coefficient", _("Temperature coefficient")
    # Engine
    ENGINE_RPM = "engine rpm", _("Engine revolution sensor")
    ENGINE_EFF = "engine efficiency", _("Engine efficiency sensor")
    ENGINE_HOURS_ABS = "engine hours", _("Absolute engine hours")
    ENGINE_HOURS_REL = "relative engine hours", _("Relative engine hours")
    # Fuel
    FUEL_CONS_IMP = (
        "impulse fuel consumption",
        _("Impulse fuel consumption sensor"),
    )
    FUEL_CONS_ABS = (
        "absolute fuel consumption",
        _("Absolute fuel consumption sensor"),
    )
    FUEL_CONS_INT = (
        "instant fuel consumption",
        _("Instant fuel consumption sensor"),
    )
    FUEL_LEVEL = "fuel level", _("Fuel level sensor")
    FUEL_LEVEL_IMP = (
        "fuel level impulse sensor",
        _("Impulse fuel level sensor"),
    )
    BATTERY_LEVEL = "battery level", _("Battery level sensor")
    # Other
    COUNTER = "counter", _("Counter sensor")
    CUSTOM = "custom", _("Custom sensor")
    DRIVER = "driver", _("Driver assignment")
    TRAILER = "trailer", _("Trailer assignment")
    TAG = "tag", _("Passenger sensor")
