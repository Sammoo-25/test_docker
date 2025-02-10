import os
from flask import Flask, jsonify, Response, request, render_template_string
import requests

app = Flask(__name__)

# Constants
API_KEY = "a6311858fb35df63b55216bae4aa952a"
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

@app.route('/', methods=['GET', 'POST'])
def home():
    city = "London,UK"
    if request.method == 'POST':
        city = request.form.get("city")

    try:
        response = requests.get(WEATHER_API_URL, params={"q": city, "appid": API_KEY, "units": "metric"})
        response.raise_for_status()
        weather_data = response.json()
        weather_info = f"Temperature: {weather_data['main']['temp']}°C, Weather: {weather_data['weather'][0]['description'].capitalize()}"

        return render_template_string('''
        <html>
        <head><title>Weather Info</title></head>
        <body>
            <form method="post">
                <input type="text" name="city" placeholder="Enter City,Country" required>
                <button type="submit">Get Weather</button>
            </form>
            <h1>Current Weather in {{ city }}</h1>
            <p>{{ weather_info }}</p>
        </body>
        </html>
        ''', city=city, weather_info=weather_info)
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {str(e)}", 500

@app.route('/ping')
def ping():
    return Response("<html><body><h1>PONG</h1></body></html>", status=200, mimetype='text/html')

@app.route('/health')
def health():
    return jsonify(status="HEALTHY")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)