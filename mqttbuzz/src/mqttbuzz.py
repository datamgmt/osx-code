import rumps
import paho.mqtt.client as mqtt
import threading
import json
import os

# Path to the configuration and help files
CONFIG_FILE = "config.json"
HELP_FILE = "help.txt"

class MQTTBuzzApp(rumps.App):
    def __init__(self):
        self.app_name = "MQTT Buzz"  # Define the application name
        super(MQTTBuzzApp, self).__init__(self.app_name)

        # Load configuration
        self.config = self.load_config()

        # Store MQTT clients for potential disconnect
        self.mqtt_clients = []

        # Store connection state
        self.connected = False

        # Create the menu
        self.menu = ["Connect to MQTT", "Settings", "Help"]  # Added "Help" to the menu

        # Read help text from file
        self.help_text = self.load_help_text()

        # Connect to MQTT brokers at startup
        self.connect_to_mqtt()
        self.connected = True
        self.menu["Connect to MQTT"].title = "Disconnect from MQTT"

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as file:
                return json.load(file)
        else:
            default_config = {
                "mqtt_servers": [
                    {
                        "mqtt_broker": "broker1_address",
                        "mqtt_port": 1883,
                        "mqtt_topic": "topic1",
                        "username": "your_username",
                        "password": "your_password",
                        "sound_name": "Submarine",
                        "header": None,  # Default to broker name if not specified
                        "subheader": None,  # Default to topic if not specified
                        "enabled": True  # Default broker to enabled
                    }
                ],
                "notification_sounds": {
                    "settings_saved": "Glass",
                    "invalid_config": "Basso",
                    "error": "Funk"
                }
            }
            with open(CONFIG_FILE, 'w') as file:
                json.dump(default_config, file, indent=4)
            return default_config

    def save_config(self):
        with open(CONFIG_FILE, 'w') as file:
            json.dump(self.config, file, indent=4)

    def load_help_text(self):
        """Load the help text from the help.txt file."""
        if os.path.exists(HELP_FILE):
            with open(HELP_FILE, 'r') as file:
                return file.read()
        else:
            default_help_text = "This is the MQTT Buzz app. Configure your MQTT settings to connect to different brokers."
            with open(HELP_FILE, 'w') as file:
                file.write(default_help_text)
            return default_help_text

    def toggle_connect(self, sender):
        """Toggle the connection state between connect and disconnect."""
        if self.connected:
            self.disconnect_mqtt_clients()
            sender.title = "Connect to MQTT"
            self.connected = False
        else:
            self.connect_to_mqtt()
            sender.title = "Disconnect from MQTT"
            self.connected = True

    def connect_to_mqtt(self):
        """Connect to all enabled MQTT brokers."""
        # Disconnect any existing MQTT clients
        self.disconnect_mqtt_clients()

        # Start new MQTT clients based on the current configuration
        for server in self.config["mqtt_servers"]:
            # Check if the server is enabled
            if server.get("enabled", False):
                mqtt_thread = threading.Thread(target=self.start_mqtt_client, args=(server,))
                mqtt_thread.daemon = True
                mqtt_thread.start()

        self.notify_with_sound(self.app_name, "Attempting to connect to MQTT brokers", sound_name="Submarine")

    def disconnect_mqtt_clients(self):
        """Disconnect from all MQTT brokers."""
        for client in self.mqtt_clients:
            client.disconnect()
        self.mqtt_clients = []

    def start_mqtt_client(self, server):
        client = mqtt.Client()

        # Set username and password if provided
        if "username" in server and "password" in server:
            client.username_pw_set(server["username"], server["password"])

        # Assigning userdata so that we can access server configuration in callbacks
        client.user_data_set(server)

        # Assigning callbacks using the new API
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect

        try:
            client.connect(server["mqtt_broker"], server["mqtt_port"], 60)
            client.loop_start()  # Use loop_start instead of loop_forever to allow disconnects
            self.mqtt_clients.append(client)
        except Exception as e:
            self.notify_with_sound(f"MQTT Connection Failed ({server['mqtt_broker']})", str(e), sound_name=server.get("sound_name"))

    def on_connect(self, client, userdata, flags, rc):
        # Extract header and subheader
        header = userdata.get("header", userdata["mqtt_broker"])
        subheader = userdata.get("subheader", userdata["mqtt_topic"])

        if rc == 0:
            self.notify_with_sound(header, f"Successfully connected to {header}", subheader=subheader, sound_name=userdata.get("sound_name"))
            client.subscribe(userdata["mqtt_topic"])
        else:
            self.notify_with_sound(header, f"Failed to connect with result code {rc}", subheader=subheader, sound_name=userdata.get("sound_name"))

    def on_message(self, client, userdata, msg):
        # Extract header and subheader
        header = userdata.get("header", userdata["mqtt_broker"])
        subheader = userdata.get("subheader", userdata["mqtt_topic"])
        message = msg.payload.decode()
        self.notify_with_sound(header, message, subheader=subheader, sound_name=userdata.get("sound_name"))

    def on_disconnect(self, client, userdata, rc):
        # Extract header and subheader
        header = userdata.get("header", userdata["mqtt_broker"])
        subheader = userdata.get("subheader", userdata["mqtt_topic"])
        self.notify_with_sound(header, "Disconnected from MQTT broker", subheader=subheader, sound_name=userdata.get("sound_name"))

    def notify_with_sound(self, header, message, subheader=None, sound_name=None):
        # Send notification with an optional sound and subheader
        subtitle = subheader if subheader else ""
        if sound_name is None:
            rumps.notification(title=header, subtitle=subtitle, message=message)
        else:
            rumps.notification(title=header, subtitle=subtitle, message=message, sound=sound_name)

    @rumps.clicked("Settings")
    def settings(self, _):
        response = rumps.Window(
            message="Edit MQTT Settings",
            title="Settings",
            default_text=json.dumps(self.config, indent=4),
            dimensions=(480, 400)  # Updated dimensions to 480x400
        ).run()

        if response.clicked:
            try:
                new_config = json.loads(response.text)
                self.config = new_config
                self.save_config()
                self.notify_with_sound(self.app_name, "The configuration has been updated.", sound_name=self.config["notification_sounds"].get("settings_saved"))
                # Reconnect with the new configuration
                self.connect_to_mqtt()
            except json.JSONDecodeError:
                self.notify_with_sound(self.app_name, "The settings you entered are not valid JSON.", sound_name=self.config["notification_sounds"].get("invalid_config"))
            except Exception as e:
                self.notify_with_sound(self.app_name, str(e), sound_name=self.config["notification_sounds"].get("error"))

    @rumps.clicked("Help")
    def help(self, _):
        # Show a help dialog with text from the help.txt file
        rumps.Window(
            title="Help",
            message=self.help_text,
            dimensions=(480, 400)  # Updated help text box dimensions to 480x400
        ).run()

if __name__ == "__main__":
    app = MQTTBuzzApp()
    # Modify the Connect to MQTT menu item to act as a toggle
    app.menu["Connect to MQTT"].set_callback(app.toggle_connect)
    app.run()