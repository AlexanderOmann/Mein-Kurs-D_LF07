from gpiozero import PWMLED
from time import sleep
from getpass import getpass

# LEDs mit PWM
rot = PWMLED(25)
gelb = PWMLED(24)
gruen = PWMLED(23)

# Richtiger Key
RICHTIGER_KEY = "1234"

fehler = 0

# Alle LEDs am Anfang aus
rot.off()
gelb.off()
gruen.off()

try:
    while fehler < 2:

        eingabe = getpass("Bitte Key eingeben: ")

        # KEY RICHTIG
        if eingabe == RICHTIGER_KEY:
            print("Key richtig - Zugang erlaubt!")

            rot.off()
            gelb.off()

            # Gruen leuchtet sehr schwach mit 10 %
            gruen.value = 0.1
            sleep(5)
            gruen.off()

            break

        # KEY FALSCH
        else:
            fehler += 1
            print("Key falsch!")

            # ERSTER FEHLER
            if fehler == 1:
                print("Noch ein Versuch.")

                gelb.off()
                gruen.off()

                # Rot leuchtet normal mit 100 %
                rot.value = 1.0
                sleep(1)
                rot.off()

                # Gelb bleibt mit 50 % Helligkeit an
                gelb.value = 0.5

            # ZWEITER FEHLER
            else:
                print("Zugang gesperrt!")

                gelb.off()
                gruen.off()

                # Rot leuchtet dauerhaft mit 100 %
                rot.value = 1.0

                while True:
                    sleep(1)

except KeyboardInterrupt:
    print("\nProgramm beendet.")

finally:
    rot.off()
    gelb.off()
    gruen.off()