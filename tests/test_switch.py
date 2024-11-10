"""Test Ecowitt IoT switch platform."""
from unittest.mock import Mock

import pytest
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant

from custom_components.ecowitt_iot.const import DOMAIN
from custom_components.ecowitt_iot.switch import async_setup_entry

from .helpers import MockEntityAdder

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_add_entities(hass):
    """Create mock add entities helper."""
    return MockEntityAdder(hass)


async def test_switch_setup(
    hass: HomeAssistant, mock_coordinator, mock_add_entities
) -> None:
    """Test switch setup."""
    config_entry = Mock()
    config_entry.entry_id = "test_entry"
    config_entry.data = {
        "devices": [
            {"id": "12345", "model": 1, "version": "1.0.5", "nickname": "Test Device"}
        ]
    }

    # Add coordinator to hass
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = mock_coordinator

    # Set up platform
    await async_setup_entry(hass, config_entry, mock_add_entities.async_add_entities)
    await hass.async_block_till_done()

    # Verify switch was added
    assert len(mock_add_entities.entities) > 0, "No switches were added"

    # Check state
    state = hass.states.get("switch.test_device_valve")
    assert state is not None, "Switch state not found"
    assert state.state == STATE_OFF


async def test_switch_turn_on(
    hass: HomeAssistant, mock_coordinator, mock_add_entities, aioclient_mock
) -> None:
    """Test turning switch on."""
    # Mock success response for turn on command
    aioclient_mock.post("http://192.168.1.100/parse_quick_cmd_iot", text="200 OK")

    config_entry = Mock()
    config_entry.entry_id = "test_entry"
    config_entry.data = {
        "devices": [
            {"id": "12345", "model": 1, "version": "1.0.5", "nickname": "Test Device"}
        ]
    }

    # Add coordinator to hass
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = mock_coordinator

    # Set up platform
    await async_setup_entry(hass, config_entry, mock_add_entities.async_add_entities)
    await hass.async_block_till_done()

    # Get first switch
    assert len(mock_add_entities.entities) > 0, "No switches were added"
    switch_entity = mock_add_entities.entities[0]

    # Turn on
    await switch_entity.async_turn_on()
    await hass.async_block_till_done()

    # Check state
    state = hass.states.get("switch.test_device_valve")
    assert state.state == STATE_ON


async def test_switch_turn_off(
    hass: HomeAssistant, mock_coordinator, mock_entities, aioclient_mock
) -> None:
    """Test turning switch off."""
    # Mock success response for turn off command
    aioclient_mock.post("http://192.168.1.100/parse_quick_cmd_iot", text="200 OK")

    config_entry = Mock()
    config_entry.entry_id = "test_entry"
    config_entry.data = {
        "devices": [
            {"id": "12345", "model": 1, "version": "1.0.5", "nickname": "Test Device"}
        ]
    }

    # Add coordinator to hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = mock_coordinator

    # Set up platform
    await async_setup_entry(hass, config_entry, mock_entities.async_add_entities)
    await hass.async_block_till_done()

    # Turn off switch
    switch_entity = mock_entities.entities[0]
    await switch_entity.async_turn_off()
    await hass.async_block_till_done()

    # Check that coordinator was called with correct parameters
    assert mock_coordinator.set_device_state.called
    assert mock_coordinator.set_device_state.call_args[0] == ("12345", False)

    # Update coordinator data to reflect new state
    new_data = {
        "12345": {
            "command": [
                {
                    "water_status": 0,
                    "always_on": 0,
                    "water_running": 0,
                    "rssi": 3,
                    "timeutc": 1600000000,
                }
            ]
        }
    }
    mock_coordinator.data = new_data
    await mock_coordinator.async_refresh()
    await hass.async_block_till_done()

    # Verify state
    state = hass.states.get("switch.test_device_valve")
    assert state.state == STATE_OFF
