from flask import Flask, render_template_string, request, jsonify
from RPLCD.i2c import CharLCD
 
app = Flask(__name__)
 
# --- INICIALIZACE DISPLEJE ---
# Adresa je většinou 0x27 (případně 0x3F)
try:
    lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
    lcd.clear()
    lcd.write_string('Cekam na zpravu!')
except Exception as e:
    print("Chyba při startu LCD:", e)
    lcd = None
 
# --- WEB UI ---
html_page = """
<!DOCTYPE html>
<html>
<head>
<title>LCD Nástěnka</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }
        .container { max-width: 400px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input[type=text] { padding: 10px; width: 80%; font-size: 16px; margin-bottom: 20px; text-align: center; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; background-color: #28a745; color: white; border: none; border-radius: 5px; }
        button:hover { background-color: #218838; }
        #status { margin-top: 15px; font-weight: bold; }
</style>
</head>
<body>
<div class="container">
<h2>Pošli vzkaz na LCD</h2>
<input type="text" id="lcd_input" placeholder="Zadej text (max 16 znaků)" maxlength="16">
<br>
<button onclick="sendText()">Vypsat na displej</button>
<p id="status"></p>
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
                    setTimeout(() => status.innerText = "", 2000);
                } else {
                    status.style.color = "red";
                    status.innerText = "Chyba: " + data.error;
                }
            });
        }
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
    text = request.form.get('text', '')
    if lcd:
        try:
            lcd.clear()
            # Vypíše text na první řádek (limitováno na 16 znaků)
            lcd.write_string(text[:16]) 
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, error=str(e))
    else:
        return jsonify(success=False, error="Displej nenalezen. Zkontroluj I2C adresu a zapojení.")
 
if __name__ == '__main__':
    # Běží na portu 8080 pro celou lokální síť
    app.run(host='0.0.0.0', port=8080)