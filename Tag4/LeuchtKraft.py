from gpiozero import PWMLED
from signal import pause

# LEDs festlegen
rot = PWMLED(17)
gelb = PWMLED(27)
gruen = PWMLED(22)

# Helligkeit einstellen
rot.value = 1.0       # Rot = 100 %
gelb.value = 0.5      # Gelb = 50 %
gruen.value = 0.1     # Gruen = 10 %

# Programm weiterlaufen lassen
pause()
