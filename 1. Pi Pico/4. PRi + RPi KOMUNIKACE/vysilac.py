from machine import UART, Pin
import time
 
# Inicializace UART1 na pinech GP4 (TX) a GP5 (RX)
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
 
# Tlačítko na GP14 s vnitřním pull-up rezistorem
button = Pin(14, Pin.IN, Pin.PULL_UP)
 
print("Pico 1 (Vysílač) spuštěn.")
 
while True:
    if button.value() == 0:  # Tlačítko stisknuto
        print("Tlačítko stisknuto! Odesílám signál...")
        uart.write(b'1')
        time.sleep(0.5)  # Ochrana proti zákmitům
    time.sleep(0.05)