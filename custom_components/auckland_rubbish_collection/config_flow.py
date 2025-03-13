import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, _LOGGER

CONF_ADDRESS_NAME = "address_name"
CONF_ADDRESS_ID = "address_id"

class AucklandRubbishConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Auckland Council Rubbish Collection."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            _LOGGER.debug("User input received: %s", user_input)
            # Validate address_id format
            address_id = user_input[CONF_ADDRESS_ID]
            if not len(address_id) == 11:
                errors[CONF_ADDRESS_ID] = "invalid_id_length"
            elif not address_id.isdigit():
                errors[CONF_ADDRESS_ID] = "invalid_id_format"
            if not errors:
                # Use the provided address_name as the title (this is immutable)
                return self.async_create_entry(title=user_input[CONF_ADDRESS_NAME], data=user_input)
        data_schema = vol.Schema({
            vol.Required(CONF_ADDRESS_NAME): str,
            vol.Required(CONF_ADDRESS_ID): str,
        })
        description_placeholders = {
            "url": "https://www.aucklandcouncil.govt.nz/rubbish-recycling/rubbish-recycling-collections/Pages/rubbish-recycling-collection-days.aspx"
        }
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders=description_placeholders,
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return AucklandRubbishOptionsFlow(entry)

class AucklandRubbishOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate address_id format if provided
            if CONF_ADDRESS_ID in user_input and user_input[CONF_ADDRESS_ID]:
                address_id = user_input[CONF_ADDRESS_ID]
                if not len(address_id) == 11:
                    errors[CONF_ADDRESS_ID] = "invalid_id_length"
                elif not address_id.isdigit():
                    errors[CONF_ADDRESS_ID] = "invalid_id_format"
            if not errors:
                # Update options by creating a new entry for the options
                return self.async_create_entry(data=user_input)
        options_schema = vol.Schema({
            vol.Required(CONF_ADDRESS_ID, default=self.entry.options.get(CONF_ADDRESS_ID, self.entry.data.get(CONF_ADDRESS_ID, ""))): str,
        })
        description_placeholders = {
            "url": "https://www.aucklandcouncil.govt.nz/rubbish-recycling/rubbish-recycling-collections/Pages/rubbish-recycling-collection-days.aspx"
        }
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
            description_placeholders=description_placeholders,
        )
