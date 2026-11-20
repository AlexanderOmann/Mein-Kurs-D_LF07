import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from time import sleep


# ----------------------------------------
# MQTT Einstellungen
# ----------------------------------------

BROKER = "localhost"
PORT = 1883
TOPIC = "ampel/eingabe"


# ----------------------------------------
# Keypad GPIO Pins
# ----------------------------------------

REIHEN = [5, 6, 13, 19]
SPALTEN = [12, 16, 20, 21]


# ----------------------------------------
# Tastenbelegung
# ----------------------------------------

TASTEN = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]


# ----------------------------------------
# GPIO vorbereiten
# ----------------------------------------

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

for reihe in REIHEN:
    GPIO.setup(reihe, GPIO.OUT)
    GPIO.output(reihe, GPIO.HIGH)

for spalte in SPALTEN:
    GPIO.setup(
        spalte,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP
    )


# ----------------------------------------
# MQTT Verbindung
# ----------------------------------------

client = mqtt.Client()

client.connect(
    BROKER,
    PORT,
    60
)

client.loop_start()

print("MQTT verbunden.")


# ----------------------------------------
# Keypad auslesen
# ----------------------------------------

def taste_lesen():

    for reihen_nummer, reihen_pin in enumerate(REIHEN):

        GPIO.output(reihen_pin, GPIO.LOW)

        for spalten_nummer, spalten_pin in enumerate(SPALTEN):

            if GPIO.input(spalten_pin) == GPIO.LOW:

                taste = TASTEN[reihen_nummer][spalten_nummer]

                # Warten bis Taste losgelassen wird
                while GPIO.input(spalten_pin) == GPIO.LOW:
                    sleep(0.05)

                GPIO.output(reihen_pin, GPIO.HIGH)

                return taste

        GPIO.output(reihen_pin, GPIO.HIGH)

    return None


# ----------------------------------------
# Hauptprogramm
# ----------------------------------------

print("--------------------------------")
print("Keypad MQTT Sender gestartet")
print("--------------------------------")
print("Drücke eine Taste auf dem Keypad.")
print("Jede Taste wird per MQTT gesendet.")
print("--------------------------------")


try:

    while True:

        taste = taste_lesen()

        if taste is not None:

            print("Taste gedrückt:", taste)

            # MQTT Nachricht senden
            client.publish(
                TOPIC,
                taste
            )

            print(
                "MQTT gesendet:",
                TOPIC,
                "=",
                taste
            )

        sleep(0.05)


except KeyboardInterrupt:

    print()
    print("Programm beendet.")


finally:

    client.loop_stop()
    client.disconnect()

    GPIO.cleanup()

    print("MQTT getrennt.")
    print("GPIO zurückgesetzt.")