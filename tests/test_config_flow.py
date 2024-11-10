"""Test Ecowitt IoT sensor platform."""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant

from custom_components.ecowitt_iot.const import DOMAIN
from custom_components.ecowitt_iot.coordinator import \
    EcowittDataUpdateCoordinator
from custom_components.ecowitt_iot.models import EcowittDeviceDescription

pytestmark = pytest.mark.asyncio


async def test_sensor_creation(hass: HomeAssistant, mock_coordinator) -> None:
    """Test creation of sensors."""
    # Import here to avoid circular dependencies
    from custom_components.ecowitt_iot.sensor import async_setup_entry

    config_entry = Mock()
    config_entry.entry_id = "test_entry"
    config_entry.data = {
        "temperature_unit": UnitOfTemperature.CELSIUS,
        "devices": [
            {"id": "12345", "model": 1, "version": "1.0.5", "nickname": "Test Device"}
        ],
    }
    config_entry.title = "Test Device"

    # Mock async_add_entities
    async_add_entities = AsyncMock()

    # Add coordinator to hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = mock_coordinator

    # Set up platform
    await async_setup_entry(hass, config_entry, async_add_entities)
    await hass.async_block_till_done()

    # Verify entities were added
    assert async_add_entities.called
    # Get the list of entities that were added
    added_entities = async_add_entities.call_args[0][0]
    assert len(added_entities) > 0

    # Check each entity's state after addition
    for entity in added_entities:
        await entity.async_update()
        await hass.async_block_till_done()

    # Check specific sensors
    state = hass.states.get("sensor.test_device_water_temperature")
    assert state is not None, "Water temperature sensor not found"
    assert state.state == "20.0"
    assert state.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS

    state = hass.states.get("sensor.test_device_flow_rate")
    assert state is not None, "Flow rate sensor not found"
    assert state.state == "1.5"

    state = hass.states.get("sensor.test_device_battery")
    assert state is not None, "Battery sensor not found"
    assert state.state == "80"
    assert state.attributes["unit_of_measurement"] == PERCENTAGE


@pytest.mark.asyncio
async def test_sensor_update(hass: HomeAssistant, mock_coordinator) -> None:
    """Test sensor updates."""
    from custom_components.ecowitt_iot.sensor import async_setup_entry

    config_entry = Mock()
    config_entry.entry_id = "test_entry"
    config_entry.data = {
        "temperature_unit": UnitOfTemperature.CELSIUS,
        "devices": [
            {"id": "12345", "model": 1, "version": "1.0.5", "nickname": "Test Device"}
        ],
    }

    async_add_entities = AsyncMock()

    # Add coordinator to hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = mock_coordinator

    # Set up platform
    await async_setup_entry(hass, config_entry, async_add_entities)
    await hass.async_block_till_done()

    # Get the entities that were added
    added_entities = async_add_entities.call_args[0][0]

    # Simulate coordinator update with new data
    mock_coordinator.data = {
        "12345": {
            "command": [
                {
                    "water_status": 0,
                    "water_temp": "25.0",
                    "flow_velocity": "2.0",
                    "water_total": "150.0",
                    "wfc01batt": 3,
                    "rssi": 3,
                    "timeutc": 1600000100,
                }
            ]
        }
    }

    # Update each entity
    for entity in added_entities:
        await entity.async_update()
    await hass.async_block_till_done()

    # Check updated values
    state = hass.states.get("sensor.test_device_water_temperature")
    assert state.state == "25.0"

    state = hass.states.get("sensor.test_device_flow_rate")
    assert state.state == "2.0"

    state = hass.states.get("sensor.test_device_battery")
    assert state.state == "60"
