"""Example integration using DataUpdateCoordinator."""

from datetime import datetime
import logging
from zoneinfo import ZoneInfo

from bwt_api.api import treated_to_blended
from bwt_api.data import BwtStatus
from bwt_api.exception import WrongCodeException

from homeassistant.components.binary_sensor import BinarySensorEntity
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
            ErrorSensor(coordinator),
            WarningSensor(coordinator),
            SimpleSensor(coordinator, "hardness_in", lambda data: data.in_hardness.dH),
            SimpleSensor(
                coordinator, "hardness_out", lambda data: data.out_hardness.dH
            ),
            DeviceClassSensor(
                coordinator,
                "customer_service",
                lambda data: data.service_customer,
                SensorDeviceClass.TIMESTAMP,
            ),
            DeviceClassSensor(
                coordinator,
                "technician_service",
                lambda data: data.service_technician,
                SensorDeviceClass.TIMESTAMP,
            ),
            StateSensor(coordinator),
            UnitSensor(
                coordinator,
                "regenerativ_level",
                lambda data: data.regenerativ_level,
                PERCENTAGE,
            ),
            UnitSensor(
                coordinator,
                "regenerativ_days",
                lambda data: data.regenerativ_days,
                UnitOfTime.DAYS,
            ),
            UnitSensor(
                coordinator,
                "regenerativ_mass",
                lambda data: data.regenerativ_total,
                UnitOfMass.GRAMS,
            ),
            DeviceClassSensor(
                coordinator,
                "last_regeneration_1",
                lambda data: data.regeneration_last_1,
                SensorDeviceClass.TIMESTAMP,
            ),
            DeviceClassSensor(
                coordinator,
                "last_regeneration_2",
                lambda data: data.regeneration_last_2,
                SensorDeviceClass.TIMESTAMP,
            ),
            SimpleSensor(
                coordinator,
                "counter_regeneration_1",
                lambda data: data.regeneration_count_1,
            ),
            SimpleSensor(
                coordinator,
                "counter_regeneration_2",
                lambda data: data.regeneration_count_2,
            ),
            HolidayModeSensor(coordinator),
            HolidayStartSensor(coordinator),
            CalculatedSensor(
                coordinator,
                "day_output",
                UnitOfVolume.LITERS,
                SensorStateClass.TOTAL_INCREASING,
                lambda data: data.treated_day,
            ),
            CalculatedSensor(
                coordinator,
                "month_output",
                UnitOfVolume.LITERS,
                SensorStateClass.TOTAL_INCREASING,
                lambda data: data.treated_month,
            ),
            CalculatedSensor(
                coordinator,
                "year_output",
                UnitOfVolume.LITERS,
                SensorStateClass.TOTAL_INCREASING,
                lambda data: data.treated_year,
            ),
            CalculatedSensor(
                coordinator,
                "capacity_1",
                UnitOfVolume.MILLILITERS,
                SensorStateClass.MEASUREMENT,
                lambda data: data.capacity_1,
            ),
            CalculatedSensor(
                coordinator,
                "capacity_2",
                UnitOfVolume.MILLILITERS,
                SensorStateClass.MEASUREMENT,
                lambda data: data.capacity_2,
            ),
        ]
    )


WATER_ICON = "mdi:water"
GAUGE_ICON = "mdi:gauge"


class TotalOutputSensor(CoordinatorEntity[BwtCoordinator], SensorEntity):
    """Total water [liter] that passed through the output."""

    _attr_icon = WATER_ICON
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator) -> None:
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "total_output"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.blended_total
        self.async_write_ha_state()


class ErrorSensor(CoordinatorEntity[BwtCoordinator], SensorEntity):
    """Errors reported by the device."""

    def __init__(self, coordinator) -> None:
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "errors"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        values = [x.name for x in self.coordinator.data.errors if x.is_fatal()]
        self._attr_native_value = ",".join(values)
        self.async_write_ha_state()


class WarningSensor(CoordinatorEntity[BwtCoordinator], SensorEntity):
    """Warnings reported by the device."""

    def __init__(self, coordinator) -> None:
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "warnings"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        values = [x.name for x in self.coordinator.data.errors if not x.is_fatal()]
        self._attr_native_value = ",".join(values)
        self.async_write_ha_state()


class SimpleSensor(CoordinatorEntity[BwtCoordinator], SensorEntity):
    """Simplest sensor with least configuration options."""

    def __init__(self, coordinator: BwtCoordinator, key: str, extract) -> None:
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = key
        self._attr_unique_id = key
        self._extract = extract

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self._extract(self.coordinator.data)
        self.async_write_ha_state()


class DeviceClassSensor(SimpleSensor):
    """Basic sensor specifying a device class."""

    def __init__(
        self,
        coordinator: BwtCoordinator,
        key: str,
        extract,
        device_class: SensorDeviceClass,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, key, extract)
        self._attr_device_class = device_class


class UnitSensor(SimpleSensor):
    """Sensor specifying a unit."""

    def __init__(
        self, coordinator: BwtCoordinator, key: str, extract, unit: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, key, extract)
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = SensorStateClass.MEASUREMENT


class StateSensor(CoordinatorEntity[BwtCoordinator], SensorEntity):
    """State of the machine."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(BwtStatus.__members__)

    def __init__(self, coordinator) -> None:
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "state"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data.state.name
        self.async_write_ha_state()


class HolidayModeSensor(CoordinatorEntity[BwtCoordinator], BinarySensorEntity):
    """Current holiday mode state."""

    def __init__(self, coordinator) -> None:
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "holiday_mode"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data.holiday_mode == 1
        self.async_write_ha_state()


class HolidayStartSensor(CoordinatorEntity[BwtCoordinator], SensorEntity):
    """Future start of holiday mode if active."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator) -> None:
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = "holiday_mode_start"
        self._attr_unique_id = self._attr_translation_key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        holiday_mode = self.coordinator.data.holiday_mode
        if holiday_mode > 1:
            self._attr_native_value = datetime.fromtimestamp(
                holiday_mode, tz=ZoneInfo("UTC")
            )
        else:
            self._attr_native_value = None
        self.async_write_ha_state()


class CalculatedSensor(CoordinatorEntity[BwtCoordinator], SensorEntity):
    """Sensor calculating blended water from treated water."""

    suggested_display_precision = 0
    suggested_unit_of_measurement = UnitOfVolume.LITERS

    def __init__(
        self,
        coordinator,
        key: str,
        unit: UnitOfVolume,
        stateClass: SensorStateClass,
        extract,
    ) -> None:
        """Initialize the sensor with the common coordinator."""
        super().__init__(coordinator)
        self._attr_translation_key = key
        self._attr_unique_id = self._attr_translation_key
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = stateClass
        self._extract = extract

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = treated_to_blended(
            self._extract(self.coordinator.data),
            self.coordinator.data.in_hardness.dH,
            self.coordinator.data.out_hardness.dH,
        )
        self.async_write_ha_state()
