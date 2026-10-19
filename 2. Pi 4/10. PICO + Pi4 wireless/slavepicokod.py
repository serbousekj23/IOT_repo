import network
import socket
from machine import Pin
 
# Název a heslo sítě, kterou Pico vytvoří (heslo musí mít min 8 znaků)
SSID = 'Pico_Siet'
PASSWORD = 'tajneheslo'
 
# Nastavení LED
led = Pin(15, Pin.OUT)
led.value(0)
 
# Vytvoření vlastní Wi-Fi sítě (Access Point)
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)
 
# Získání IP adresy (zpravidla to bude 192.168.4.1)
ip = ap.ifconfig()[0]
 
print("====================================")
print(f"Wi-Fi úspěšně vytvořena!")
print(f"Název sítě: {SSID}")
print(f"Heslo: {PASSWORD}")
print(f"IP adresa Pica: {ip}")
print("====================================")
 
# Spuštění malého serveru na portu 80
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
 
print('Čekám na příkazy od velkého Raspberry...')
 
while True:
    try:
        cl, addr = s.accept()
        request = cl.recv(1024).decode('utf-8')
        if '/on' in request:
            led.value(1)
            print("Zapínám LED")
        elif '/off' in request:
            led.value(0)
            print("Vypínám LED")
        response = "HTTP/1.0 200 OK\r\n\r\nOK"
        cl.send(response)
        cl.close()
    except Exception as e:
        print("Chyba na serveru:", e)