"""Example integration using DataUpdateCoordinator."""

from datetime import datetime
import logging
from zoneinfo import ZoneInfo

from bwt_api.exception import WrongCodeException

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfMass, UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BwtCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up bwt sensors from config entry."""
    my_api = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = BwtCoordinator(hass, my_api)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    try:
        await coordinator.async_config_entry_first_refresh()
    except WrongCodeException as e:
        # Raising ConfigEntryAuthFailed will cancel future updates
        # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        raise ConfigEntryAuthFailed from e

    async_add_entities(
        [
            TotalOutputSensor(coordinator),
            HardnessInSensor(coordinator),
            HardnessOutSensor(coordinator),
            LastServiceCustomerSensor(coordinator),
            LastServiceTechnicianSensor(coordinator),
            StateSensor(coordinator),
            RegenerativLevelSensor(coordinator),
            RegenerativDaySensor(coordinator),
            RegenerativMassSensor(coordinator),
        ]
    )


WATER_ICON = "mdi:water"
GAUGE_ICON = "mdi:gauge"


class TotalOutputSensor(CoordinatorEntity, SensorEntity):
    """Total water [liter] passing through the output."""

    _attr_icon = WATER_ICON
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator):
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "total_output"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.blended_total
        self.async_write_ha_state()


class HardnessInSensor(CoordinatorEntity, SensorEntity):
    """Hardness coming into the device."""

    # _attr_device_class = SensorDeviceClass.WATER

    def __init__(self, coordinator):
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "hardness_in"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.in_hardness.dH
        self.async_write_ha_state()


class HardnessOutSensor(CoordinatorEntity, SensorEntity):
    """Hardness of water leaving the device."""

    # _attr_device_class = SensorDeviceClass.WATER

    def __init__(self, coordinator):
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "hardness_out"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.out_hardness.dH
        self.async_write_ha_state()


class LastServiceCustomerSensor(CoordinatorEntity, SensorEntity):
    """Last service done by customer."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator):
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "customer_service"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # adjust timezone after response from customer service
        self._attr_native_value = datetime.strptime(
            self.coordinator.data.service_customer, "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=ZoneInfo("UTC"))
        self.async_write_ha_state()


class LastServiceTechnicianSensor(CoordinatorEntity, SensorEntity):
    """Last service done by technician."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator):
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "technician_service"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # adjust timezone after response from customer service
        self._attr_native_value = datetime.strptime(
            self.coordinator.data.service_technician, "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=ZoneInfo("UTC"))
        self.async_write_ha_state()


class StateSensor(CoordinatorEntity, SensorEntity):
    """State of the machine.

    0=ok, 1=warning, 2=error
    """

    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, coordinator):
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "state"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.show_error
        self.async_write_ha_state()


class RegenerativLevelSensor(CoordinatorEntity, SensorEntity):
    """percentage of regenerativ left."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator):
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "regenerativ_level"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.regenerativ_level
        self.async_write_ha_state()


class RegenerativDaySensor(CoordinatorEntity, SensorEntity):
    """days of regenerativ left."""

    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator):
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "regenerativ_days"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.regenerativ_days
        self.async_write_ha_state()


class RegenerativMassSensor(CoordinatorEntity, SensorEntity):
    """mass of regenerativ left."""

    _attr_native_unit_of_measurement = UnitOfMass.GRAMS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator):
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "regenerativ_mass"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.regenerativ_total
        self.async_write_ha_state()
