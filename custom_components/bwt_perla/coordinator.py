"""Coordinator to fetch the data once for all sensors."""

import asyncio
from datetime import timedelta
import logging

from bwt_api.api import BwtApi

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

_UPDATE_INTERVAL_MIN = 1
_UPDATE_INTERVAL_MAX = 30


class BwtCoordinator(DataUpdateCoordinator):
    """Bwt coordinator."""

    def __init__(self, hass: HomeAssistant, my_api: BwtApi) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="My sensor",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=_UPDATE_INTERVAL_MAX),
        )
        self.my_api = my_api

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        #        try:
        # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        async with asyncio.timeout(10):
            new_values = await self.my_api.get_current_data()
            self.update_interval = calculate_update_interval(
                self.update_interval, new_values.current_flow
            )
            return new_values


def calculate_update_interval(current_interval: timedelta | None, current_flow: int):
    """Calculate the new update interval, based on the old one and the current flow."""

    if current_flow > 0:
        return timedelta(seconds=_UPDATE_INTERVAL_MIN)
    if current_interval is None:
        return timedelta(seconds=_UPDATE_INTERVAL_MAX)
    if current_interval.seconds >= _UPDATE_INTERVAL_MAX:
        return current_interval
    # Increase the interval to max if there is no flow at the moment
    return timedelta(seconds=min(_UPDATE_INTERVAL_MAX, current_interval.seconds * 2))
