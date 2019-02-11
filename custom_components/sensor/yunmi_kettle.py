"""Yunmi Kettle for homeassistant"""
import math
import logging

from homeassistant.components.sensor import DOMAIN
from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_TOKEN, )
from homeassistant.helpers.entity import Entity
from homeassistant.exceptions import PlatformNotReady

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['python-miio>=0.3.1']

CURRENT_TEMPE = {'name': 'kettle current temperture', 'key': '°C'}
SETUP_TEMPE = {'name': 'kettle setup temperture', 'key': '°C'}
TDS = {'name': 'kettle TDS', 'key': 'ppm'}
WATER_REMAIN_TIME = {'name': 'kettle water remain time', 'key': 'hour'}


SUCCESS = ['ok']

ATTR_TEMP = 'temp'
DEFAULT_TEMP = '48'


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Perform the setup for Yunmi kettle."""
    from miio import Device, DeviceException

    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)

    _LOGGER.info("Initializing Yunmi Kettle with host %s (token %s...)", host, token[:5])

    devices = []
    try:
        device = Device(host, token)
        yumikettle = YunmiKettle(device, name)
        devices.append(yumikettle)
        devices.append(YunmiKettleSensor(yumikettle, CURRENT_TEMPE))
        devices.append(YunmiKettleSensor(yumikettle, SETUP_TEMPE))
        devices.append(YunmiKettleSensor(yumikettle, TDS))
        devices.append(YunmiKettleSensor(yumikettle, WATER_REMAIN_TIME))

    except DeviceException:
        _LOGGER.exception('Fail to setup yunmi kettle')
        raise PlatformNotReady

    add_devices(devices)

    def handle_set_temp(service):
        temp = service.data.get(ATTR_TEMP, DEFAULT_TEMP)
        _LOGGER.info("yunmi kettle service call data: %s", temp)
        result = device.send('set_tempe_setup', [1, int(temp)])

        return result == SUCCESS

    hass.services.register(DOMAIN, 'set_kettle_temp', handle_set_temp)


class YunmiKettleSensor(Entity):
    """Representation of a YunmiKettleSensor."""

    def __init__(self, yunmiKettle, data_key):
        """Initialize the YunmiKettleSensor."""
        self._state = None
        self._data = None
        self._yunmiKettle = yunmiKettle
        self._data_key = data_key
        self.parse_data()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._data_key['name']

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self._data_key['key'] is CURRENT_TEMPE['key'] or \
           self._data_key['key'] is SETUP_TEMPE['key']:
            return 'mdi:water'
        else:
            return 'mdi:filter-outline'

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        if self._data_key['key'] is TDS['key']:
            return 'TDS'
        if self._data_key['key'] is WATER_REMAIN_TIME['key']:
            return 'hour'
        return '°C'

    @property
    def device_state_attributes(self):
        """Return the state attributes of the last update."""
        attrs = {}

        # if self._data_key['key'] is WATER_REMAIN_TIME['key']:
        #     attrs[self._data_key['name']] = '{} hour remaining'.format(self._data[self._data_key['days_key']])

        return attrs

    def parse_data(self):
        if self._yunmiKettle._data:
            self._data = self._yunmiKettle._data
            self._state = self._data[self._data_key['key']]

    def update(self):
        """Get the latest data and updates the states."""
        self.parse_data()

class YunmiKettle(Entity):
    """Representation of a YunmiKettle."""

    def __init__(self, device, name):
        """Initialize the YunmiKettle."""
        self._state = None
        self._device = device
        self._name = name
        self.parse_data()

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return 'mdi:water'

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return '°C'

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def hidden(self) -> bool:
        """Return True if the entity should be hidden from UIs."""
        return True

    @property
    def device_state_attributes(self):
        """Return the state attributes of the last update."""
        attrs = {}
        attrs[CURRENT_TEMPE['name']] = '{}°C'.format(self._data[CURRENT_TEMPE['key']])
        attrs[SETUP_TEMPE['name']] = '{}°C'.format(self._data[SETUP_TEMPE['key']])
        attrs[TDS['name']] = '{}ppm'.format(self._data[TDS['key']])
        attrs[WATER_REMAIN_TIME['name']] = '{}hour'.format(self._data[WATER_REMAIN_TIME['key']])

        return attrs

    def parse_data(self):
        """Parse data."""
        try:
            data = {}
            curr_tempe_status = self._device.send('get_prop', ["curr_tempe"])
            data[CURRENT_TEMPE['key']] = curr_tempe_status[0]
            setup_tempe_status = self._device.send('get_prop', ["setup_tempe"])
            data[SETUP_TEMPE['key']] = setup_tempe_status[0]
            tds_status = self._device.send('get_prop', ["tds"])
            data[TDS['key']] = tds_status[0]
            water_remain_time_status = self._device.send('get_prop', ["water_remain_time"])
            data[WATER_REMAIN_TIME['key']] = water_remain_time_status[0]


            self._data = data
            self._state = self._data[CURRENT_TEMPE['key']]
        except DeviceException:
            _LOGGER.exception('Fail to get_prop from YunmiKettle')
            self._data = None
            self._state = None
            raise PlatformNotReady

    def update(self):
        """Get the latest data and updates the states."""
        self.parse_data()
