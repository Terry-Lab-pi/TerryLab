import serial
import sys
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import time
from flask import Flask, render_template, request, jsonify
import sqlite3

# Variables globales

#####################
# Servos
kit = ServoKit(channels=16)

servo_sensor = 0
servo_taladro = 4
servo_horizontal = 8

# Rango total 0-425: 232-2873
kit.servo[servo_sensor].set_pulse_width_range(323, 2873)
kit.servo[servo_sensor].actuation_range = 425
kit.servo[servo_taladro].set_pulse_width_range(323, 2873)
kit.servo[servo_taladro].actuation_range = 425
kit.servo[servo_horizontal].set_pulse_width_range(323, 2873)
kit.servo[servo_horizontal].actuation_range = 425
#####################


#####################
# Taladro
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
#####################

# Base de datos
db = 'terry.db'


# Sensor NPK
def medicion_npk(tiempo_medicion):
    # Movimiento horizontal de sensor
    kit.servo[servo_horizontal].angle = 235
    time.sleep(5)

    # Bajar sensor
    kit.servo[servo_sensor].angle = 220
    time.sleep(tiempo_medicion)

    # Iniciar medición
    ser = serial.Serial(port='/dev/serial0', baudrate=4800, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

    data = b'\x01\x03\x00\x00\x00\x07\x04\x08'
    ser.write(data)
    time.sleep(1)

    response = ser.read(ser.in_waiting)

    # Humedad (%)
    humidity = int.from_bytes(response[3:5], byteorder='big')/10
    # Temperatura (°C)
    temperature = int.from_bytes(response[5:7], byteorder='big')/10
    # Conductividad (us/cm)
    conductivity = int.from_bytes(response[7:9], byteorder='big')
    # PH
    ph = int.from_bytes(response[9:11], byteorder='big')/10
    # Nitrógeno (mg/kg)
    nitrogen = int.from_bytes(response[11:13], byteorder='big')
    # Fósforo (mg/kg)
    phosphorus = int.from_bytes(response[13:15], byteorder='big')
    # Potasio (mg/kg)
    potassium = int.from_bytes(response[15:17], byteorder='big')

    ser.close()

    # Subir sensor
    kit.servo[servo_sensor].angle = 0
    time.sleep(3)

    # Regresar a posición inicial
    kit.servo[servo_horizontal].angle = 0
    time.sleep(3)

    # GPIO.cleanup()

    return humidity, temperature, conductivity, ph, nitrogen, phosphorus, potassium


# Encender taladro
def encender_taladro(speed, direction):
    GPIO.output(stby, GPIO.HIGH)  # Disable standby mode
    if direction == "forward":
        GPIO.output(ain1, GPIO.HIGH)
        GPIO.output(ain2, GPIO.LOW)
        pwmA.ChangeDutyCycle(speed)
    if direction == "backward":
        GPIO.output(ain1, GPIO.LOW)
        GPIO.output(ain2, GPIO.HIGH)
        pwmA.ChangeDutyCycle(speed)
    time.sleep(2)
    return

# Apagar taladro
def apagar_taladro():
    pwmA.ChangeDutyCycle(0)
    GPIO.output(stby, GPIO.LOW)
    GPIO.output(stby, GPIO.LOW)
    time.sleep(2)
    return


# Abrir 5 agujeros
def abrir_agujeros():
    posicion_inicial = 0
    incremento_posicion = 17.5
    for i in range(5):
        # Movimiento horizontal del taladro
        kit.servo[servo_horizontal].angle = posicion_inicial + (i * incremento_posicion)

        # Encender taladro
        encender_taladro(100, "forward")

        # Bajar taladro
        kit.servo[servo_taladro].angle = 220
        time.sleep(3)

        # Subir taladro
        kit.servo[servo_taladro].angle = 0
        time.sleep(3)

        # Apagar taladro
        apagar_taladro()
    return


# Inicializar servos
def inicializar_servos():
    apagar_taladro()
    kit.servo[servo_sensor].angle = 0
    kit.servo[servo_taladro].angle = 0
    kit.servo[servo_horizontal].angle = 0
    time.sleep(1)
    return


# Proceso completo de medición
def proceso_medicion():
    # Inicializar servos
    inicializar_servos()

    print("Iniciando Proceso\n")

    # Abrir 5 agujeros
    print("Abriendo agujeros\n")
    abrir_agujeros()

    # Medir NPK
    print("Midiendo parámetros del suelo\n")
    humidity, temperature, conductivity, ph, nitrogen, phosphorus, potassium = medicion_npk(30)

    print("RESULTADOS DE LA MEDICION")
    print("-------------------------")
    print(f"Humedad: {humidity} %")
    print(f"Temperatura: {temperature} C")
    print(f"Conductividad: {conductivity} s/cm")
    print(f"PH: {ph}")
    print(f"Nitrógeno: {nitrogen} mg/kg")
    print(f"Fósforo: {phosphorus} mg/kg")
    print(f"Potasio: {potassium} mg/kg")
    print("-------------------------")

    # Guardar datos en base de datos
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mediciones (FechaHora, Humedad, Temperatura, Conductividad, PH, Nitrogeno, Fosforo, Potasio)
        VALUES (datetime('now', 'localtime'), ?, ?, ?, ?, ?, ?, ?)
    ''', (humidity, temperature, conductivity, ph, nitrogen, phosphorus, potassium))
    conn.commit()
    conn.close()

    results = { "humidity": humidity, "temperature": temperature, "conductivity": conductivity, "ph": ph, "nitrogen": nitrogen, "phosphorus": phosphorus, "potassium": potassium }

    return results


# Inicializar base de datos API
conn = sqlite3.connect(db)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mediciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        FechaHora DateTime,
        Humedad DECIMAL,
        Temperatura DECIMAL,
        Conductividad NUMERIC,
        PH DECIMAL,
        Nitrogeno NUMERIC,
        Fosforo NUMERIC,
        Potasio NUMERIC)
''')
conn.commit()
conn.close()

# Web
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/measure")
def measure():
    results = proceso_medicion()
    return render_template('results.html', results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)