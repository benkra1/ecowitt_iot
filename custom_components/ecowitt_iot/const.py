"""Constants for the Ecowitt IoT integration."""

from datetime import timedelta
from typing import Final

DOMAIN: Final = "ecowitt_iot"

# Configuration
CONF_DEVICE_ID: Final = "device_id"
CONF_MODEL: Final = "model"

# Defaults
DEFAULT_NAME: Final = "Ecowitt IoT"
DEFAULT_SCAN_INTERVAL: Final = 30  # seconds

# Device Models
MODEL_AC1100: Final = 2
MODEL_WFC01: Final = 1
MODEL_WFC02: Final = 3  # ADDED: WHC02 support

# Device Status
STATUS_OFFLINE: Final = "offline"
STATUS_ONLINE: Final = "online"

# Attributes
ATTR_DEVICE_ID: Final = "device_id"
ATTR_MODEL: Final = "model"
ATTR_WARNING: Final = "warning"

# Error/Warning Bits
ERROR_BITS_AC1100: Final[dict[int, str]] = {
    0: "leak_current",
    1: "no_load",
    2: "low_current",
    3: "overload",
    4: "relay_abnormal",
    7: "offline",
}

ERROR_BITS_WFC01: Final[dict[int, str]] = {
    0: "leak",
    1: "no_water",
    2: "temp_low",
    3: "temp_high",
    4: "low_battery",
    7: "offline",
}
