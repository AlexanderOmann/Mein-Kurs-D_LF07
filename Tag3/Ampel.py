from gpiozero import LED
from time import sleep

# Ampel-LEDs
rot = LED(25)
gelb = LED(24)
gruen = LED(23)

while True:

    # ROT leuchtet 5 Sekunden
    rot.on()
    gelb.off()
    gruen.off()
    sleep(5)

    # GELB leuchtet 5 Sekunden
    rot.off()
    gelb.on()
    gruen.off()
    sleep(5)

    # GRUEN leuchtet 5 Sekunden
    rot.off()
    gelb.off()
    gruen.on()
    sleep(5)