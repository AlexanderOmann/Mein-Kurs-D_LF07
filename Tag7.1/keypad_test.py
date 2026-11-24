import RPi.GPIO as GPIO
import time

# BCM-Nummerierung verwenden
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# GPIO-Pins entsprechend unserer Verdrahtung
ROWS = [5, 6, 13, 19]
COLS = [12, 16, 20, 21]

# Aufbau des 4x4-Keypads
KEYS = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

# Zeilen als Ausgänge
for row in ROWS:
    GPIO.setup(row, GPIO.OUT)
    GPIO.output(row, GPIO.HIGH)

# Spalten als Eingänge mit Pull-Up
for col in COLS:
    GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def read_keypad():

    for row_index, row_pin in enumerate(ROWS):

        # Aktuelle Zeile aktivieren
        GPIO.output(row_pin, GPIO.LOW)

        for col_index, col_pin in enumerate(COLS):

            if GPIO.input(col_pin) == GPIO.LOW:

                taste = KEYS[row_index][col_index]

                # Warten, bis Taste losgelassen wird
                while GPIO.input(col_pin) == GPIO.LOW:
                    time.sleep(0.05)

                GPIO.output(row_pin, GPIO.HIGH)

                return taste

        GPIO.output(row_pin, GPIO.HIGH)

    return None


print("--------------------------")
print("     KEYPAD TEST")
print("--------------------------")
print()
print("Druecke eine Taste.")
print("Beenden mit STRG + C")
print()

try:

    while True:

        taste = read_keypad()

        if taste is not None:
            print("Gedrueckte Taste:", taste)

        time.sleep(0.05)

except KeyboardInterrupt:

    print()
    print("Keypad-Test beendet.")

finally:

    GPIO.cleanup()