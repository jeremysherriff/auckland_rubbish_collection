import datetime
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, _LOGGER

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Collection Today binary sensor."""
    coordinator = hass.data[DOMAIN].get(entry.entry_id)  # Retrieve coordinator
    if not coordinator:
        _LOGGER.error("Coordinator not found for entry: %s", entry.entry_id)
        return

    await coordinator.async_config_entry_first_refresh()  # Ensure data is available
    async_add_entities([CollectionTodayBinarySensor(coordinator)])

class CollectionTodayBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor indicating whether there is a rubbish collection today."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator  # Ensure coordinator is assigned
        self._attr_name = f"{coordinator.address_name} Collection Today"
        self._attr_unique_id = f"{DOMAIN}_{coordinator.address_id}_collection_today"

    @property
    def is_on(self):
        """Return true if today is a collection day."""
        if not self.coordinator.data:
            _LOGGER.warning("Collection data is not yet available.")
            return False  # Prevent crash when data is None

        today = datetime.datetime.now().strftime("%A %d %B")  # Format: "Thursday 13 March"
        return any(
            date == today for date in [
                self.coordinator.data.get("rubbish"),
                self.coordinator.data.get("recycling"),
                self.coordinator.data.get("food_scraps")
            ] if date
        )

    @property
    def device_info(self):
        """Return device information for this integration."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.address_id)},
            "name": self.coordinator.address_name,
            "manufacturer": "Auckland Council",
            "model": "Rubbish Collection",
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:trash-can-outline"
