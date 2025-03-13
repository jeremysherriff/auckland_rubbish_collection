from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN, _LOGGER
from .service import get_coordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Auckland Rubbish Collection from a config entry."""
    _LOGGER.debug("Setting up entry: %s", entry.title)

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Get or create coordinator using the service module
    coordinator = get_coordinator(hass, entry)
    
    try:
        await coordinator.async_config_entry_first_refresh()
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    except Exception as ex:
        _LOGGER.exception("Error during setup: %s", ex)
        raise ConfigEntryNotReady from ex

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading entry: %s", entry.title)
    
    # Unload the platform entities
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])
    
    # Clean up the coordinator if unloaded successfully
    if unload_ok and entry.entry_id in hass.data[DOMAIN]:
        del hass.data[DOMAIN][entry.entry_id]
        
    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry."""
    # Unload the entry first
    await async_unload_entry(hass, entry)
    
    # Set up the entry again
    await async_setup_entry(hass, entry)