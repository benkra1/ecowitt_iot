"""Test the Ecowitt IoT config flow."""
from __future__ import annotations

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import (
    CONF_HOST,
    CONF_TEMPERATURE_UNIT,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant

from custom_components.ecowitt_iot.const import DOMAIN
from custom_components.ecowitt_iot.sensor import async_setup_entry
from .helpers import MockEntityAdder

pytestmark = pytest.mark.asyncio

async def test_sensor_creation(hass: HomeAssistant, mock_coordinator) -> None:
    """Test creation of sensors."""
    entity_adder = MockEntityAdder(hass)
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id="test_entry",
        title="Test Device",
        data={
            CONF_TEMPERATURE_UNIT: UnitOfTemperature.CELSIUS,
            "devices": [{
                "id": "12345",
                "model": 1,
                "version": "1.0.5",
                "nickname": "Test Device"
            }]
        }
    )

    # Add coordinator to hass
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = mock_coordinator

    # Set up platform
    await async_setup_entry(hass, config_entry, entity_adder.async_add_entities)
    await hass.async_block_till_done()

    # Get added entities
    added_entities = entity_adder.entities
    assert len(added_entities) > 0, "No entities were added"

    # Add entities to HA and update states
    for entity in added_entities:
        entity.hass = hass
        if not entity.entity_id:
            entity.entity_id = f"sensor.test_device_{entity.name}".lower()
        await entity.async_added_to_hass()
        await entity.async_update_ha_state(True)

    await hass.async_block_till_done()

    # Debug output
    all_states = hass.states.async_all()
    print(f"\nAll states: {[state.entity_id for state in all_states]}")

    # Check specific sensors
    state = hass.states.get("sensor.test_device_water_temperature")
    assert state is not None, "Water temperature sensor not found"
    assert state.state == "20.0"
    assert state.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS
