import os
import RPi.GPIO as GPIO
from time import sleep
from dotenv import load_dotenv


# ==========================================
# .ENV DATEI LADEN
# ==========================================

load_dotenv()

PASSWORT = os.getenv("PASSWORD")

if not PASSWORT:
    raise RuntimeError(
        "Kein Passwort gefunden! "
        "Bitte PASSWORD in der .env eintragen."
    )


# ==========================================
# KEYPAD
# ==========================================

ROWS = [5, 6, 13, 19]
COLS = [12, 16, 20, 21]

KEYS = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]


# ==========================================
# SCHRITTMOTOR / ULN2003
# ==========================================

# ULN2003:
# IN1 -> GPIO17
# IN2 -> GPIO18
# IN3 -> GPIO22
# IN4 -> GPIO23

MOTOR_PINS = [17, 18, 22, 23]


# ==========================================
# SCHRITTMOTOR-SEQUENZ
# ==========================================

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
# SCHRITTE PRO UMDREHUNG
# ==========================================

SCHRITTE_PRO_UMDREHUNG = 4096


# ==========================================
# HIMMELSRICHTUNGEN
# ==========================================

RICHTUNGEN = {
    "A": ("NORDEN", 0),
    "B": ("OSTEN", 1024),
    "C": ("SUEDEN", 2048),
    "D": ("WESTEN", 3072)
}


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


# Motor-Pins
for pin in MOTOR_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


# ==========================================
# VARIABLEN
# ==========================================

eingabe = ""

freigeschaltet = False

# Motor startet bei Norden
aktuelle_position = 0

# Position innerhalb der Motorsequenz
sequenz_position = 0


# ==========================================
# KEYP