from paho.mqtt.client import Client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

class ClientDevice:
    def __init__(self, device_name, device_id, device_ip, broker_id):
        self.device_name = device_name
        self.device_id = device_id
        self.device_ip = device_ip
        self.broker_id = broker_id
        self.received_messages = []

    def on_mqtt_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        client.subscribe("$SYS/#")

    def on_mqtt_message(client, userdata, msg):
        newMSG = msg.topic + " " + str(msg.payload)
        print(newMSG)

    def init_mqtt(self):
        mqttc = mqtt(callback_api_version=CallbackAPIVersion.VERSION2)
        mqttc.on_connect = self.on_mqtt_connect
        mqttc.on_message = self.on_mqtt_message
        mqttc.connect(self.broker_id)
        mqttc.loop_forever()

clientDevice = ClientDevice("device", "device_id", "device_ip", "broker_id")