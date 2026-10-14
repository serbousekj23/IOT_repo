from machine import UART, Pin
import time
 
# Inicializace UART1 na pinech GP4 (TX) a GP5 (RX)
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
 
# LED dioda na GP15 (pin 20)
led = Pin(15, Pin.OUT)
led.off()
 
print("Pico 2 (Přijímač) poslouchá...")
 
while True:
    if uart.any():
        data = uart.read(1)
        if data == b'1':
            print("Přijat signál! Rozsvěcím LED...")
            led.on()
            time.sleep(2)  # LED svítí 2 sekundy
            led.off()
            print("LED zhasnuta.")
    time.sleep(0.05)