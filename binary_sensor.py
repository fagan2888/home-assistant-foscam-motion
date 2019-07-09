"""
"""
import logging
import threading

import voluptuous as vol

from homeassistant.components.binary_sensor import (
    BinarySensorDevice, PLATFORM_SCHEMA, DEVICE_CLASS_MOTION)
from homeassistant.const import DEVICE_DEFAULT_NAME
from homeassistant.const import (
    CONF_NAME, CONF_USERNAME, CONF_PASSWORD, CONF_PORT)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_IP = 'ip'

DEFAULT_NAME = 'Foscam Camera Motion'
DEFAULT_PORT = 88

DEPENDENCIES = []

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    _LOGGER.info("Setting up foscam motion platform")
    """Set up the Raspberry PI GPIO devices."""
    try:
        add_devices([FoscamCamMotion(config)], True)
    except:
        _LOGGER.exception("Unexpected error setting up foscam motion platform")


class FoscamCamMotion(BinarySensorDevice):
    """Represent a binary sensor that uses Raspberry Pi GPIO via gpiozero"""

    def __init__(self, device_info):
        # pylint: disable=no-member
        from libpyfoscam import FoscamCamera

        super(FoscamCamMotion, self).__init__()

        ip_address = device_info.get(CONF_IP)
        port = device_info.get(CONF_PORT)
        self._username = device_info.get(CONF_USERNAME)
        self._password = device_info.get(CONF_PASSWORD)
        self._name = device_info.get(CONF_NAME)
       
        self._available = False
        self._state = False
 
        self._foscam_session = FoscamCamera(
            ip_address,
            port,
            self._username,
            self._password,
            verbose=True
        )

    @property
    def should_poll(self):
        return True

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return the state of the entity."""
        return self._state

    @property
    def available(self):
        return self._available
    
    @property
    def device_class(self):
        return DEVICE_CLASS_MOTION

    def update(self):
        """Update the GPIO state."""
        _LOGGER.info("Updating %s", self._name)
        try:
            self._dev_state = self._foscam_session.get_dev_state()
            _LOGGER.info("DEV STATE %s", self._dev_state)
            if self._dev_state[0] == 0:
                motionDetectAlarm = int(self._dev_state[1]['motionDetectAlarm'])
                if motionDetectAlarm == 1:
                    self._available = True
                    self._state = False
                elif motionDetectAlarm == 2:
                    self._available = True
                    self._state = True
                else:
                    self._available = False
                    self._state = False
            else:
                    self._available = False
                    self._state = False
        except:
            # If there are any errors during checking is_pressed
            # reset the _btn
            _LOGGER.exception("%s has failed to update", self._name)

        _LOGGER.info("%s has been updated to state %s available %s",
                     self._name, self._state, self._available)
