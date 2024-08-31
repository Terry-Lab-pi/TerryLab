from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

servo_channel = 0

# Rango 0-360: 500-2660
# Rango 0-390: 500-2873
# Rango total 0-425: 232-2873
kit.servo[servo_channel].set_pulse_width_range(323, 2873)

kit.servo[servo_channel].actuation_range = 425

def test_servo_range(channel):
    kit.servo[channel].angle = 30
    time.sleep(0.5)
    kit.servo[channel].angle = 0
    time.sleep(0.5)
    kit.servo[channel].angle = 90
    time.sleep(0.5)
    kit.servo[channel].angle = 180
    time.sleep(0.5)
    kit.servo[channel].angle = 270
    time.sleep(0.5)
    kit.servo[channel].angle = 360
    time.sleep(0.5)
    kit.servo[channel].angle = 420
    time.sleep(0.5)
    kit.servo[channel].angle = 0
    time.sleep(0.5)

test_servo_range(servo_channel)
























