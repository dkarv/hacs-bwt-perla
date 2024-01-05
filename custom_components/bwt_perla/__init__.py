"""The BWT Perla integration."""

import logging

from bwt_api.api import BwtApi
from bwt_api.exception import BwtException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BWT Perla from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    api = BwtApi(entry.data["host"], entry.data["code"])
    try:
        await api.get_current_data()
    except BwtException as e:
        _LOGGER.exception("Error setting up Bwt API")
        await api.close()
        raise ConfigEntryNotReady from e

    hass.data[DOMAIN][entry.entry_id] = api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        api = hass.data[DOMAIN].pop(entry.entry_id)
        await api.close()

    return unload_ok
