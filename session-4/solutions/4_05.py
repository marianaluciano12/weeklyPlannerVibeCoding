# 5. Wave Height Website

# 🔎  Make a website showing the wave height in Nazare:
#     1. Gets the wave height in Nazare
#     2. Creates a website showing the wave height

import requests
from flask import Flask, render_template_string

app = Flask(__name__)

def get_nazare_wave_height():
    url = "https://marine-api.open-meteo.com/v1/marine"
    params = {
        "latitude": 39.6011,
        "longitude": -9.0731,
        "current": "wave_height",
        "timezone": "Europe/Lisbon"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data["current"]["wave_height"], data["current"]["time"]
    except Exception as e:
        return None, str(e)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nazaré Wave Height Tracker</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            max-width: 500px;
        }
        h1 { font-size: 2.5rem; margin-bottom: 0.2rem; }
        p { color: #b8c6db; margin-bottom: 2rem; }
        .wave-height {
            font-size: 5.5rem;
            font-weight: bold;
            color: #00d2ff;
            margin: 2rem 0 0;
        }
        .unit { font-size: 1.5rem; color: #3a7bd5; vertical-align: super; }
        .time { color: #9ab4c7; font-size: 0.9rem; margin-top: 1rem; }
        .refresh-btn {
            margin-top: 1.5rem;
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: bold;
            color: white;
            background: linear-gradient(to right, #3a7bd5, #3a6073);
            border: none;
            border-radius: 30px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 Nazaré Waves</h1>
        <p>Live data from Praia do Norte, Portugal</p>
        {% if wave_height %}
            <div class="wave-height">{{ wave_height }}<span class="unit">m</span></div>
            <div class="time">Last updated: {{ time }} (Lisbon Time)</div>
        {% else %}
            <div class="wave-height" style="font-size: 3rem; color: #ff6b6b;">Error</div>
            <div class="time">Could not fetch data: {{ time }}</div>
        {% endif %}
        <button class="refresh-btn" onclick="window.location.reload();">Refresh Data</button>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    wave_height, time_str = get_nazare_wave_height()
    return render_template_string(HTML_TEMPLATE, wave_height=wave_height, time=time_str)

if __name__ == "__main__":
    print("Click this link to view your website: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server.")
    app.run(host="127.0.0.1", port=5000)
