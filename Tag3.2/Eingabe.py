from gpiozero import LED
from time import sleep
from getpass import getpass

# GPIO-Pins der LEDs
rot = LED(25)
gelb = LED(24)
gruen = LED(23)

# Richtiger Zugangsschlüssel
RICHTIGER_KEY = "1234"

# Anzahl der falschen Eingaben
fehler = 0

# Am Anfang sind alle LEDs ausgeschaltet
rot.off()
gelb.off()
gruen.off()

try:
    while fehler < 2:

        # Key verdeckt eingeben
        eingabe = getpass("Bitte Key eingeben: ")

        if eingabe == RICHTIGER_KEY:
            print("Key richtig - Zugang erlaubt!")

            rot.off()
            gelb.off()

            # Grün leuchtet 5 Sekunden
            gruen.on()
            sleep(5)
            gruen.off()

            # Programm nach erfolgreicher Eingabe beenden
            break

        else:
            fehler = fehler + 1
            print("Key falsch!")

            # Erster Fehler
            if fehler == 1:
                print("Noch ein Versuch.")

                gelb.off()
                gruen.off()

                # Rot leuchtet einmal auf
                rot.on()
                sleep(1)
                rot.off()

                # Danach bleibt Gelb an
                gelb.on()

            # Zweiter Fehler
            else:
                print("Zugang gesperrt!")

                gelb.off()
                gruen.off()

                # Rot leuchtet dauerhaft
                rot.on()

                # Programm läuft weiter, damit Rot anbleibt
                while True:
                    sleep(1)

except KeyboardInterrupt:
    print("\nProgramm beendet.")

finally:
    # LEDs beim manuellen Beenden ausschalten
    rot.off()
    gelb.off()
    gruen.off()