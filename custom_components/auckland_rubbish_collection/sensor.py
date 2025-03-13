import aiohttp
import asyncio
import datetime
import voluptuous as vol
from bs4 import BeautifulSoup
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import EntityCategory
from .const import DOMAIN, _LOGGER, VERSION

SCAN_INTERVAL = timedelta(hours=3)
BASE_URL = "https://www.aucklandcouncil.govt.nz"

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the rubbish collection sensors."""
    _LOGGER.debug("Setting up sensors for entry: %s", entry.title)
    coordinator = AucklandRubbishCollectionCoordinator(hass, entry.data["address_id"])
    coordinator.address_name = entry.data.get("address_name", entry.data["address_id"])
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([
        RubbishCollectionSensor(coordinator, "rubbish"),
        RubbishCollectionSensor(coordinator, "recycling"),
        RubbishCollectionSensor(coordinator, "food_scraps"),
        RubbishCollectionSensor(coordinator, "geolocation_address"),
        RubbishCollectionSensor(coordinator, "next_collection_type")
    ])

class AucklandRubbishCollectionCoordinator(DataUpdateCoordinator):
    """Fetch rubbish collection data periodically."""
    def __init__(self, hass, address_id):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.hass = hass
        self.address_id = address_id
        self.address_name = "Address"

    def parse_collection_date(self, text):
        """Convert collection text (e.g., 'Thursday 13 March') into a standardized format."""
        try:
            parts = text.split(" ")
            day_name, day, month = parts[0], parts[1], parts[2]
            year = datetime.datetime.now().year  # Assume current year
            parsed_date = datetime.datetime.strptime(f"{day} {month} {year}", "%d %B %Y")
            return parsed_date.strftime("%A %d %B")  # Ensure consistent format
        except (ValueError, IndexError):
            return None  # Return None if parsing fails

    async def _async_update_data(self):
        url = f"{BASE_URL}/rubbish-recycling/rubbish-recycling-collections/Pages/collection-day-detail.aspx?an={self.address_id}"
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(url) as response:
                response_text = await response.text()
            soup = BeautifulSoup(response_text, "html.parser")
            collection_info = soup.find_all(attrs={"class": "collectionDayDate"})
            if not collection_info:
                _LOGGER.error("Unexpected response format: no collection data found")
                return {}

            # Extract geolocation address
            address_blocks = soup.find_all(attrs={"class": "m-b-2"})
            geolocation_address = address_blocks[0].string.strip() if address_blocks and address_blocks[0].string else None

            # Initialize collection dates
            rubbish, recycling, food_scraps = None, None, None

            # Parse each collection entry and assign to the correct type
            for entry in collection_info:
                text = entry.get_text(strip=True)
                if "rubbish" in text.lower():
                    rubbish = self.parse_collection_date(text.split(":", 1)[-1].strip() if ":" in text else text)
                elif "recycling" in text.lower():
                    recycling = self.parse_collection_date(text.split(":", 1)[-1].strip() if ":" in text else text)
                elif "food scraps" in text.lower():
                    food_scraps = self.parse_collection_date(text.split(":", 1)[-1].strip() if ":" in text else text)

            # Determine next collection type based on dates
            if rubbish and recycling and (rubbish == recycling):
                next_collection_type = "Recycling"
            else:
                next_collection_type = "Rubbish"

            return {
                "rubbish": rubbish,
                "recycling": recycling,
                "food_scraps": food_scraps,
                "geolocation_address": geolocation_address,
                "next_collection_type": next_collection_type
            }
        except Exception as e:
            _LOGGER.error("Error fetching rubbish collection data: %s", e)
            return {}

class RubbishCollectionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a rubbish collection sensor."""
    def __init__(self, coordinator, sensor_type):
        super().__init__(coordinator)
        self.sensor_type = sensor_type
        self._attr_name = f"{coordinator.address_name} {sensor_type.replace('_', ' ').title()}"
        self._attr_unique_id = f"{DOMAIN}_{coordinator.address_id}_{sensor_type}"
        self._attr_icon = self._determine_icon(sensor_type)

        if sensor_type == "geolocation_address":
            self.entity_registry_enabled_default = False
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def state(self):
        return self.coordinator.data.get(self.sensor_type, None)

    @property
    def device_info(self):
        """Return device information for this integration."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.address_id)},
            "name": self.coordinator.address_name,
            "manufacturer": "Auckland Council",
            "model": "Rubbish Collection",
            "sw_version": VERSION,
        }

    def _determine_icon(self, sensor_type: str) -> str:
        if sensor_type == "rubbish":
            return "mdi:trash-can"
        if sensor_type == "recycling":
            return "mdi:recycle"
        if sensor_type == "food_scraps":
            return "mdi:compost"
        if sensor_type == "geolocation_address":
            return "mdi:map-marker"
        if sensor_type == "next_collection_type":
            return "mdi:calendar"
        return "mdi:help-circle"
