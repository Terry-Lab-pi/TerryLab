import RPi.GPIO as GPIO
import time

# Configuración de pines GPIO
GPIO.setmode(GPIO.BCM)

# Pines del controlador TB6612FNG
ain1 = 24
ain2 = 23
pwma = 18
stby = 25

# Set GPIO mode
GPIO.setup(ain1, GPIO.OUT)
GPIO.setup(ain2, GPIO.OUT)
GPIO.setup(pwma, GPIO.OUT)
GPIO.setup(stby, GPIO.OUT)

pwmA = GPIO.PWM(pwma, 1000) # Hz frequency
pwmA.start(0)

def drive_motor(speed, direction):
    GPIO.output(stby, GPIO.HIGH)  # Disable standby mode
    if direction == "forward":
        GPIO.output(ain1, GPIO.HIGH)
        GPIO.output(ain2, GPIO.LOW)
        pwmA.ChangeDutyCycle(speed)
    if direction == "backward":
        GPIO.output(ain1, GPIO.LOW)
        GPIO.output(ain2, GPIO.HIGH)
        pwmA.ChangeDutyCycle(speed)

def stop_motor():
    pwmA.ChangeDutyCycle(0)
    GPIO.output(stby, GPIO.LOW)

drive_motor(100, "forward")
time.sleep(10)
stop_motor()

pwmA.stop()
GPIO.cleanup()