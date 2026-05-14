# 5. Make a website showing the wave height in Nazare
""" 
    Make a program that:
        1. Gets the wave height in Nazare
        2. Creates a website showing the wave height
"""

import requests
from flask import Flask, render_template_string

app = Flask(__name__)

def get_nazare_wave_height():
    # URL for the Open-Meteo Marine API
    url = "https://marine-api.open-meteo.com/v1/marine"
    
    # Parameters for Nazaré, Portugal (Praia do Norte)
    params = {
        "latitude": 39.6011,
        "longitude": -9.0731,
        "current": "wave_height",
        "timezone": "Europe/Lisbon"
    }
    
    try:
        # 1. Gets the wave height in Nazare
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data["current"]["wave_height"], data["current"]["time"]
    except Exception as e:
        return None, str(e)

# 2. Creates a website showing the wave height
# A beautiful, modern HTML template with embedded CSS
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
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            max-width: 500px;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        p {
            color: #b8c6db;
            margin-bottom: 2rem;
        }
        .wave-container {
            margin: 2rem 0;
        }
        .wave-height {
            font-size: 5.5rem;
            font-weight: bold;
            color: #00d2ff;
            text-shadow: 0px 4px 10px rgba(0,210,255,0.4);
            margin: 0;
        }
        .unit {
            font-size: 1.5rem;
            color: #3a7bd5;
            vertical-align: super;
        }
        .time {
            color: #9ab4c7;
            font-size: 0.9rem;
            margin-top: 1rem;
        }
        .refresh-btn {
            margin-top: 1rem;
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: bold;
            color: white;
            background: linear-gradient(to right, #3a7bd5, #3a6073);
            border: none;
            border-radius: 30px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        .refresh-btn:active {
            transform: translateY(1px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 Nazaré Waves</h1>
        <p>Live data from Praia do Norte, Portugal</p>
        
        <div class="wave-container">
            {% if wave_height %}
                <div class="wave-height">{{ wave_height }}<span class="unit">m</span></div>
                <div class="time">Last updated: {{ time }} (Lisbon Time)</div>
            {% else %}
                <div class="wave-height" style="font-size: 3rem; color: #ff6b6b;">Error</div>
                <div class="time">Could not fetch data: {{ time }}</div>
            {% endif %}
        </div>
        
        <button class="refresh-btn" onclick="window.location.reload();">Refresh Data</button>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    # Fetch the wave height whenever someone loads the page
    wave_height, time_str = get_nazare_wave_height()
    # Render the HTML template with the dynamic data
    return render_template_string(HTML_TEMPLATE, wave_height=wave_height, time=time_str)

if __name__ == "__main__":
    print("="*50)
    print("🌊 Starting Nazaré Wave Tracker Website 🌊")
    print("="*50)
    print("Click this link to view your website: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server.")
    app.run(host="127.0.0.1", port=5000)
