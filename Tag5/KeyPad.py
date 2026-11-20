import sqlite3
import RPi.GPIO as GPIO
from time import sleep
from pathlib import Path


# -------------------------------------------------
# Datenbank
# -------------------------------------------------

# codes.db wird im gleichen Ordner wie KeyPad.py gesucht
DATENBANK_PFAD = Path(__file__).parent / "codes.db"


def code_pruefen(eingegebener_code):
    """
    Überprüft, ob der eingegebene Code in der Datenbank vorhanden ist.

    Rückgabe:
    - Name des Benutzers, wenn der Code gefunden wurde
    - None, wenn der Code nicht gefunden wurde
    """

    try:
        datenbank = sqlite3.connect(DATENBANK_PFAD)
        cursor = datenbank.cursor()

        cursor.execute(
            "SELECT name FROM zugang WHERE code = ?",
            (eingegebener_code,)
        )

        benutzer = cursor.fetchone()

        datenbank.close()

        if benutzer is not None:
            return benutzer[0]

        return None

    except sqlite3.Error as fehler:
        print("Datenbankfehler:", fehler)
        return None


# -------------------------------------------------
# GPIO-Pins der LEDs
# -------------------------------------------------

ROT = 25
GELB = 24
GRUEN = 23


# -------------------------------------------------
# GPIO-Pins des 4x4-Keypads
# -------------------------------------------------

# Reihen des Keypads: R1, R2, R3, R4
REIHEN = [5, 6, 13, 19]

# Spalten des Keypads: C1, C2, C3, C4
SPALTEN = [12, 16, 20, 21]


# -------------------------------------------------
# Tastenbelegung
# -------------------------------------------------

TASTEN = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]


# -------------------------------------------------
# GPIO vorbereiten
# -------------------------------------------------

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# LEDs als Ausgänge festlegen
GPIO.setup(ROT, GPIO.OUT)
GPIO.setup(GELB, GPIO.OUT)
GPIO.setup(GRUEN, GPIO.OUT)

# Alle LEDs am Anfang ausschalten
GPIO.output(ROT, GPIO.LOW)
GPIO.output(GELB, GPIO.LOW)
GPIO.output(GRUEN, GPIO.LOW)

# Keypad-Reihen als Ausgänge festlegen
for reihe in REIHEN:
    GPIO.setup(reihe, GPIO.OUT)
    GPIO.output(reihe, GPIO.HIGH)

# Keypad-Spalten als Eingänge mit Pull-up-Widerstand festlegen
for spalte in SPALTEN:
    GPIO.setup(
        spalte,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP
    )


# -------------------------------------------------
# Keypad auslesen
# -------------------------------------------------

def taste_lesen():
    """
    Prüft alle Reihen und Spalten des Keypads.

    Rückgabe:
    - gedrückte Taste
    - None, wenn keine Taste gedrückt wurde
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


# -------------------------------------------------
# LED-Funktionen
# -------------------------------------------------

def alle_leds_aus():
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
    Nach dem zweiten falschen Versuch
    leuchtet Rot dauerhaft.
    """

    alle_leds_aus()
    GPIO.output(ROT, GPIO.HIGH)


# -------------------------------------------------
# Hauptprogramm
# -------------------------------------------------

eingabe = ""
fehler = 0
gesperrt = False

print("----------------------------------")
print("Codeschloss wurde gestartet")
print("----------------------------------")
print("Code über das Keypad eingeben.")
print("# = Eingabe bestätigen")
print("* = Eingabe löschen")
print("----------------------------------")

try:

    while True:

        # Wenn das System gesperrt ist,
        # wird keine weitere Eingabe angenommen
        if gesperrt:
            sleep(1)
            continue

        taste = taste_lesen()

        if taste is not None:

            print("Gedrückte Taste:", taste)

            # Eingabe mit * löschen
            if taste == "*":

                eingabe = ""
                print("Eingabe wurde gelöscht.")

            # Eingabe mit # bestätigen
            elif taste == "#":

                if eingabe == "":
                    print("Es wurde noch kein Code eingegeben.")

                else:
                    print("Code wird überprüft ...")

                    benutzername = code_pruefen(eingabe)

                    # Richtiger Code
                    if benutzername is not None:

                        print("Code richtig!")
                        print("Zugang erlaubt für:", benutzername)

                        zugang_erlaubt()

                        # Eingabe und Fehler zurücksetzen
                        eingabe = ""
                        fehler = 0

                        print("Das Codeschloss ist wieder bereit.")

                    # Falscher Code
                    else:

                        fehler = fehler + 1
                        print("Code falsch!")

                        # Erster falscher Versuch
                        if fehler == 1:

                            print("Noch ein Versuch möglich.")

                            erster_fehler()
                            eingabe = ""

                        # Zweiter falscher Versuch
                        elif fehler >= 2:

                            print("Zugang dauerhaft gesperrt!")

                            zugang_gesperrt()
                            gesperrt = True
                            eingabe = ""

            # Zahlen in die Eingabe übernehmen
            elif taste in "0123456789":

                # Maximal acht Zeichen erlauben
                if len(eingabe) < 8:

                    eingabe = eingabe + taste

                    # Im Terminal nur Sternchen anzeigen
                    print("Aktuelle Eingabe:", "*" * len(eingabe))

                else:
                    print("Der eingegebene Code ist zu lang.")

            # Tasten A, B, C und D werden nicht verwendet
            else:
                print(
                    "Die Taste",
                    taste,
                    "hat momentan keine Funktion."
                )

        # Kleine Pause zur Entlastung des Raspberry Pi
        sleep(0.05)


except KeyboardInterrupt:

    print("\nProgramm wurde mit Strg + C beendet.")


finally:

    # GPIO-Pins beim Beenden zurücksetzen
    alle_leds_aus()
    GPIO.cleanup()

    print("GPIO-Pins wurden zurückgesetzt.")