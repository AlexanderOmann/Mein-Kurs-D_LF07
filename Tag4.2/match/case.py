from gpiozero import LED
from time import sleep
from getpass import getpass

# GPIO-Pins der LEDs
rot = LED(25)
gelb = LED(24)
gruen = LED(23)

# Richtiger Zugangsschluessel
RICHTIGER_KEY = "1234"

# Anzahl der falschen Eingaben
fehler = 0

# Am Anfang sind alle LEDs ausgeschaltet
rot.off()
gelb.off()
gruen.off()

try:
    while fehler < 2:

        # Key eingeben
        eingabe = getpass("Bitte Key eingeben: ")

        # Eingabe pruefen
        match eingabe:

            # Richtiger Key
            case "1234":
                print("Key richtig - Zugang erlaubt!")

                rot.off()
                gelb.off()

                # Gruen leuchtet 5 Sekunden
                gruen.on()
                sleep(5)
                gruen.off()

                break

            # Falscher Key
            case _:
                fehler = fehler + 1
                print("Key falsch!")

                # Fehleranzahl pruefen
                match fehler:

                    # Erster falscher Versuch
                    case 1:
                        print("Noch ein Versuch.")

                        gelb.off()
                        gruen.off()

                        # Rot leuchtet einmal
                        rot.on()
                        sleep(1)
                        rot.off()

                        # Gelb bleibt an
                        gelb.on()

                    # Zweiter falscher Versuch
                    case 2:
                        print("Zugang gesperrt!")

                        gelb.off()
                        gruen.off()

                        # Rot leuchtet dauerhaft
                        rot.on()

                        while True:
                            sleep(1)

                    # Sicherheitshalber
                    case _:
                        print("Unbekannter Fehler")


except KeyboardInterrupt:
    print("\nProgramm beendet.")


finally:
    # LEDs ausschalten
    rot.off()
    gelb.off()
    gruen.off()