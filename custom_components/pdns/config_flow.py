"""Config flow to configure PowerDNS Dynhost."""
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from . import DOMAIN, CONF_ALIAS, CONF_PDNSSRV
from .pdns import PDNS, CannotConnect, TimeoutExpired, PDNSFailed, DetectionFailed

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ALIAS): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_PDNSSRV): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


class PDNSFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            try:
                client = PDNS(
                    servername=user_input[CONF_PDNSSRV],
                    alias=user_input[CONF_ALIAS],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    session=async_create_clientsession(self.hass),
                )
                await client.async_update()
                return self.async_create_entry(
                    title="PowerDNS Dynhost", data=user_input
                )
            except CannotConnect:
                errors["base"] = "login_incorrect"
            except TimeoutExpired:
                errors["base"] = "timeout"
            except PDNSFailed as err:
                errors["base"] = err.args[0]
            except DetectionFailed:
                errors["base"] = "detect_failed"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
