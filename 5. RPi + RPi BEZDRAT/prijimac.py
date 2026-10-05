import network
import socket
import machine
import time
 
# Nastavení LED
led = machine.Pin(15, machine.Pin.OUT)
led.value(0) # Pro jistotu na začátku zhasneme
 
# Vytvoření Wi-Fi Access Pointu
ap = network.WLAN(network.AP_IF)
ap.config(essid='izrael', password='picopassword')
ap.active(True)
 
while not ap.active():
    pass
 
print('Wi-Fi vytvořena. IP adresa Pica:', ap.ifconfig()[0])
 
# Nastavení UDP serveru
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Použití 0.0.0.0 zajistí naslouchání na všech rozhraních
s.bind(('0.0.0.0', 5000))
# Odstranili jsme s.setblocking(False), kód teď bude čekat na paket
 
print("Čekám na příkazy...")
 
while True:
    try:
        # Program se zde zastaví a čeká na data ze sítě
        data, addr = s.recvfrom(1024)
        zprava = data.decode('utf-8')
       
        # Vypíše nejen zprávu, ale i IP adresu vysílače
        print("Přijato od", addr[0], ":", zprava)
       
        # Rozsvícení nebo zhasnutí LED
        if zprava == 'ON':
            led.value(1)
        elif zprava == 'OFF':
            led.value(0)
           
    except Exception as e:
        print("Chyba při příjmu:", e)