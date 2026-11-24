import RPi.GPIO as GPIO
from time import sleep

# ==========================================
# EINSTELLUNGEN
# ==========================================

PASSWORT = "2580"

# Keypad-Pins
ROWS = [5, 6, 13, 19]
COLS = [12, 16, 20, 21]

KEYS = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

# ULN2003-Pins: IN1, IN2, IN3, IN4
MOTOR_PINS = [17, 18, 22, 23]

# Der 28BYJ-48 benötigt ungefähr 4096 Halbschritte
# für eine vollständige Umdrehung.
SCHRITTE_PRO_UMDREHUNG = 4096

# Positionen der vier Himmelsrichtungen
RICHTUNGEN = {
    "A": ("NORDEN", 0),
    "B": ("OSTEN", 1024),
    "C": ("SUEDEN", 2048),
    "D": ("WESTEN", 3072)
}

# Halbschrittfolge
SEQUENZ = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

# ==========================================
# GPIO EINRICHTEN
# ==========================================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Keypad-Zeilen
for row in ROWS:
    GPIO.setup(row, GPIO.OUT)
    GPIO.output(row, GPIO.HIGH)

# Keypad-Spalten
for col in COLS:
    GPIO.setup(
        col,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP
    )

# Motoranschlüsse
for pin in MOTOR_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# ==========================================
# PROGRAMMVARIABLEN
# ==========================================

eingabe = ""
freigeschaltet = False

# Wichtig:
# Beim Programmstart muss der Zeiger auf Norden stehen.
aktuelle_position = 0

# Aktuelle Position innerhalb der Schrittabfolge
sequenz_position = 0

# ==========================================
# KEYPAD AUSLESEN
# ==========================================

def taste_lesen():

    for row_index, row_pin in enumerate(ROWS):

        GPIO.output(row_pin, GPIO.LOW)

        for col_index, col_pin in enumerate(COLS):

            if GPIO.input(col_pin) == GPIO.LOW:

                taste = KEYS[row_index][col_index]

                # Warten, bis die Taste losgelassen wird
                while GPIO.input(col_pin) == GPIO.LOW:
                    sleep(0.05)

                GPIO.output(row_pin, GPIO.HIGH)

                sleep(0.15)

                return taste

        GPIO.output(row_pin, GPIO.HIGH)

    return None

# ==========================================
# MOTOR ABSCHALTEN
# ==========================================

def motor_abschalten():

    for pin in MOTOR_PINS:
        GPIO.output(pin, GPIO.LOW)

# ==========================================
# EINEN HALBSCHRITT AUSFÜHREN
# ==========================================

def einzelner_schritt(richtung):

    global sequenz_position

    # Sequenzposition verändern
    sequenz_position = (
        sequenz_position + richtung
    ) % len(SEQUENZ)

    schritt = SEQUENZ[sequenz_position]

    for pin, wert in zip(MOTOR_PINS, schritt):
        GPIO.output(pin, wert)

    sleep(0.0015)

# ==========================================
# MOTOR ZU EINER POSITION FAHREN
# ==========================================

def fahre_zu(zielposition):

    global aktuelle_position

    # Abstand im Uhrzeigersinn
    differenz = (
        zielposition - aktuelle_position
    ) % SCHRITTE_PRO_UMDREHUNG

    # Kürzesten Weg auswählen
    if differenz <= SCHRITTE_PRO_UMDREHUNG // 2:

        richtung = 1
        anzahl_schritte = differenz

    else:

        richtung = -1
        anzahl_schritte = (
            SCHRITTE_PRO_UMDREHUNG - differenz
        )

    print("Motorschritte:", anzahl_schritte)

    for _ in range(anzahl_schritte):
        einzelner_schritt(richtung)

    aktuelle_position = zielposition

    # Motor nach dem Erreichen der Position abschalten
    motor_abschalten()

# ==========================================
# HIMMELSRICHTUNG EINSTELLEN
# ==========================================

def himmelsrichtung_einstellen(taste):

    name, zielposition = RICHTUNGEN[taste]

    print()
    print("============================")
    print("Fahre nach:", name)
    print("============================")

    fahre_zu(zielposition)

    print(name, "erreicht.")
    print()

# ==========================================
# STARTANZEIGE
# ==========================================

print()
print("============================")
print(" KOMPASS-STEUERUNG")
print("============================")
print()
print("WICHTIG:")
print("Zeiger vor dem Start auf")
print("NORDEN stellen.")
print()
print("System ist GESPERRT.")
print("Passwort eingeben.")
print("Mit # bestaetigen.")
print()

# ==========================================
# HAUPTPROGRAMM
# ==========================================

try:

    while True:

        taste = taste_lesen()

        if taste is None:
            sleep(0.05)
            continue

        # ----------------------------------
        # SYSTEM IST GESPERRT
        # ----------------------------------

        if not freigeschaltet:

            if taste in "0123456789":

                eingabe += taste

                print(
                    "Passwort:",
                    "*" * len(eingabe)
                )

            elif taste == "*":

                eingabe = ""

                print("Eingabe geloescht.")

            elif taste == "#":

                if eingabe == PASSWORT:

                    freigeschaltet = True

                    print()
                    print("============================")
                    print(" PASSWORT RICHTIG")
                    print("============================")
                    print()
                    print("Steuerung freigeschaltet.")
                    print()
                    print("A = Norden")
                    print("B = Osten")
                    print("C = Sueden")
                    print("D = Westen")
                    print()
                    print("* = System sperren")
                    print()

                else:

                    print()
                    print("PASSWORT FALSCH!")
                    print("Bitte erneut versuchen.")
                    print()

                eingabe = ""

        # ----------------------------------
        # SYSTEM IST FREIGESCHALTET
        # ----------------------------------

        else:

            if taste in RICHTUNGEN:

                himmelsrichtung_einstellen(taste)

            elif taste == "*":

                freigeschaltet = False
                eingabe = ""

                print()
                print("============================")
                print(" SYSTEM GESPERRT")
                print("============================")
                print()
                print("Passwort erneut eingeben.")
                print("Mit # bestaetigen.")
                print()

except KeyboardInterrupt:

    print()
    print("Programm beendet.")

finally:

    motor_abschalten()
    GPIO.cleanup()