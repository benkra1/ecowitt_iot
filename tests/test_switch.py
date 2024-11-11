from __future__ import annotations

import pytest
from unittest.mock import Mock, AsyncMock
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_OFF, STATE_ON

from custom_components.ecowitt_iot.const import DOMAIN
from custom_components.ecowitt_iot.switch import async_setup_entry, EcowittSwitch
from .helpers import MockEntityAdder

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_switch_entry():
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry",
        data={
            "devices": [
                {
                    "id": "12345",
                    "model": 1,
                    "version": "1.0.5",
                    "nickname": "Test Device",
                }
            ]
        },
    )


async def test_switch_setup(
    hass: HomeAssistant, mock_coordinator, mock_add_entities, mock_switch_entry
) -> None:
    """Test switch setup."""
    # Add coordinator to hass
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][mock_switch_entry.entry_id] = mock_coordinator

    # Set up platform
    await async_setup_entry(
        hass, mock_switch_entry, mock_add_entities.async_add_entities
    )
    await hass.async_block_till_done()

    # Verify entities were added
    await mock_add_entities.async_add_entities([])
    assert len(mock_add_entities.entities) == 1, "Expected 1 switch"

    # Get the switch entity
    switch_entity = mock_add_entities.entities[0]

    # Add entity to HA
    switch_entity.hass = hass
    await switch_entity.async_added_to_hass()
    await hass.async_block_till_done()

    # Force state update
    await switch_entity.async_update_ha_state(True)
    await hass.async_block_till_done()

    # Check state
    state = hass.states.get(switch_entity.entity_id)
    assert state is not None
    assert state.state == STATE_OFF


async def test_switch_turn_on(
    hass: HomeAssistant, mock_coordinator, mock_add_entities, mock_switch_entry
) -> None:
    """Test turning switch on."""
    # Add coordinator to hass
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][mock_switch_entry.entry_id] = mock_coordinator

    # Set up platform
    await async_setup_entry(
        hass, mock_switch_entry, mock_add_entities.async_add_entities
    )
    await hass.async_block_till_done()

    # Get added entities
    await mock_add_entities.async_add_entities([])
    assert len(mock_add_entities.entities) == 1
    switch_entity = mock_add_entities.entities[0]

    # Add entity to HA
    switch_entity.hass = hass
    await switch_entity.async_added_to_hass()
    await hass.async_block_till_done()

    # Turn on switch
    await switch_entity.async_turn_on()
    await hass.async_block_till_done()

    # Verify coordinator was called correctly
    mock_coordinator.set_device_state.assert_awaited_once_with("12345", True)

    # Update coordinator data to reflect new state
    mock_coordinator.data["12345"]["command"][0].update(
        {"water_status": 1, "water_running": 1}
    )

    # Update state
    await switch_entity.async_update_ha_state(True)
    await hass.async_block_till_done()

    # Verify state
    state = hass.states.get(switch_entity.entity_id)
    assert state is not None
    assert state.state == STATE_ON


async def test_switch_turn_off(
    hass: HomeAssistant, mock_coordinator, mock_add_entities, mock_switch_entry
) -> None:
    """Test turning switch off."""
    # Start with switch on
    mock_coordinator.data["12345"]["command"][0].update(
        {"water_status": 1, "water_running": 1}
    )

    # Add coordinator to hass
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][mock_switch_entry.entry_id] = mock_coordinator

    # Set up platform
    await async_setup_entry(
        hass, mock_switch_entry, mock_add_entities.async_add_entities
    )
    await hass.async_block_till_done()

    # Get added entities
    await mock_add_entities.async_add_entities([])
    assert len(mock_add_entities.entities) == 1
    switch_entity = mock_add_entities.entities[0]

    # Add entity to HA
    switch_entity.hass = hass
    await switch_entity.async_added_to_hass()
    await hass.async_block_till_done()

    # Force initial state
    await switch_entity.async_update_ha_state(True)
    await hass.async_block_till_done()

    # Verify initial state is on
    state = hass.states.get(switch_entity.entity_id)
    assert state is not None
    assert state.state == STATE_ON

    # Turn off switch
    await switch_entity.async_turn_off()
    await hass.async_block_till_done()

    # Verify coordinator was called correctly
    mock_coordinator.set_device_state.assert_awaited_once_with("12345", False)

    # Update coordinator data to reflect new state
    mock_coordinator.data["12345"]["command"][0].update(
        {"water_status": 0, "water_running": 0}
    )

    # Update state
    await switch_entity.async_update_ha_state(True)
    await hass.async_block_till_done()

    # Verify state
    state = hass.states.get(switch_entity.entity_id)
    assert state is not None
    assert state.state == STATE_OFF
