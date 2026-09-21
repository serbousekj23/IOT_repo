from machine import Pin, I2C
import time

# Nastavení I2C
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=50000)

devices = i2c.scan()
if not devices:
    raise SystemExit("LCD nenalezeno!")
ADDR = devices[0]

BACKLIGHT = 0x08
ENABLE    = 0x04

def pulse_enable(val):
    i2c.writeto(ADDR, bytes([val | ENABLE]))
    time.sleep_us(500)
    i2c.writeto(ADDR, bytes([val & ~ENABLE]))
    time.sleep_us(500)

def send(data, mode=0):
    high = (data & 0xF0) | BACKLIGHT | mode
    pulse_enable(high)
    low = ((data << 4) & 0xF0) | BACKLIGHT | mode
    pulse_enable(low)

def lcd_init():
    time.sleep_ms(100)
    pulse_enable(0x30 | BACKLIGHT)
    time.sleep_ms(10)
    pulse_enable(0x30 | BACKLIGHT)
    time.sleep_ms(10)
    pulse_enable(0x30 | BACKLIGHT)
    time.sleep_ms(10)
    pulse_enable(0x20 | BACKLIGHT)
    time.sleep_ms(10)
    send(0x28, 0)
    send(0x08, 0)
    send(0x01, 0)
    time.sleep_ms(5)
    send(0x06, 0)
    send(0x0C, 0)

def lcd_clear():
    send(0x01, 0)
    time.sleep_ms(2)

def lcd_move_to(col, row):
    # row 0 = 1. radek, row 1 = 2. radek
    addr = (0x80 if row == 0 else 0xC0) + col
    send(addr, 0)

def lcd_print(text):
    for ch in str(text):
        send(ord(ch), 1)

# ================= HLAVNÍ PROGRAM =================
lcd_init()
lcd_clear()

# Výpis na první řádek
lcd_move_to(0, 0)
lcd_print("Ahoj svete!")

# Výpis na druhý řádek
lcd_move_to(0, 1)
lcd_print("Pico funguje :)")

time.sleep(2)
lcd_clear()

# Ukázka dynamického počítadla
pocet = 0
while True:
    lcd_move_to(0, 0)
    lcd_print("Pocitadlo:")
    
    lcd_move_to(0, 1)
    lcd_print(f"{pocet} s       ")  # mezery na konci smažou staré číslice
    
    pocet += 1
    time.sleep(1)