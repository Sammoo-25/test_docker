from flask import Flask, jsonify, Response
import requests
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Summary

app = Flask(__name__)

# Constants
API_KEY = "a6311858fb35df63b55216bae4aa952a"
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
CITY = "London,UK"

# Prometheus Metrics
REQUEST_COUNTER = Counter('weather_app_requests_total', 'Total number of requests', ['endpoint'])
REQUEST_LATENCY = Summary('weather_app_request_latency_seconds', 'Request latency in seconds', ['endpoint'])

@app.route('/')
@REQUEST_LATENCY.labels(endpoint='/').time()
def home():
    REQUEST_COUNTER.labels(endpoint='/').inc()
    try:
        response = requests.get(WEATHER_API_URL, params={"q": CITY, "appid": API_KEY, "units": "metric"})
        response.raise_for_status()
        weather_data = response.json()
        weather_html = f"""
        <html>
        <head><title>Current Weather in London</title></head>
        <body>
            <h1>Current Weather in London</h1>
            <p>Temperature: {weather_data['main']['temp']}&#8451;</p>
            <p>Weather: {weather_data['weather'][0]['description'].capitalize()}</p>
        </body>
        </html>
        """
        return Response(weather_html, status=200, mimetype='text/html')
    except requests.exceptions.RequestException as e:
        error_html = f"""
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Unable to fetch weather data</h1>
            <p>Error: {str(e)}</p>
        </body>
        </html>
        """
        return Response(error_html, status=500, mimetype='text/html')

@app.route('/ping')
@REQUEST_LATENCY.labels(endpoint='/ping').time()
def ping():
    REQUEST_COUNTER.labels(endpoint='/ping').inc()
    return Response("<html><body><h1>PONG</h1></body></html>", status=200, mimetype='text/html')

@app.route('/health')
@REQUEST_LATENCY.labels(endpoint='/health').time()
def health():
    REQUEST_COUNTER.labels(endpoint='/health').inc()
    return jsonify(status="HEALTHY")

@app.route('/metrics')
def metrics():
    REQUEST_COUNTER.labels(endpoint='/metrics').inc()
    return Response(generate_latest(), status=200, mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
