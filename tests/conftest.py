"""Test fixtures for Ecowitt IoT."""
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant

from custom_components.ecowitt_iot.const import DOMAIN
from custom_components.ecowitt_iot.coordinator import \
    EcowittDataUpdateCoordinator
from custom_components.ecowitt_iot.models import EcowittDeviceDescription

pytest_plugins = "pytest_homeassistant_custom_component"

MOCK_DEVICE_DATA = {
    "12345": {
        "command": [
            {
                "water_status": 0,
                "water_temp": "20.0",
                "flow_velocity": "1.5",
                "water_total": "100.0",
                "wfc01batt": 4,
                "rssi": 3,
                "timeutc": 1600000000,
            }
        ]
    }
}


@pytest.fixture
async def mock_coordinator(hass: HomeAssistant) -> EcowittDataUpdateCoordinator:
    """Create a mock coordinator."""
    device = EcowittDeviceDescription(
        device_id="12345", model=1, name="Test Device", sw_version="1.0.5"
    )

    coordinator = EcowittDataUpdateCoordinator(
        hass=hass,
        entry=Mock(
            entry_id="test_entry",
            data={
                "host": "192.168.1.100",
                "temperature_unit": UnitOfTemperature.CELSIUS,
                "devices": [
                    {
                        "id": "12345",
                        "model": 1,
                        "version": "1.0.5",
                        "nickname": "Test Device",
                    }
                ],
            },
        ),
        devices=[device],
    )

    # Mock the update method
    async def mock_update():
        return MOCK_DEVICE_DATA

    coordinator._async_update_data = AsyncMock(side_effect=mock_update)
    coordinator.set_device_state = AsyncMock()

    # Set initial data
    coordinator.data = MOCK_DEVICE_DATA
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    return coordinator


@pytest.fixture(autouse=True)
async def setup_comp(hass):
    """Set up the component and clean up after tests."""
    yield
    await hass.async_block_till_done()

    # Clean up states
    states = hass.states.async_all()
    for state in states:
        hass.states.async_remove(state.entity_id)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    yield


@pytest.fixture(autouse=True)
async def cleanup_timers(hass: HomeAssistant):
    """Clean up timers between tests."""
    yield
    await hass.async_block_till_done()
    for domain in hass.data:
        for coordinator in hass.data.get(domain, {}).values():
            if hasattr(coordinator, "_unschedule_refresh"):
                coordinator._unschedule_refresh()

    # Force cleanup of lingering timers
    for handle in list(hass.loop._scheduled):
        handle.cancel()
