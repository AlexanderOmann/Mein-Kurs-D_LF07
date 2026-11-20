import paho.mqtt.client as mqtt
from time import sleep

BROKER = "localhost"
TOPIC = "ampel/eingabe"

client = mqtt.Client()

client.connect(BROKER, 1883, 60)

werte = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20"
]

for wert in werte:

    client.publish(TOPIC, wert)

    print("Gesendet:", wert)

    sleep(1)

client.disconnect()

print("Alle Events wurden gesendet.")