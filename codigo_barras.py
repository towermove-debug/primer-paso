
#recibir el dato del codgio de barras a travez de usb 
#y mostrarlo en la pantalla del programa

import serial
import time

# Configurar el puerto serie (ajusta 'COM3' si es necesario)
ser = serial.Serial('COM3', 9600, timeout=1)

def leer_codigo_barras():
    """Lee el código de barras desde el puerto serie"""
    try:
        # Leer una línea del puerto serie
        codigo = ser.readline().decode('utf-8').strip()
        return codigo
    except Exception as e:
        print(f"Error al leer el código de barras: {e}")
        return None

if __name__ == "__main__":
    print("Esperando código de barras...")
    
    while True:
        codigo = leer_codigo_barras()
        if codigo:
            print(f"Código de barras detectado: {codigo}")
        time.sleep(0.1)

#probar para el id de la tabla 