## Ecowitt IOT device configuration

The **Ecowitt IOT** integration works by polling your Ecowitt gateway device to discover all available IOT devices (currently *WFC01 WittFlow Smart Water Timer* and *AC1100 WittSwitch Smart Plug*), and then creates Homeassistant sensors and switches to match.

This integration is seperate and does not interfere or integrate with the **Ecowitt** core integration [docs](https://www.home-assistant.io/integrations/ecowitt/); they can both be configured against the same Ecowitt gateway device without problems as the operate on a different set of devices. You do probably want both so you can 

To set up this integration:

Add the Ecowitt IOT integration to your Home Assistant instance. When doing so, the config flow will request the Ecowitt GW IP/name on your network, and if it is configured with Celsius or Farenheit temperature reporting.
