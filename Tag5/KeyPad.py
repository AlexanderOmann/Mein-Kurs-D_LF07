import RPi.GPIO as GPIO
from time import sleep

# -----------------------
# LEDs
# -----------------------

ROT = 25
GELB = 24
GRUEN = 23

# -----------------------
# Keypad
# -----------------------

ROWS = [5, 6, 13, 19]
COLS = [12, 16, 20, 21]

KEYS = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

RICHTIGER_KEY = "1234"

GPIO.setmode(GPIO.BCM)

# LEDs als Ausgaenge
GPIO.setup(ROT, GPIO.OUT)
GPIO.setup(GELB, GPIO.OUT)
GPIO.setup(GRUEN, GPIO.OUT)

# Reihen als Ausgaenge
for row in ROWS:
    GPIO.setup(row, GPIO.OUT)
    GPIO.output(row, GPIO.HIGH)

# Spalten als Eingaenge
for col in COLS:
    GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# -----------------------
# Taste erkennen
# -----------------------

def taste_lesen():

    for row_num, row_pin in enumerate(ROWS):

        GPIO.output(row_pin, GPIO.LOW)

        for col_num, col_pin in enumerate(COLS):

            if GPIO.input(col_pin) == GPIO.LOW:

                taste = KEYS[row_num][col_num]

                # Warten bis Taste losgelassen wird
                while GPIO.input(col_pin) == GPIO.LOW:
                    sleep(0.05)

                GPIO.output(row_pin, GPIO.HIGH)

                return taste

        GPIO.output(row_pin, GPIO.HIGH)

    return None


# -----------------------
# Hauptprogramm
# -----------------------

eingabe = ""
fehler = 0

print("Codeschloss gestartet")
print("Code eingeben und mit # bestaetigen.")

try:

    while True:

        taste = taste_lesen()

        if taste is not None:

            print("Taste:", taste)

            # Eingabe loeschen
            if taste == "*":

                eingabe = ""

                print("Eingabe geloescht")

            # Eingabe bestaetigen
            elif taste == "#":

                if eingabe == RICHTIGER_KEY:

                    print("Code richtig!")

                    GPIO.output(ROT, GPIO.LOW)
                    GPIO.output(GELB, GPIO.LOW)

                    GPIO.output(GRUEN, GPIO.HIGH)

                    sleep(5)

                    GPIO.output(GRUEN, GPIO.LOW)

                    break

                else:

                    fehler += 1

                    print("Code falsch!")

                    # Erster Fehler
                    if fehler == 1:

                        print("Noch ein Versuch")

                        GPIO.output(GELB, GPIO.LOW)
                        GPIO.output(GRUEN, GPIO.LOW)

                        # Rot kurz
                        GPIO.output(ROT, GPIO.HIGH)

                        sleep(1)

                        GPIO.output(ROT, GPIO.LOW)

                        # Gelb bleibt an
                        GPIO.output(GELB, GPIO.HIGH)

                        eingabe = ""

                    # Zweiter Fehler
                    else:

                        print("Zugang gesperrt!")

                        GPIO.output(GELB, GPIO.LOW)
                        GPIO.output(GRUEN, GPIO.LOW)

                        # Rot dauerhaft
                        GPIO.output(ROT, GPIO.HIGH)

                        while True:
                            sleep(1)

            # Zahlen speichern
            elif taste in "0123456789":

                eingabe += taste

                print("Code:", "*" * len(eingabe))

        sleep(0.05)


except KeyboardInterrupt:

    print("\nProgramm beendet")


finally:

    GPIO.cleanup()