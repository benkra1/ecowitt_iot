"""Fixtures for Ecowitt IoT tests."""
from unittest.mock import AsyncMock, Mock, patch
import pytest
from homeassistant.core import HomeAssistant
from custom_components.ecowitt_iot.const import DOMAIN
pytest_plugins = "pytest_homeassistant_custom_component"
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations in tests."""
    yield

@pytest.fixture
def mock_setup_entry() -> AsyncMock:
    """Override async_setup_entry."""
    with patch(
        "custom_components.ecowitt_iot.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry

@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = Mock()
    entry.domain = DOMAIN
    entry.title = "Test Device"
    entry.data = {
        "host": "192.168.1.100",
        "devices": [
            {
            "id": "test_device",
            "model": 1,
            "nickname": "Test Device",
            "version": "1.0.0"
            }
        ]
    }
    return entry