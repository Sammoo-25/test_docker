import os
import psycopg2
from flask import Flask, jsonify, Response, request, render_template_string
import requests

app = Flask(__name__)

# Constants
API_KEY = "a6311858fb35df63b55216bae4aa952a"
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# Database connection settings from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:qwerty123@db:5432/weather_db")

# Database connection function
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Create table if not exists
def create_table():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS weather (
                    city_country TEXT PRIMARY KEY,
                    weather_info TEXT
                )
            ''')
            conn.commit()

create_table()

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

        # Save to database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO weather (city_country, weather_info) VALUES (%s, %s) ON CONFLICT (city_country) DO UPDATE SET weather_info = EXCLUDED.weather_info", (city, weather_info))
                conn.commit()

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
