from flask import Flask, render_template_string, jsonify
import smbus2

try:
    from gpiozero import Button
    button = Button(17)
except Exception as e:
    print("gpiozero nedostupné nebo chyba GPIO:", e)
    button = None

app = Flask(__name__)

# I2C nastavení (adresa 0x41 musí sedět s kódem v Picu)
I2C_ADDR = 0x41
I2C_BUS = 1

try:
    bus = smbus2.SMBus(I2C_BUS)
except Exception as e:
    print("Chyba I2C:", e)
    bus = None

led_state = 0

def update_pico(state):
    """Odešle bajt (0 nebo 1) do Pica přes I2C"""
    if bus:
        try:
            bus.write_byte(I2C_ADDR, state)
            print(f"I2C odesláno: {state}")
        except Exception as e:
            print("Chyba při odesílání I2C:", e)

def toggle_led():
    global led_state
    led_state = 1 if led_state == 0 else 0
    update_pico(led_state)

# Fyzické tlačítko spustí funkci toggle_led
if button:
    button.when_pressed = toggle_led

html_page = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>RPi 4 -> Pico I2C Ovladač</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: system-ui, sans-serif; text-align: center; margin-top: 60px; background-color: #f4f4f9; }
        .card { background: white; padding: 40px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 420px; width: 90%; }
        .status-box { font-size: 22px; margin: 25px 0; font-weight: bold; }
        .on { color: #2ecc71; }
        .off { color: #e74c3c; }
        button { padding: 16px 36px; font-size: 18px; cursor: pointer; border-radius: 10px; background-color: #007bff; color: white; border: none; font-weight: bold; transition: background 0.2s; }
        button:hover { background-color: #0056b3; }
        button:active { transform: scale(0.98); }
        .note { margin-top: 20px; font-size: 14px; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="card">
        <h2>I2C Ovladač Pico</h2>
        <div class="status-box">
            Stav LED na Picu:<br>
            <span id="led-state" class="off">VYPNUTO (OFF)</span>
        </div>
        <button onclick="toggle()">Přepnout stav LED</button>
        <p class="note">Ovládání funguje z webu i fyzickým tlačítkem na GPIO 17 (stav se obousměrně synchronizuje).</p>
    </div>
    
    <script>
        function updateUI(state) {
            const el = document.getElementById('led-state');
            if (state === 1) {
                el.innerText = "ZAPNUTO (ON)";
                el.className = "on";
            } else {
                el.innerText = "VYPNUTO (OFF)";
                el.className = "off";
            }
        }

        async function toggle() {
            const res = await fetch('/toggle');
            const data = await res.json();
            updateUI(data.state);
        }

        async function syncState() {
            try {
                const res = await fetch('/state');
                const data = await res.json();
                updateUI(data.state);
            } catch (err) {
                console.error("Chyba synchronizace:", err);
            }
        }

        // Pravidelná synchronizace každých 500ms pro zachycení stisku fyzického tlačítka
        setInterval(syncState, 500);
        syncState();
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

@app.route('/state')
def get_state():
    return jsonify(state=led_state)

if __name__ == '__main__':
    # Při startu zkusíme poslat výchozí stav
    update_pico(led_state)
    app.run(host='0.0.0.0', port=8080)