from flask import Flask, render_template_string, request, jsonify
from RPLCD.i2c import CharLCD
import datetime
import socket

# Pokus o import tlačítka z gpiozero (pro fyzický vstup)
try:
    from gpiozero import Button
    btn = Button(17, bounce_time=0.05)
except Exception as e:
    print("gpiozero nedostupné nebo chyba GPIO:", e)
    btn = None

app = Flask(__name__)

current_message = "Cekam na zpravu!"
display_mode = "msg"  # 'msg' nebo 'info'
btn_press_count = 0

# --- INICIALIZACE DISPLEJE ---
try:
    lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
    lcd.clear()
    lcd.write_string(current_message[:16])
except Exception as e:
    print("Chyba při startu LCD:", e)
    lcd = None

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def write_to_lcd(line1, line2=""):
    if lcd:
        try:
            lcd.clear()
            lcd.cursor_pos = (0, 0)
            lcd.write_string(line1[:16])
            if line2:
                lcd.cursor_pos = (1, 0)
                lcd.write_string(line2[:16])
        except Exception as e:
            print("Chyba zápisu na LCD:", e)

def on_physical_button():
    global display_mode, btn_press_count
    btn_press_count += 1
    # Přepínání mezi vzkazem a systémovými informacemi
    if display_mode == "msg":
        display_mode = "info"
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        ip = get_ip()
        write_to_lcd(f"IP:{ip}", f"Cas:{now_str} #{btn_press_count}")
    else:
        display_mode = "msg"
        write_to_lcd(current_message[:16], f"Stisky: {btn_press_count}")

if btn:
    btn.when_pressed = on_physical_button

# --- WEB UI ---
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>LCD Nástěnka</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }
        .container { max-width: 450px; margin: auto; padding: 25px; background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input[type=text] { padding: 10px; width: 80%; font-size: 16px; margin-bottom: 15px; text-align: center; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; background-color: #28a745; color: white; border: none; border-radius: 5px; margin: 5px; }
        button:hover { background-color: #218838; }
        .info-btn { background-color: #007bff; }
        .info-btn:hover { background-color: #0056b3; }
        #status { margin-top: 15px; font-weight: bold; }
        .lcd-preview { background: #2f3542; color: #a4b0be; font-family: monospace; font-size: 18px; padding: 15px; border-radius: 6px; margin-top: 15px; text-align: left; }
    </style>
</head>
<body>
    <div class="container">
        <h2>I2C LCD Nástěnka</h2>
        <p>Vstup z webu nebo fyzického tlačítka (GPIO 17)</p>
        <input type="text" id="lcd_input" placeholder="Zadej text (max 16 znaků)" maxlength="16">
        <br>
        <button onclick="sendText()">Odeslat text na LCD</button>
        <button class="info-btn" onclick="toggleInfo()">Přepnout Info (Sys/Text)</button>
        <p id="status"></p>

        <div class="lcd-preview">
            <div>LCD Řádek 1: <span id="prev1" style="color: #7bed9f;">-</span></div>
            <div>LCD Řádek 2: <span id="prev2" style="color: #7bed9f;">-</span></div>
        </div>
    </div>
    
    <script>
        function sendText() {
            const text = document.getElementById('lcd_input').value;
            const status = document.getElementById('status');
            
            fetch('/lcd', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'text=' + encodeURIComponent(text)
            })
            .then(r => r.json())
            .then(data => {
                if(data.success) {
                    status.style.color = "green";
                    status.innerText = "Úspěšně odesláno!";
                    updateStatus();
                    setTimeout(() => status.innerText = "", 2000);
                } else {
                    status.style.color = "red";
                    status.innerText = "Chyba: " + data.error;
                }
            });
        }

        function toggleInfo() {
            fetch('/toggle_info', { method: 'POST' }).then(() => updateStatus());
        }

        function updateStatus() {
            fetch('/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('prev1').innerText = data.line1 || '';
                    document.getElementById('prev2').innerText = data.line2 || '';
                });
        }

        setInterval(updateStatus, 1000);
        updateStatus();
    </script>
</body>
</html>
"""

# --- ROUTY ---
@app.route('/')
def index():
    return render_template_string(html_page)

@app.route('/lcd', methods=['POST'])
def update_lcd():
    global current_message, display_mode
    text = request.form.get('text', '')
    current_message = text
    display_mode = "msg"
    write_to_lcd(current_message[:16], f"Stisky: {btn_press_count}")
    return jsonify(success=True)

@app.route('/toggle_info', methods=['POST'])
def web_toggle_info():
    on_physical_button()
    return jsonify(success=True)

@app.route('/status')
def get_lcd_status():
    if display_mode == "info":
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        ip = get_ip()
        return jsonify(line1=f"IP:{ip}", line2=f"Cas:{now_str} #{btn_press_count}")
    else:
        return jsonify(line1=current_message[:16], line2=f"Stisky: {btn_press_count}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)