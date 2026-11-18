# LED-Klasse aus der gpiozero-Bibliothek importieren.
from gpiozero import LED
# Funktion zum Anhalten des Programms importieren.
from time import sleep

# Eine LED wird am GPIO-Pin 25 angeschlossen und angesprochen.
led = LED(25)

# Die Schleife wird dauerhaft ausgeführt.
while True:
	# LED einschalten.
	led.on()
	# Eine Sekunde lang eingeschaltet bleiben.
	sleep(1)
	# LED ausschalten.
	led.off()
	# Eine Sekunde lang ausgeschaltet bleiben.
	sleep(1)