from enum import StrEnum

from django.db import models
from django.utils.translation import gettext_lazy as _


# fmt: off
class WialonNotificationUpdateCallModeType(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class WialonNotificationTriggerType(models.TextChoices):
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


class WialonUnitSensorType(models.TextChoices):
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
    FUEL_CONS_IMP = "impulse fuel consumption", _("Impulse fuel consumption sensor")
    FUEL_CONS_ABS = "absolute fuel consumption", _("Absolute fuel consumption sensor")
    FUEL_CONS_INT = "instant fuel consumption", _("Instant fuel consumption sensor")
    FUEL_LEVEL = "fuel level", _("Fuel level sensor")
    FUEL_LEVEL_IMP = "fuel level impulse sensor", _("Impulse fuel level sensor")
    BATTERY_LEVEL = "battery level", _("Battery level sensor")
    # Other
    COUNTER = "counter", _("Counter sensor")
    CUSTOM = "custom", _("Custom sensor")
    DRIVER = "driver", _("Driver assignment")
    TRAILER = "trailer", _("Trailer assignment")
    TAG = "tag", _("Passenger sensor")


class WialonNotificationMessageTag(models.TextChoices):
    UNIT = "%UNIT%", _("Unit name")
    CURR_TIME = "%CURR_TIME%", _("Current date and time")
    LOCATION = "%LOCATION%", _("Location")
    LOCATOR_LINK = "%LOCATOR_LINK(60,T)%", _("Create locator link for the triggered unit (brackets indicate lifespan in minutes, T and G parameters to show tracks and geofences)")
    ZONE_MIN = "%ZONE_MIN%", _( "The smallest of geofences holding unit at the moment of notification")
    ZONE_ALL = "%ZONES_ALL%", _("All geofences holding unit at the moment of notification")
    UNIT_GROUP = "%UNIT_GROUP%", _("Groups containing triggered unit")
    SPEED = "%SPEED%", _("Unit speed at the moment of notification")
    POS_TIME = "%POS_TIME%", _("Date and time of the triggered message or the latest message with position in case the triggered message has no position")
    MSG_TIME = "%MSG_TIME%", _("Date and time of the triggered message")
    DRIVER = "%DRIVER%", _("Driver name")
    DRIVER_PHONE = "%DRIVER_PHONE%", _("Driver phone number")
    TRAILER = "%TRAILER%", _("Trailer name")
    SENSOR = "%SENSOR(*)%", _("Unit sensors and their values (indicate sensor mask in brackets)")
    ENGINE_HOURS = "%ENGINE_HOURS%", _("Engine hours at the moment of notification")
    MILEAGE = "%MILEAGE%", _("Mileage at the moment of notification")
    LAT = "%LAT%", _("Latitude at the moment of notification")
    LON = "%LON%", _("Longitude at the moment of notification")
    LATD = "%LATD%", _("Latitude at the moment of notification (without formatting)")
    LOND = "%LOND%", _("Longitude at the moment of notification (without formatting)")
    GOOGLE_LINK = "%GOOGLE_LINK%", _("Link to Google Maps with the position at the moment of notification")
    CUSTOM_FIELD = "%CUSTOM_FIELD(*)%", _("Custom field value from unit properties (indicate custom field name in brackets)")
    SENSOR_NAME = "%SENSOR_NAME%", _("Sensor name")
    SENSOR_VALUE = "%SENSOR_VALUE%", _("Triggered sensor value")
    TRIGGERED_SENSORS = "%TRIGGERED_SENSORS%", _("All triggered sensors and their values")
    VIDEO_LINK = "%VIDEO_LINK(480)%", _("Links to the video files saved for the triggered notification with the 'Save a video as a file' action. In parentheses, specify the validity period of the links in minutes, the maximum value is 2880")
    UNIT_ID = "%UNIT_ID%", _("Unit ID")
    MSG_TIME_INT = "%MSG_TIME_INT%", _("Time of triggered message in UNIX format")
