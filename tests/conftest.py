"""Test fixtures for Ecowitt IoT tests."""
from unittest.mock import Mock, AsyncMock
import pytest
from homeassistant.core import HomeAssistant

from custom_components.ecowitt_iot.const import DOMAIN
from custom_components.ecowitt_iot.models import EcowittDeviceDescription
from custom_components.ecowitt_iot.coordinator import EcowittDataUpdateCoordinator

@pytest.fixture
def mock_coordinator(hass: HomeAssistant):
    """Create mock coordinator with test data."""
    coordinator = Mock(spec=EcowittDataUpdateCoordinator)

    # Mock device list
    device = EcowittDeviceDescription(
        device_id="12345",
        model=1,
        name="Test Device",
        sw_version="1.0.5"
    )
    coordinator.devices = [device]

    # Mock data property
    coordinator.data = {
        "12345": {
            "command": [{
                "water_status": 0,
                "water_temp": "20.0",
                "flow_velocity": "1.5",
                "water_total": "100.0",
                "wfc01batt": 4,
                "rssi": 3,
                "timeutc": 1600000000
            }]
        }
    }

    # Mock all async methods
    coordinator.async_request_refresh = AsyncMock()
    coordinator.async_refresh = AsyncMock()
    coordinator.set_device_state = AsyncMock()
    coordinator.last_update_success = True

    return coordinator

@pytest.fixture
def mock_add_entities(hass):
    """Create mock add entities helper."""
    return AsyncMock()
