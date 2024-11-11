"""Test Ecowitt IoT sensor platform."""

from unittest.mock import Mock

import pytest
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant

from custom_components.ecowitt_iot.const import DOMAIN
from custom_components.ecowitt_iot.sensor import async_setup_entry

from .helpers import MockEntityAdder

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_add_entities(hass):
    """Create mock add entities helper."""
    return MockEntityAdder(hass)


async def test_sensor_creation(
    hass: HomeAssistant, mock_coordinator, mock_add_entities
) -> None:
    """Test creation of sensors."""
    config_entry = Mock()
    config_entry.entry_id = "test_entry"
    config_entry.data = {
        "temperature_unit": UnitOfTemperature.CELSIUS,
        "devices": [
            {"id": "12345", "model": 1, "version": "1.0.5", "nickname": "Test Device"}
        ],
    }

    # Add coordinator to hass
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = mock_coordinator

    # Set up platform
    await async_setup_entry(hass, config_entry, mock_add_entities.async_add_entities)
    await hass.async_block_till_done()

    # Verify entities were added
    assert len(mock_add_entities.entities) > 0, "No entities were added"

    # Check states
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
