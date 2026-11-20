import sqlite3
import RPi.GPIO as GPIO

from datetime import datetime
from pathlib import Path
from time import sleep


# =====================================================
# DATENBANK
# =====================================================

# codes.db wird im gleichen Ordner wie KeyPad.py gesucht
DATENBANK_PFAD = Path(__file__).parent / "codes.db"


def datenbank_vorbereiten():
    """
    Erstellt die Tabellen 'zugang' und 'protokoll',
    falls sie noch nicht vorhanden sind.
    """

    try:
        with sqlite3.connect(DATENBANK_PFAD) as datenbank:
            cursor = datenbank.cursor()

            # Tabelle für Benutzer und gültige Codes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS zugang (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL
                )
            """)

            # Tabelle für Anmeldeversuche
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS protokoll (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zeitpunkt TEXT NOT NULL,
                    benutzer TEXT,
                    ergebnis TEXT NOT NULL
                )
            """)

            datenbank.commit()

        print("Datenbank wurde vorbereitet.")

    except sqlite3.Error as fehler:
        print("Datenbankfehler:", fehler)


def code_pruefen(eingegebener_code):
    """
    Prüft, ob der eingegebene Code in der
    Tabelle 'zugang' vorhanden ist.

    Rückgabe:
    Benutzername = Code gefunden
    None = Code nicht gefunden
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
    Speichert einen Anmeldeversuch in
    der Tabelle 'protokoll'.
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

        print("Anmeldeversuch wurde gespeichert.")

    except sqlite3.Error as fehler:
        print("Fehler beim Speichern:", fehler)


# =====================================================
# GPIO-PINS DER LEDs
# =====================================================

ROT = 25
GELB = 24
GRUEN = 23


# =====================================================
# GPIO-PINS DES 4x4-KEYPADS
# =====================================================

# Keypad-Reihen R1 bis R4
REIHEN = [5, 6, 13, 19]

# Keypad-Spalten C1 bis C4
SPALTEN = [12, 16, 20, 21]


# =====================================================
# TASTENBELEGUNG DES KEYPADS
# =====================================================

TASTEN = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]


# =====================================================
# GPIO VORBEREITEN
# =====================================================

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


# =====================================================
# LED-FUNKTIONEN
# =====================================================

def alle_leds_aus():
    """Schaltet alle LEDs aus."""

    GPIO.output(ROT, GPIO.LOW)
    GPIO.output(GELB, GPIO.LOW)
    GPIO.output(GRUEN, GPIO.LOW)


def zugang_erlaubt():
    """
    Bei einem richtigen Code leuchtet
    Grün fünf Sekunden.
    """

    alle_leds_aus()

    GPIO.output(GRUEN, GPIO.HIGH)
    sleep(5)
    GPIO.output(GRUEN, GPIO.LOW)


def erster_fehler():
    """
    Beim ersten falschen Code:
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
    Beim zweiten falschen Code
    leuchtet Rot dauerhaft.
    """

    alle_leds_aus()
    GPIO.output(ROT, GPIO.HIGH)


# =====================================================
# KEYPAD AUSLESEN
# =====================================================

def taste_lesen():
    """
    Prüft alle Reihen und Spalten des Keypads.

    Rückgabe:
    gedrückte Taste oder None
    """

    for reihen_nummer, reihen_pin in enumerate(REIHEN):

        # Aktuelle Reihe aktivieren
        GPIO.output(reihen_pin, GPIO.LOW)

        for spalten_nummer, spalten_pin in enumerate(SPALTEN):

            # Prüfen, ob eine Taste gedrückt wurde
            if GPIO.input(spalten_pin) == GPIO.LOW:

                taste = TASTEN[reihen_nummer][spalten_nummer]

                # Warten, bis die Taste losgelassen wurde
                while GPIO.input(spalten_pin) == GPIO.LOW:
                    sleep(0.05)

                # Reihe wieder deaktivieren
                GPIO.output(reihen_pin, GPIO.HIGH)

                return taste

        # Reihe wieder deaktivieren
        GPIO.output(reihen_pin, GPIO.HIGH)

    return None


# =====================================================
# PROGRAMMSTART
# =====================================================

alle_leds_aus()
datenbank_vorbereiten()

eingabe = ""
fehler = 0
gesperrt = False

print()
print("----------------------------------------")
print("Codeschloss wurde gestartet")
print("----------------------------------------")
print("PIN mit den Zahlentasten eingeben")
print("# = PIN bestätigen")
print("* = Eingabe löschen")
print("A, B, C und D = ohne Funktion")
print("----------------------------------------")


# =====================================================
# HAUPTPROGRAMM
# =====================================================

try:

    while True:

        # Nach zwei falschen Versuchen bleibt das System gesperrt
        if gesperrt:
            sleep(1)
            continue

        taste = taste_lesen()

        # Wenn keine Taste gedrückt wurde
        if taste is None:
            sleep(0.05)
            continue

        print("Taste:", taste)

        # -------------------------------------------------
        # Eingabe löschen
        # -------------------------------------------------

        if taste == "*":

            eingabe = ""
            print("Eingabe wurde gelöscht.")

        # -------------------------------------------------
        # Eingabe mit # bestätigen
        # -------------------------------------------------

        elif taste == "#":

            if eingabe == "":
                print("Es wurde noch kein PIN eingegeben.")

            else:
                print("PIN wird überprüft ...")

                benutzername = code_pruefen(eingabe)

                # -----------------------------------------
                # Richtiger PIN
                # -----------------------------------------

                if benutzername is not None:

                    print("PIN richtig!")
                    print("Zugang erlaubt für:", benutzername)

                    versuch_speichern(
                        benutzername,
                        "Zugang erlaubt"
                    )

                    zugang_erlaubt()

                    # Eingaben und Fehler zurücksetzen
                    eingabe = ""
                    fehler = 0

                    print("Codeschloss ist wieder bereit.")

                # -----------------------------------------
                # Falscher PIN
                # -----------------------------------------

                else:
                    fehler = fehler + 1

                    print("PIN falsch!")

                    # Erster falscher Versuch
                    if fehler == 1:

                        print("Noch ein Versuch möglich.")

                        versuch_speichern(
                            "Unbekannt",
                            "Falscher PIN - Versuch 1"
                        )

                        erster_fehler()
                        eingabe = ""

                    # Zweiter falscher Versuch
                    elif fehler >= 2:

                        print("Zugang dauerhaft gesperrt!")

                        versuch_speichern(
                            "Unbekannt",
                            "Zugang gesperrt - Versuch 2"
                        )

                        zugang_gesperrt()

                        eingabe = ""
                        gesperrt = True

        # -------------------------------------------------
        # Zahl zur PIN-Eingabe hinzufügen
        # -------------------------------------------------

        elif taste in "0123456789":

            # Maximal acht Stellen zulassen
            if len(eingabe) < 8:

                eingabe = eingabe + taste

                # PIN im Terminal nur als Sternchen anzeigen
                print(
                    "Aktuelle Eingabe:",
                    "*" * len(eingabe)
                )

            else:
                print("Der eingegebene PIN ist zu lang.")

        # -------------------------------------------------
        # Tasten A, B, C und D
        # -------------------------------------------------

        else:
            print(
                "Die Taste",
                taste,
                "hat momentan keine Funktion."
            )

        sleep(0.05)


# =====================================================
# PROGRAMM BEENDEN
# =====================================================

except KeyboardInterrupt:

    print()
    print("Programm wurde mit Strg + C beendet.")


finally:

    alle_leds_aus()
    GPIO.cleanup()

    print("Alle LEDs wurden ausgeschaltet.")
    print("GPIO-Pins wurden zurückgesetzt.")