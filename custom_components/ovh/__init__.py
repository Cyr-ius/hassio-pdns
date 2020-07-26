"""Integrate with OVH Dynamic DNS service."""
import asyncio
from datetime import timedelta
import logging

import aiohttp
from aiohttp.hdrs import USER_AGENT
import async_timeout
import voluptuous as vol

from homeassistant.const import CONF_DOMAIN, CONF_PASSWORD, CONF_TIMEOUT, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import SERVER_SOFTWARE
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ovh"

# We should set a dedicated address for the user agent.
EMAIL = "hello@home-assistant.io"

INTERVAL = timedelta(minutes=5)

DEFAULT_TIMEOUT = 10

OVH_ERRORS = {
    "nohost": "Hostname supplied does not exist under specified account",
    "badauth": "Invalid username password combination",
    "badagent": "Client disabled",
    "!donator": "An update request was sent with a feature that is not available",
    "abuse": "Username is blocked due to abuse",
}

UPDATE_URL = "https://www.ovh.com/nic/update"
IP_URL = "https://api.ipify.org"
HA_USER_AGENT = f"{SERVER_SOFTWARE} {EMAIL}"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DOMAIN): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Initialize the OVH component."""
    domain = config[DOMAIN].get(CONF_DOMAIN)
    user = config[DOMAIN].get(CONF_USERNAME)
    password = config[DOMAIN].get(CONF_PASSWORD)
    timeout = config[DOMAIN].get(CONF_TIMEOUT)

    session = hass.helpers.aiohttp_client.async_get_clientsession()

    result = await _update_ovh(hass, session, domain, user, password, timeout)

    if not result:
        return False

    async def update_domain_interval(now):
        """Update the OVH entry."""
        await _update_ovh(hass, session, domain, user, password, timeout)

    hass.helpers.event.async_track_time_interval(update_domain_interval, INTERVAL)

    return True


async def _update_ovh(hass, session, domain, user, password, timeout):
    """Update OVH."""
    url = UPDATE_URL

    ip = session.get(IP_URL).text
    _LOGGER.info("Public IP: {}".format(ip))

    params = {"myip": ip, "system": "dyndns", "hostname": domain}

    headers = {USER_AGENT: HA_USER_AGENT}

    authentication = hass.helpers.aiohttp_client.BasicAuth(user, password)

    try:
        with async_timeout.timeout(timeout):
            resp = await session.get(url, params=params, headers=headers, auth=authentication)
            body = await resp.text()

            if body.startswith("good") or body.startswith("nochg"):
                return True

            _LOGGER.warning(
                "Updating OVH failed: %s => %s", domain, OVH_ERRORS[body.strip()]
            )

    except aiohttp.ClientError:
        _LOGGER.warning("Can't connect to OVH API")

    except asyncio.TimeoutError:
        _LOGGER.warning("Timeout from OVH API for domain: %s", domain)

    return False