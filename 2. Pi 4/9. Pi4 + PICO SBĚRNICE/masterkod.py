from flask import Flask, render_template_string, jsonify
from gpiozero import Button
import smbus2
 
app = Flask(__name__)
 
# I2C nastavení (adresa 0x41 musí sedět s kódem v Picu)
I2C_ADDR = 0x41
I2C_BUS = 1
 
try:
    bus = smbus2.SMBus(I2C_BUS)
except Exception as e:
    print("Chyba I2C:", e)
    bus = None
 
# Tlačítko na GPIO 17
button = Button(17)
led_state = 0
 
def update_pico(state):
    """Odešle bajt (0 nebo 1) do Pica přes I2C"""
    if bus:
        try:
            bus.write_byte(I2C_ADDR, state)
            print(f"Odesláno: {state}")
        except Exception as e:
            print("Chyba při odesílání I2C:", e)
 
def toggle_led():
    global led_state
    led_state = 1 if led_state == 0 else 0
    update_pico(led_state)
 
# Fyzické tlačítko spustí funkci toggle_led
button.when_pressed = toggle_led
 
html_page = """
<!DOCTYPE html>
<html>
<head>
<title>Ovládání z RPi 4</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; }
        button { padding: 20px 40px; font-size: 20px; cursor: pointer; border-radius: 10px; background-color: #007bff; color: white; border: none; }
        button:hover { background-color: #0056b3; }
</style>
</head>
<body>
<h2>I2C Ovladač Pica</h2>
<button onclick="toggle()">Přepnout LED</button>
<script>
        function toggle() {
            fetch('/toggle');
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
    # Při startu zkusíme poslat výchozí stav
    update_pico(led_state)
    app.run(host='0.0.0.0', port=8080)