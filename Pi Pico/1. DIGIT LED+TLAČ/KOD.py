from machine import Pin
import time

# Nastavení pinů
led = Pin(14, Pin.OUT)
# Interní pull-up drží pin na 1, stisk tlačítka stáhne pin na 0 (GND)
button = Pin(16, Pin.IN, Pin.PULL_UP)

led_state = False
last_button_val = 1

while True:
    current_val = button.value()
    
    # Detekce stisku: pin byl dříve rozpojený (1) a nyní je sepnutý k zemi (0)
    if last_button_val == 1 and current_val == 0:
        led_state = not led_state
        led.value(led_state)
        # Ochrana proti zákmitům kontaktů (debouncing)
        time.sleep(0.2)
    
    last_button_val = current_val
    time.sleep(0.01)  # Krátká pauza pro odlehčení procesoru