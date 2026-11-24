from gpiozero import AngularServo
from time import sleep

# Servo befindet sich an GPIO 18
servo = AngularServo(
    18,
    min_angle=-90,
    max_angle=90,
    min_pulse_width=0.0005,
    max_pulse_width=0.0025
)

print("Servo-Test startet.")

# 1. Position
print("Position 1")
servo.angle = -90
sleep(2)

# 2. Position
print("Position 2")
servo.angle = -30
sleep(2)

# 3. Position
print("Position 3")
servo.angle = 30
sleep(2)

# 4. Position
print("Position 4")
servo.angle = 90
sleep(2)

# Servo-Signal abschalten
servo.detach()

print("Servo-Test beendet.")