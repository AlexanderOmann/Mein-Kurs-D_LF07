import sqlite3
import RPi.GPIO as GPIO

from datetime import datetime
from pathlib import Path
from time import sleep


# =================================================
# DATENBANK
# =================================================

# Die Datei codes.db muss im gleichen Ordner
# wie KeyPad.py liegen.
DATENBANK_PFAD = Path(__file__).parent / "codes.db"


def protokoll_erstellen():
    """
    Erstellt die Tabelle 'protokoll', falls sie
    noch nicht vorhanden ist.
    """

    try:
        with sqlite3.connect(DATENBANK_PFAD) as datenbank:
            cursor = datenbank.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS protokoll (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zeitpunkt TEXT NOT NULL,
                    benutzer TEXT,
                    ergebnis TEXT NOT NULL
                )
            """)

            datenbank.commit()

    except sqlite3.Error as fehler:
        print("Fehler beim Erstellen des Protokolls:", fehler)


def code_pruefen(eingegebener_code):
    """
    Prüft, ob der eingegebene Code in der
    Tabelle 'zugang' vorhanden ist.

    Rückgabe:
    - Benutzername bei richtigem Code
    - None bei falschem Code
    """

    try:
        with sqlite3.connect(DATENBANK_PFAD) as datenbank:
            cursor = datenbank.cursor()

            cursor.execute(
                """
                SELECT name
                FROM zugang
                WHERE code = ?
                """,
                (eingegebener_code,)
            )

            benutzer = cursor.fetchone()

            if benutzer is not None:
                return benutzer[0]

            return None

    except sqlite3.Error as fehler:
        print("Fehler bei der Codeprüfung:", fehler)
        return None


def versuch_speichern(benutzer, ergebnis):
    """
    Speichert einen Anmeldeversuch in der
    Tabelle 'protokoll'.
    """

    try:
        zeitpunkt = datetime.now().strftime(
            "%d.%m.%Y %H:%M:%S"
        )

        with sqlite3.connect(DATENBANK_PFAD) as datenbank:
            cursor = datenbank.cursor()

            cursor.execute(
                """
                INSERT INTO protokoll
                (zeitpunkt, benutzer, ergebnis)
                VALUES (?, ?, ?)
                """,
                (zeitpunkt, benutzer, ergebnis)
            )

            datenbank.commit()

        print("Anmeldeversuch wurde protokolliert.")

    except sqlite3.Error as fehler:
        print("Fehler beim Speichern des Protokolls:", fehler)


# =================================================
# GPIO-PINS DER LEDs
# =================================================

ROT = 25
GELB = 24
GRUEN = 23


# =================================================
# GPIO-PINS DES 4x4-KEYPADS
# =================================================

# Reihen R1 bis R4
REIHEN = [5, 6, 13, 19]

# Spalten C1 bis C4
SPALTEN = [12, 16, 20, 21]


# =================================================
# TASTENBELEGUNG
# =================================================

TASTEN = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]


# =================================================
# GPIO VORBEREITEN
# =================================================

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# LEDs als Ausgänge einrichten
GPIO.setup(ROT, GPIO.OUT)
GPIO.setup(GELB, GPIO.OUT)
GPIO.setup(GRUEN, GPIO.OUT)

# Keypad-Reihen als Ausgänge einrichten
for reihe in REIHEN:
    GPIO.setup(reihe, GPIO.OUT)
    GPIO.output(reihe, GPIO.HIGH)

# Keypad-Spalten als Eingänge einrichten
for spalte in SPALTEN:
    GPIO.setup(
        spalte,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP
    )


# =================================================
# LED-FUNKTIONEN
# =================================================

def alle_leds_aus():
    """Schaltet alle drei LEDs aus."""

    GPIO.output(ROT, GPIO.LOW)
    GPIO.output(GELB, GPIO.LOW)
    GPIO.output(GRUEN, GPIO.LOW)


def zugang_erlaubt():
    """
    Grün leuchtet fünf Sekunden.
    """

    alle_leds_aus()

    GPIO.output(GRUEN, GPIO.HIGH)
    sleep(5)
    GPIO.output(GRUEN, GPIO.LOW)


def erster_fehler():
    """
    Rot leuchtet eine Sekunde.
    Danach bleibt Gelb eingeschaltet.
    """

    alle_leds_aus()

    GPIO.output(ROT, GPIO.HIGH)
    sleep(1)
    GPIO.output(ROT, GPIO.LOW)

    GPIO.output(GELB, GPIO.HIGH)


def zugang_gesperrt():
    """
    Rot leuchtet dauerhaft.
    """

    alle_leds_aus()
    GPIO.output(ROT, GPIO.HIGH)


# =================================================
# KEYPAD AUSLESEN
# =================================================

def taste_lesen():
    """
    Prüft die vier Reihen und vier Spalten.

    Rückgabe:
    - gedrückte Taste
    - None, wenn keine Taste gedrückt wurde
    """