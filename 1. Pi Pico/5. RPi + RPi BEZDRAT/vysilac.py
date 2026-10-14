import network
import socket
import machine
import time
 
# ZMĚNA: Zapnutí PULL_UP rezistoru (klidový stav = 1, stisk = 0)
tlacitko = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
 
# Připojení k Wi-Fi přijímače
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('izrael', 'picopassword')
 
print("Připojování k přijímači...")
while not wlan.isconnected():
    time.sleep(0.5)
 
print('Připojeno!')
 
# Nastavení UDP klienta
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_ip = '192.168.4.1'
server_port = 5000
 
posledni_stav = tlacitko.value()
 
while True:
    aktualni_stav = tlacitko.value()
    # Detekce změny stavu tlačítka
    if aktualni_stav != posledni_stav:
        # ZMĚNA LOGIKY: Při zapojení na GND znamená hodnota 0 stisknuté tlačítko
        if aktualni_stav == 0:
            zprava = "ON"
        else:
            zprava = "OFF"
        try:
            # Odeslání zprávy
            s.sendto(zprava.encode('utf-8'), (server_ip, server_port))
            print("Odesláno:", zprava)
        except Exception as e:
            print("Chyba odeslání:", e)
        posledni_stav = aktualni_stav
        time.sleep(0.05) # Debouncing proti zákmitům