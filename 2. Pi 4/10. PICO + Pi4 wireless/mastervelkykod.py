from flask import Flask, render_template_string, jsonify
from gpiozero import Button
import requests
 
app = Flask(__name__)
 
# Výchozí IP adresa Pica, když vysílá vlastní síť
PICO_IP = "192.168.4.1"
 
button = Button(17)
led_state = 0
 
def update_pico(state):
    try:
        command = "on" if state == 1 else "off"
        requests.get(f"http://{PICO_IP}/{command}", timeout=1.5)
        print(f"Odesláno na Pico: {command}")
    except requests.exceptions.RequestException as e:
        print("Chyba při komunikaci s Picem:", e)
 
def toggle_led():
    global led_state
    led_state = 1 if led_state == 0 else 0
    update_pico(led_state)
 
button.when_pressed = toggle_led
 
html_page = """
<!DOCTYPE html>
<html>
<head>
<title>Pico AP Ovladač</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #222; color: white; }
        button { padding: 20px 40px; font-size: 20px; cursor: pointer; border-radius: 10px; background-color: #ff4757; color: white; border: none; font-weight: bold; }
        button:hover { background-color: #ff6b81; }
        #status { margin-top: 20px; font-weight: bold; color: #aaa; }
</style>
</head>
<body>
<h2>Přímé spojení s Picem</h2>
<button onclick="toggle()">Přepnout LED</button>
<p id="status"></p>
<script>
        function toggle() {
            const statusText = document.getElementById('status');
            statusText.innerText = "Odesílám...";
            fetch('/toggle')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        statusText.innerText = "LED " + (data.state ? "ZAPNUTA" : "VYPNUTA");
                        statusText.style.color = "#2ed573";
                    }
                })
                .catch(err => {
                    statusText.innerText = "Chyba spojení!";
                    statusText.style.color = "#ff4757";
                });
        }
</script>
</body>
</html>
"""
 
@app.route('/')
def index():
    return render_template_string(html_page)
 
@app.route('/toggle')
def web_toggle():
    toggle_led()
    return jsonify(success=True, state=led_state)
 
if __name__ == '__main__':
    update_pico(led_state)
    # Zde běžíme na 0.0.0.0, takže webovka bude dostupná na IP adrese
    # kterou dostala velká malina od Pica (např. 192.168.4.2:8080)
    app.run(host='0.0.0.0', port=8080)