from flask import Flask, render_template_string, jsonify
import requests

try:
    from gpiozero import Button
    button = Button(17)
except Exception as e:
    print("gpiozero nedostupné nebo chyba GPIO:", e)
    button = None

app = Flask(__name__)

# Výchozí IP adresa Pica, když vysílá vlastní síť
PICO_IP = "192.168.4.1" 

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

if button:
    button.when_pressed = toggle_led

html_page = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Pico AP Ovladač</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: system-ui, sans-serif; text-align: center; margin-top: 60px; background-color: #222; color: white; }
        .card { background: #2f3542; padding: 40px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 12px rgba(0,0,0,0.4); max-width: 420px; width: 90%; }
        button { padding: 18px 36px; font-size: 18px; cursor: pointer; border-radius: 10px; background-color: #ff4757; color: white; border: none; font-weight: bold; transition: background 0.2s; }
        button:hover { background-color: #ff6b81; }
        button:active { transform: scale(0.98); }
        #status { margin-top: 25px; font-size: 22px; font-weight: bold; color: #ced6e0; }
        .note { margin-top: 20px; font-size: 14px; color: #a4b0be; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Přímé Wi-Fi spojení s Picem</h2>
        <button onclick="toggle()">Přepnout stav LED</button>
        <p id="status">Načítám stav...</p>
        <p class="note">Ovládání funguje z webu i fyzickým tlačítkem na GPIO 17 (live synchronizace každých 500 ms).</p>
    </div>
    
    <script>
        function updateUI(state) {
            const statusText = document.getElementById('status');
            statusText.innerText = "Stav LED: " + (state === 1 ? "ZAPNUTA (ON)" : "VYPNUTA (OFF)");
            statusText.style.color = (state === 1) ? "#2ed573" : "#ff4757";
        }

        async function toggle() {
            try {
                const res = await fetch('/toggle');
                const data = await res.json();
                if (data.success) {
                    updateUI(data.state);
                }
            } catch (err) {
                const statusText = document.getElementById('status');
                statusText.innerText = "Chyba spojení!";
                statusText.style.color = "#ffa502";
            }
        }

        async function syncState() {
            try {
                const res = await fetch('/state');
                const data = await res.json();
                updateUI(data.state);
            } catch (err) {
                console.error("Chyba načtení stavu:", err);
            }
        }

        // Pravidelná synchronizace – fyzický stisk tlačítka se ihned projeví na webu!
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
    update_pico(led_state)
    # Běží na 0.0.0.0, dostupné v síti vytvořené Picem (např. 192.168.4.2:8080)
    app.run(host='0.0.0.0', port=8080)