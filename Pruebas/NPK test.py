# Librerías
import serial
import sys
import time
import RPi.GPIO as GPIO


# Abrir puerto serial
ser = serial.Serial(port='/dev/ttyS0', baudrate=4800, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)


# Solicito medición al sensor
data = b'\x01\x03\x00\x00\x00\x07\x04\x08'
ser.write(data)
time.sleep(0.5)

# Puerto lee resultados del sensor
response = ser.read(ser.in_waiting)
print("Received:" , response)


# Conversión de resultados
humidity = int.from_bytes(response[3:5], byteorder='big')/10
print("Humedad:", humidity, "%")

temperature = int.from_bytes(response[5:7], byteorder='big')/10
print("Temperatura:", temperature, "ºC")

conductivity = int.from_bytes(response[7:9], byteorder='big')
print("Conductividad:", conductivity, "us/cm")

PH = int.from_bytes(response[9:11], byteorder='big')/10
print("PH:", PH, "PH")

nitrogen = int.from_bytes(response[11:13], byteorder='big')
print("Nitrógeno:", nitrogen, "mg/kg")

phosphorus = int.from_bytes(response[13:15], byteorder='big')
print("Fósforo:", phosphorus, "mg/kg")

potassium = int.from_bytes(response[15:17], byteorder='big')
print("Potasio:", potassium, "mg/kg")

ser.close()