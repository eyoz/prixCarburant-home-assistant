import logging
import sys
from datetime import datetime, timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_ELEVATION, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers.entity import Entity

ATTR_ID = "Station ID"
ATTR_GASOIL = 'Gasoil'
ATTR_E95 = 'E95'
ATTR_E98 = 'E98'
ATTR_E10 = 'E10'
ATTR_GPL = 'GPLc'
ATTR_E85 = 'E85'
ATTR_GASOIL_LAST_UPDATE = 'Last Update Gasoil'
ATTR_E95_LAST_UPDATE= 'Last Update E95'
ATTR_E98_LAST_UPDATE = 'Last Update E98'
ATTR_E10_LAST_UPDATE = 'Last Update E10'
ATTR_GPL_LAST_UPDATE = 'Last Update GPLc'
ATTR_E85_LAST_UPDATE = 'Last Update E85'
ATTR_CITY = 'Station City'
ATTR_ADDRESS = "Station Address"
ATTR_NAME = "Station name"
ATTR_DISTANCE = "Distance"
ATTR_LAST_UPDATE = "Last update"

CONF_MAX_KM = 'maxDistance'
CONF_STATION_ID = 'stationID'

'''
No need to set the scan_inverval below 10 mins as the details instantanés have a refresh of max every 10 min.
Suggestion to set hourly (default)
'''
SCAN_INTERVAL = timedelta(seconds=3600)



# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_MAX_KM, default=10): cv.positive_int,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_STATION_ID, default=[]): cv.ensure_list
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    logging.debug("[prixCarburantLoad] start")
    from .prixCarburantClient import PrixCarburantClient
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    """Setup the sensor platform."""
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    maxDistance = config.get(CONF_MAX_KM)
    listToExtract = config.get(CONF_STATION_ID)

    homeLocation = [{
        'lat': str(latitude),
        'lng': str(longitude)
    }]

    client = PrixCarburantClient(homeLocation, maxDistance)
    client.load()

    if not listToExtract:
        logging.info(
            "[prixCarburantLoad] No station list, find nearest station")
        stations = client.foundNearestStation()
    else:
        logging.info(
            "[prixCarburantLoad] Station list is defined, extraction in progress")
        list = []
        for station in listToExtract:
            list.append(str(station))
            logging.info("[prixCarburantLoad] - " + str(station))
        stations = client.extractSpecificStation(list)

    logging.info("[prixCarburantLoad] " +
                 str(len(stations)) + " stations found")
    client.clean()
    for station in stations:
        add_devices([PrixCarburant(stations.get(station), client,"mdi:currency-eur")])


class PrixCarburant(Entity):
    """Representation of a Sensor."""

    def __init__(self, station, client, icon):
        """Initialize the sensor."""
        self._state = None
        self.station = station
        self.client = client
        self._icon = icon        
        self._state = self.station.gazoil['valeur']
        self.lastUpdate=self.client.lastUpdate
        self.lastUpdateTime=datetime.now()
        self._unique_id = "PrixCarburant_" + self.station.id


    @property
    def name(self):
        """Return the name of the sensor."""
        return 'PrixCarburant_' + self.station.id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "€"

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this sensor."""
        return f"{self._unique_id}"

    @property
    def icon(self) -> str:
        """Return the mdi icon of the entity."""
        return self._icon

    @property
    #def device_state_attributes(self):
    def extra_state_attributes(self):
        """Return the device state attributes of the last update."""
        """Use ISO format for date to allow easier integration in iOS."""

        attrs = {
            ATTR_ID: self.station.id,
            ATTR_GASOIL: self.station.gazoil['valeur'],
            ATTR_GASOIL_LAST_UPDATE: self.station.gazoil['maj'].replace(' ','T'),
            ATTR_E95: self.station.e95['valeur'],
            ATTR_E95_LAST_UPDATE: self.station.e95['maj'].replace(' ','T'),
            ATTR_E98: self.station.e98['valeur'],
            ATTR_E98_LAST_UPDATE: self.station.e98['maj'].replace(' ','T'),
            ATTR_E10: self.station.e10['valeur'],
            ATTR_E10_LAST_UPDATE: self.station.e10['maj'].replace(' ','T'),
            ATTR_E85: self.station.e85['valeur'],
            ATTR_E85_LAST_UPDATE: self.station.e85['maj'].replace(' ','T'),
            ATTR_GPL: self.station.gpl['valeur'],
            ATTR_GPL_LAST_UPDATE: self.station.gpl['maj'].replace(' ','T'),
            ATTR_CITY: self.station.city,
            ATTR_ADDRESS: self.station.adress,
            ATTR_NAME: self.station.name,
            ATTR_DISTANCE: self.station.distance,
            ATTR_LAST_UPDATE: self.client.lastUpdateTime.strftime('%Y-%m-%dT%H:%M')
        }
        return attrs

    """Fetch new state data for the sensor.
    This is the only method that should fetch new data for Home Assistant.

    The sensor contains multiple elements that may or may not have updated over different dates and times.
    The scan_interval kicks of for each (!) of the loaded sensors, 
    The code below to avoid downloading / processing the same data for each sensor-call

    IMPORTANT: do not set the scan_interval too low, there is no (business) need for it and may lead to the API rejecting requests

    """
    def update(self):
        logging.warning('Start prixCarburant update process')
        self.client.reload()
        logging.warning("[UPDATE] of ["+self.station.id+"]")
        list = []
        list.append(str(self.station.id))
        myStation = self.client.extractSpecificStation(list)
        self.station = myStation.get(self.station.id)
        self.lastUpdate=self.client.lastUpdate
        self._state = self.station.gazoil['valeur']
        self.client.clean()
