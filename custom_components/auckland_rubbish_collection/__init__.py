from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from .const import _LOGGER
from .sensor import AucklandRubbishCollectionCoordinator  # Import Coordinator

DOMAIN = "auckland_rubbish_collection"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Auckland Rubbish Collection from a config entry."""
    _LOGGER.debug("Setting up entry: %s", entry.title)

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    coordinator = AucklandRubbishCollectionCoordinator(hass, entry.data["address_id"])
    hass.data[DOMAIN][entry.entry_id] = coordinator  # Store the coordinator

    try:
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    except Exception as ex:
        _LOGGER.exception("Error during setup: %s", ex)
        raise ConfigEntryNotReady from ex

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading entry: %s", entry.title)
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor") and \
           await hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
