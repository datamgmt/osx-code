# Configuring MQTTBuzz

To configure MQTTBuzz, follow these steps:

## Configure the application

You can configure and update the settings directly from the UI:

 * Click on the MQTTBuzz icon in the macOS toolbar.
 * Select Settings.
 * A window will open with the current configuration in JSON format.
 * Edit the configuration as needed and click OK to save.

Note: Make sure the edited JSON is valid. An error will be displayed if the configuration is invalid.

Configuration Parameters

In the mqtt_servers section:

 * mqtt_broker: The address of the MQTT broker.
 * mqtt_port: The port number of the MQTT broker (default is 1883).
 * mqtt_topic: The topic to subscribe to.
 * username: The username for MQTT broker authentication (if required).
 * password: The password for MQTT broker authentication (if required).
 * header: Optional. The title for notifications (defaults to the broker name if not provided).
 * subheader: Optional. The subtitle for notifications (defaults to the topic name if not provided).
 * broker_enabled: Boolean. Whether this broker is enabled (default is true). This allows an individual broker to be turned off without removing the entire configuration 
 * sounds_enabled: Boolean. Whether to enable sound for notifications for the specific broker (default is true).
 * filter: Type of message filtering:
     * "none": Default No filtering, all messages are sent as notifications.
     * "dedup": Deduplicates messages, only sending notifications for new messages.
     * "throttle": Throttles notifications, limiting the frequency based on filter_time.
 * filter_time: Time in seconds for filtering (applicable for dedup and throttle).

Global parameters:

 * sounds_enabled: Boolean. This enables sounds for the entire application. For a sound to be heard both the global parameter and the broker-specific parameter need to be true
 
## Example MQTTBuzz configuration

```
{
    "mqtt_servers": [
        {
            "mqtt_broker": "broker1.example.com",
            "mqtt_port": 1883,
            "mqtt_topic": "home/livingroom/temperature",
            "username": "user1",
            "password": "password1",
            "header": "Living Room",
            "subheader": "Temperature",
            "broker_enabled": false,
            "sounds_enabled": false,
            "filter": "none",  # No filtering
            "filter_time": 0  # Not used when filter is 'none'
        },
        {
            "mqtt_broker": "broker2.example.com",
            "mqtt_port": 1883,
            "mqtt_topic": "office/desk/light",
            "username": "user2",
            "password": "password2",
            "sound_name": "Glass",
            "header": null,  # Will default to the mqtt_broker value
            "subheader": null,  # Will default to the mqtt_topic value
            "broker_enabled": true,
            "sounds_enabled": true,
            "filter": "dedup",  # Deduplicate messages
            "filter_time": 10  # 10 seconds deduplication window
        },
        {
            "mqtt_broker": "broker3.example.com",
            "mqtt_port": 1883,
            "mqtt_topic": "kitchen/fridge/door",
            "username": "user3",
            "password": "password3",
            "sound_name": "Ping",
            "header": "Kitchen",
            "subheader": null,  # Will default to the mqtt_topic value
            "broker_enabled": true,
            "sounds_enabled": true,
            "filter": "throttle",  # Throttle messages
            "filter_time": 5  # 5 seconds throttle window
        }
    ],
    "sounds_enabled": false
}
```
