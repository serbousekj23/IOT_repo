from machine import I2C, Pin, mem32
import time
 
LED_PIN = 15
I2C_ADDR = 0x41
 
# Nastavení LED
led = Pin(LED_PIN, Pin.OUT)
led.value(0)
 
# 1. Necháme MicroPython klasicky nastavit piny pro I2C0 v Master režimu
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
 
# 2. Hack: Sáhneme přímo do registrů čipu RP2040 a přepíšeme to na Slave
I2C0_BASE = 0x40044000
 
# Vypnutí I2C (zápis 0 do registru IC_ENABLE)
mem32[I2C0_BASE + 0x6C] = 0
 
# Přečtení aktuální konfigurace (registr IC_CON)
ic_con = mem32[I2C0_BASE + 0x00]
# Pomocí bitové masky (~0x41) vymažeme bit 0 (MASTER_MODE) a bit 6 (IC_SLAVE_DISABLE)
ic_con &= ~0x41
mem32[I2C0_BASE + 0x00] = ic_con
 
# Nastavení adresy (registr IC_SAR na hodnotu 0x41)
mem32[I2C0_BASE + 0x08] = I2C_ADDR
 
# Opětovné zapnutí I2C (IC_ENABLE)
mem32[I2C0_BASE + 0x6C] = 1
 
print(f"Pico jede jako I2C Slave na adrese {hex(I2C_ADDR)}")
 
# Smyčka pro čtení příchozích dat
while True:
    # Kontrola bitu 3 (RFNE - Receive FIFO Not Empty) v registru IC_STATUS
    # Zjišťujeme, jestli velká malina něco neposlala
    if mem32[I2C0_BASE + 0x70] & 0x08:
        # Přečteme samotný bajt dat (registr IC_DATA_CMD)
        command = mem32[I2C0_BASE + 0x10] & 0xFF
        print("Prijato:", command)
        # Rozsvítíme nebo zhasneme LEDku
        if command == 1:
            led.value(1)
        elif command == 0:
            led.value(0)
    # Krátká pauza, ať se nepřehřeje procesor
    time.sleep(0.01)