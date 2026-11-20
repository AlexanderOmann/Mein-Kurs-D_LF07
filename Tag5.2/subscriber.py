import sqlite3
from datetime import datetime
import paho.mqtt.client as mqtt


# ---------------------------------
# MQTT
# ---------------------------------

BROKER = "localhost"
TOPIC = "ampel/eingabe"


# ---------------------------------
# Datenbank
# ---------------------------------

datenbank = sqlite3.connect(
    "mqtt.db",
    check_same_thread=False
)

cursor = datenbank.cursor()


# Tabelle erstellen
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    wert TEXT NOT NULL,
    zeitpunkt TEXT NOT NULL
)
""")

datenbank.commit()


# ---------------------------------
# Verbindung zu Mosquitto
# ---------------------------------

def on_connect(client, userdata, flags, rc):

    print("Mit Mosquitto verbunden.")

    client.subscribe(TOPIC)

    print("Topic abonniert:", TOPIC)


# ---------------------------------
# Nachricht empfangen
# ---------------------------------

def on_message(client, userdata, msg):

    wert = msg.payload.decode()

    zeitpunkt = datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )

    print()
    print("Event empfangen")
    print("Topic:", msg.topic)
    print("Wert:", wert)
    print("Zeit:", zeitpunkt)

    # In Datenbank speichern
    cursor.execute(
        """
        INSERT INTO events
        (topic, wert, zeitpunkt)
        VALUES (?, ?, ?)
        """,
        (
            msg.topic,
            wert,
            zeitpunkt
        )
    )

    datenbank.commit()

    print("In Datenbank gespeichert.")


# ---------------------------------
# MQTT starten
# ---------------------------------

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(
    BROKER,
    1883,
    60
)

print("Subscriber gestartet...")
print("Warte auf MQTT Events...")

client.loop_forever()