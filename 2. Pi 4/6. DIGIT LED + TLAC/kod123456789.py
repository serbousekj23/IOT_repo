from flask import Flask, jsonify, render_template_string
from gpiozero import LED, Button
app = Flask(__name__)
# Initialize GPIO using Broadcom (BCM) pin numbering
led = LED(17)
button = Button(27, pull_up=True, bounce_time=0.05)
# Toggle the LED in the background whenever the physical button is pressed
button.when_pressed = led.toggle
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Raspberry Pi LED Controller</title>
<style>
        body { font-family: system-ui, sans-serif; text-align: center; margin-top: 80px; background: #f4f4f9; }
        .card { background: white; padding: 40px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .status { font-size: 24px; margin: 20px 0; font-weight: bold; }
        .on { color: #2ecc71; }
        .off { color: #e74c3c; }
        button { font-size: 18px; padding: 14px 28px; cursor: pointer; border: none; border-radius: 8px; background: #007bff; color: white; }
        button:active { transform: scale(0.98); }
</style>
</head>
<body>
<div class="card">
<h1>Argon Pi LED Control</h1>
<div class="status">LED is: <span id="state" class="off">OFF</span></div>
<button onclick="toggleLed()">Toggle LED</button>
</div>
<script>
        async function toggleLed() {
            const res = await fetch('/api/toggle', { method: 'POST' });
            const data = await res.json();
            updateUI(data.is_on);
        }
        async function syncState() {
            const res = await fetch('/api/state');
            const data = await res.json();
            updateUI(data.is_on);
        }
        function updateUI(isOn) {
            const el = document.getElementById('state');
            el.textContent = isOn ? 'ON' : 'OFF';
            el.className = isOn ? 'on' : 'off';
        }
        // Poll every 500ms so physical button presses update the web page automatically
        setInterval(syncState, 500);
        syncState();
</script>
</body>
</html>
"""
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)
@app.route('/api/toggle', methods=['POST'])
def api_toggle():
    led.toggle()
    return jsonify({'is_on': led.is_lit})
@app.route('/api/state', methods=['GET'])
def api_state():
    return jsonify({'is_on': led.is_lit})
if __name__ == '__main__':
    # Bind strictly to 127.0.0.1 for localhost-only access
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)