from machine import Pin, PWM, ADC
import time

# Nastavení PWM na GP14 pro LED
led_pwm = PWM(Pin(14))
led_pwm.freq(1000)  # Frekvence 1000 Hz eliminuje blikání viditelné okem

# Nastavení analogového vstupu na GP26
potentiometer = ADC(Pin(26))

while True:
    # Načtení hodnoty z potenciometru (0 až 65535)
    pot_value = potentiometer.read_u16()
    
    # Přímé přiřazení střídy PWM (0 = zhasnuto, 65535 = plný jas)
    led_pwm.duty_u16(pot_value)
    
    time.sleep(0.02)  # Krátká prodleva pro plynulost