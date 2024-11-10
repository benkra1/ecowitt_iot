"""Tests for the Ecowitt IoT switch platform."""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.ecowitt_iot.switch import (
    EcowittSwitch,
    EcowittSwitchEntityDescription,
)
from custom_components.ecowitt_iot.command_queue import EcowittCommandQueue
from custom_components.ecowitt_iot.const import DOMAIN, MODEL_WFC01

@pytest.fixture
def mock_coordinator():
    """Mock the Ecowitt coordinator."""
    coordinator = Mock()
    coordinator.data = {
        "test_device": {
            "command": [{
                "water_status": 0,
                "ac_status": 0,
            }]
        }
    }
    coordinator.set_device_state = AsyncMock()
    return coordinator

@pytest.fixture
def mock_device():
    """Mock the Ecowitt device."""
    device = Mock()
    device.device_id = "test_device"
    device.model = MODEL_WFC01
    device.device_info = {
        "identifiers": {(DOMAIN, "test_device")},
        "name": "Test Device",
        "manufacturer": "Ecowitt",
        "model": "WFC01",
    }
    return device

@pytest.fixture
def switch_entity_description():
    """Create a switch entity description."""
    return EcowittSwitchEntityDescription(
        key="valve_switch",
        name="Valve",
        status_key="water_status",
    )

@pytest.fixture
def switch(
    hass: HomeAssistant,
    mock_coordinator,
    mock_device,
    switch_entity_description,
):
    """Create a switch instance."""
    command_queue = EcowittCommandQueue(hass)
    return EcowittSwitch(
        coordinator=mock_coordinator,
        device=mock_device,
        description=switch_entity_description,
        command_queue=command_queue,
    )

async def test_switch_turn_on(switch: EcowittSwitch):
    """Test turning on the switch."""
    # Turn on
    await switch.async_turn_on()
    
    # Check coordinator was called
    switch.coordinator.set_device_state.assert_called_once_with(
        "test_device", True
    )
    
    # Check command was queued
    assert switch._command_queue.is_command_pending("test_device")
    cmd_state = switch._command_queue.get_command_state("test_device")
    assert cmd_state.target_state is True

async def test_switch_turn_off(switch: EcowittSwitch):
    """Test turning off the switch."""
    # Turn off
    await switch.async_turn_off()
    
    # Check coordinator was called
    switch.coordinator.set_device_state.assert_called_once_with(
        "test_device", False
    )
    
    # Check command was queued
    assert switch._command_queue.is_command_pending("test_device")
    cmd_state = switch._command_queue.get_command_state("test_device")
    assert cmd_state.target_state is False

async def test_switch_state_attributes(switch: EcowittSwitch):
    """Test switch state attributes."""
    # Add pending command
    switch._command_queue.add_command("test_device", True)
    
    # Get attributes
    attrs = switch.extra_state_attributes
    
    # Check attributes
    assert attrs["command_pending"] is True
    assert attrs["command_target_state"] is True
    assert "command_age" in attrs
    assert attrs["verification_attempts"] == 0

async def test_switch_is_on_pending(switch: EcowittSwitch):
    """Test switch state while command is pending."""
    # Set pending state
    switch._pending_state = True
    
    # Check state
    assert switch.is_on is True

async def test_switch_is_on_error(switch: EcowittSwitch):
    """Test switch state after error."""
    # Add failed command
    switch._command_queue.add_command("test_device", True)
    cmd_state = switch._command_queue.get_command_state("test_device")
    cmd_state.last_error = "Test error"
    
    # Check state
    assert switch.is_on is False
    assert switch._pending_state is None

async def test_switch_state_restore(
    hass: HomeAssistant,
    switch: EcowittSwitch,
):
    """Test switch state restoration."""
    # Set mock state
    await switch.async_added_to_hass()
    
    # Restore state
    state = Mock()
    state.state = STATE_ON
    await switch.async_restore_last_state(state)
    
    # Check state
    assert switch.is_on is True