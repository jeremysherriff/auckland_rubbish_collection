import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
from .const import DOMAIN, _LOGGER
from .service import get_coordinator

def slugify(name: str) -> str:
    """Convert a string into a slug safe for unique IDs."""
    return name.lower().replace(" ", "_")

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the rubbish collection sensors."""
    _LOGGER.debug("Setting up sensors for entry: %s", entry.title)
    
    # Get the coordinator
    coordinator = get_coordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    async_add_entities([
        RubbishCollectionSensor(coordinator, "rubbish"),
        RubbishCollectionSensor(coordinator, "recycling"),
        RubbishCollectionSensor(coordinator, "food_scraps"),
        RubbishCollectionSensor(coordinator, "geolocation_address"),
        RubbishCollectionSensor(coordinator, "next_collection_type")
    ])

class RubbishCollectionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a rubbish collection sensor."""
    def __init__(self, coordinator, sensor_type):
        super().__init__(coordinator)
        self.sensor_type = sensor_type
        # Use slugified address_name for unique IDs
        self._attr_name = f"{coordinator.address_name} {sensor_type.replace('_', ' ').title()}"
        self._attr_unique_id = f"{DOMAIN}_{slugify(coordinator.address_name)}_{sensor_type}"
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
            "identifiers": {(DOMAIN, slugify(self.coordinator.address_name))},
            "name": self.coordinator.address_name,
            "manufacturer": "Auckland Council",
            "model": "Rubbish Collection Service",
            "entry_type": "service",  # This indicates it's a service, not a device
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