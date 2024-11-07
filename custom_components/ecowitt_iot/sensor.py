"""Support for Ecowitt IoT sensors."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfVolume,
    UnitOfVolumeFlowRate,  # Use this instead of VOLUME_FLOW_RATE
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODEL_AC1100
from .coordinator import EcowittDataUpdateCoordinator
from .models import EcowittDeviceDescription

_LOGGER = logging.getLogger(__name__)


@dataclass
class EcowittSensorEntityDescription(SensorEntityDescription):
    """Describes Ecowitt sensor entity."""

    value_fn: str | None = None


AC1100_SENSORS = [
    EcowittSensorEntityDescription(
        key="power",
        name="Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn="realtime_power",
    ),
    EcowittSensorEntityDescription(
        key="voltage",
        name="Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn="ac_voltage",
    ),
    EcowittSensorEntityDescription(
        key="current",
        name="Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn="ac_current",
    ),
    EcowittSensorEntityDescription(
        key="energy",
        name="Energy",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn="elect_total",
    ),
]

WFC01_SENSORS = [
    EcowittSensorEntityDescription(
        key="flow_rate",
        name="Flow Rate",
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn="flow_velocity",
    ),
    EcowittSensorEntityDescription(
        key="total_water",
        name="Total Water",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn="water_total",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ecowitt sensor based on a config entry."""
    coordinator: EcowittDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[EcowittSensor] = []

    for device in coordinator.devices:
        sensors = AC1100_SENSORS if device.model == MODEL_AC1100 else WFC01_SENSORS
        for description in sensors:
            entities.append(
                EcowittSensor(
                    coordinator=coordinator,
                    device=device,
                    description=description,
                )
            )

    async_add_entities(entities)


class EcowittSensor(CoordinatorEntity[EcowittDataUpdateCoordinator], SensorEntity):
    """Representation of an Ecowitt sensor."""

    entity_description: EcowittSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcowittDataUpdateCoordinator,
        device: EcowittDeviceDescription,
        description: EcowittSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device = device
        self._attr_unique_id = f"{DOMAIN}_{device.device_id}_{description.key}"
        self._attr_device_info = device.device_info

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        try:
            device_data = self.coordinator.data[self._device.device_id]["command"][0]
            return float(device_data.get(self.entity_description.value_fn, 0))
        except (KeyError, IndexError, ValueError, TypeError):
            return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self._device.device_id in self.coordinator.data
            and len(self.coordinator.data[self._device.device_id].get("command", [])) > 0
        )