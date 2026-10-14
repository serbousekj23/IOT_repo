import network
import socket
import machine
import time
 
# Nastavení pinů enkóderu
clk = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
dt = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
sw = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
 
# Globální proměnné
rychlost = 50
odeslat_toggle = False
odeslat_rychlost = False
posledni_stisk = 0
posledni_krok = 0 # Přidáno pro debouncing otáčení
 
def encoder_handler(pin):
    global rychlost, odeslat_rychlost, posledni_krok
    nyni = time.ticks_ms()
    # Softwarový filtr: ignoruje změny rychlejší než 15 ms
    if time.ticks_diff(nyni, posledni_krok) > 15:
        if dt.value() == 0:
            rychlost = max(0, rychlost - 5)
        else:
            rychlost = min(100, rychlost + 5)
        odeslat_rychlost = True
        posledni_krok = time.ticks_ms()
 
def button_handler(pin):
    global odeslat_toggle, posledni_stisk
    nyni = time.ticks_ms()
    if time.ticks_diff(nyni, posledni_stisk) > 300:
        odeslat_toggle = True
        posledni_stisk = nyni
 
# Navěšení přerušení
clk.irq(trigger=machine.Pin.IRQ_FALLING, handler=encoder_handler)
sw.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_handler)
 
# Wi-Fi připojení
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('izrael', 'picopassword')
 
print("Připojování...")
while not wlan.isconnected():
    time.sleep(0.5)
print('Připojeno!')
 
# UDP Klient
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_ip = '192.168.4.1'
server_port = 5000
 
print("Enkóder připraven!")
 
while True:
    if odeslat_toggle:
        s.sendto(b"TOGGLE", (server_ip, server_port))
        print("Odesláno: TOGGLE")
        odeslat_toggle = False
    if odeslat_rychlost:
        zprava = f"SPEED:{rychlost}"
        s.sendto(zprava.encode('utf-8'), (server_ip, server_port))
        print(f"Odesláno: {zprava}")
        odeslat_rychlost = False
    time.sleep(0.01)