from flask import Flask, render_template_string, request, jsonify
from gpiozero import RotaryEncoder, PWMLED
 
app = Flask(__name__)
 
# Piny podle tvého zadání (LED přesunuta na 17 kvůli konfliktu s DT)
# a = CLK, b = DT
encoder = RotaryEncoder(a=27, b=18, max_steps=100) 
led = PWMLED(17)
 
# Výchozí jas a synchronizace kroků
brightness = 0
encoder.steps = 0
 
def update_led_from_encoder():
    global brightness
    # Udržení hodnoty mezi 0 a 100
    brightness = max(0, min(100, encoder.steps))
    encoder.steps = brightness
    led.value = brightness / 100.0
 
# Callback při otočení enkóderem
encoder.when_rotated = update_led_from_encoder
 
html_page = """
<!DOCTYPE html>
<html>
<head>
<title>Ovládání LED</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; }
        input[type=range] { width: 80%; max-width: 400px; }
</style>
</head>
<body>
<h2>Jas LED: <span id="jas_text">0</span>%</h2>
<input type="range" min="0" max="100" value="0" id="slider" oninput="sendSlider(this.value)">
<script>
        const slider = document.getElementById('slider');
        const jasText = document.getElementById('jas_text');
        // Odeslání hodnoty ze slideru do Raspberry
        function sendSlider(val) {
            jasText.innerText = val;
            fetch('/set?val=' + val);
        }
 
        // Pravidelná kontrola (2x za vteřinu), jestli někdo neotočil fyzickým enkóderem
        setInterval(() => {
            fetch('/get')
                .then(r => r.json())
                .then(data => {
                    // Pokud uživatel zrovna netahá za slider, updatuj ho podle enkóderu
                    if(document.activeElement !== slider) {
                        slider.value = data.brightness;
                        jasText.innerText = data.brightness;
                    }
                });
        }, 500);
</script>
</body>
</html>
"""
 
@app.route('/')
def index():
    return render_template_string(html_page)
 
@app.route('/set')
def set_brightness():
    global brightness
    try:
        val = int(request.args.get('val', 0))
        brightness = max(0, min(100, val))
        encoder.steps = brightness  # Synchronizace enkóderu se sliderem
        led.value = brightness / 100.0
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))
 
@app.route('/get')
def get_brightness():
    return jsonify(brightness=brightness)
 
if __name__ == '__main__':
    # Běží na portu 8080 a naslouchá celé lokální síti
    app.run(host='0.0.0.0', port=8080)