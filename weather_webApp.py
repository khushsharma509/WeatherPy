import requests
from flask import Flask, request, jsonify, render_template_string

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Data Fetching and Processing Logic (from previous version) ---

def get_weather_description(code):
    """
    Converts WMO weather code to a human-readable description.
    """
    codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Drizzle: Light", 53: "Drizzle: Moderate", 55: "Drizzle: Dense",
        56: "Freezing Drizzle: Light", 57: "Freezing Drizzle: Dense",
        61: "Rain: Slight", 63: "Rain: Moderate", 65: "Rain: Heavy",
        66: "Freezing Rain: Light", 67: "Freezing Rain: Heavy",
        71: "Snow fall: Slight", 73: "Snow fall: Moderate", 75: "Snow fall: Heavy",
        77: "Snow grains",
        80: "Rain showers: Slight", 81: "Rain showers: Moderate", 82: "Rain showers: Violent",
        85: "Snow showers: Slight", 86: "Snow showers: Heavy",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, "Unknown condition")

def get_location_coords(city):
    """
    Converts a city name to latitude and longitude. Returns (lat, lon, full_name) or (None, None, None).
    """
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {'name': city, 'count': 1, 'language': 'en', 'format': 'json'}
    try:
        response = requests.get(geocoding_url, params=params)
        response.raise_for_status()
        results = response.json().get('results')
        if not results:
            return None, None, None
        location = results[0]
        country = location.get('country', '')
        admin1 = location.get('admin1', '')
        full_name = f"{location.get('name', city.title())}, {admin1}, {country}".strip(", ")
        return location['latitude'], location['longitude'], full_name
    except requests.exceptions.RequestException:
        return None, None, None

def get_weather(city):
    """
    Fetches weather data and returns it as a dictionary.
    Returns (data, None) on success, (None, error_message) on failure.
    """
    latitude, longitude, full_name = get_location_coords(city)
    if latitude is None:
        return None, f"Could not find location for '{city}'"

    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
        'wind_speed_unit': 'ms'
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        current = weather_data.get('current', {})
        
        result = {
            "city": full_name,
            "description": get_weather_description(current.get('weather_code')),
            "temperature": f"{current.get('temperature_2m')}°C",
            "humidity": f"{current.get('relative_humidity_2m')}%",
            "wind": f"{current.get('wind_speed_10m')} m/s"
        }
        return result, None
    except (requests.exceptions.RequestException, KeyError) as e:
        return None, f"Error fetching weather data."

# --- HTML, CSS, and JavaScript for the Frontend ---
# This is all embedded in a single string to keep it in one file.

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WeatherPy Web</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        :root {
            --bg-color: #1a202c;
            --card-color: #2d3748;
            --text-color: #e2e8f0;
            --primary-color: #4299e1;
            --border-color: #4a5568;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .weather-card {
            background: var(--card-color);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 450px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .weather-card h1 {
            font-size: 2rem;
            margin-bottom: 20px;
            font-weight: 600;
        }

        .search-form {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }

        .search-form input {
            flex-grow: 1;
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            background: #1a202c;
            color: var(--text-color);
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s ease;
        }

        .search-form input:focus {
            border-color: var(--primary-color);
        }

        .search-form button {
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            background: var(--primary-color);
            color: white;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .search-form button:hover {
            background: #3182ce;
        }

        .results-container {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
            height: 0;
            overflow: hidden;
        }
        
        .results-container.visible {
            opacity: 1;
            transform: translateY(0);
            height: auto;
        }

        #status {
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: #a0aec0;
        }
        
        #location {
            font-size: 1.5rem;
            font-weight: 500;
            margin-bottom: 10px;
        }
        
        #temperature {
            font-size: 4rem;
            font-weight: 700;
            margin: 10px 0;
        }
        
        #description {
            font-size: 1.2rem;
            font-weight: 400;
            text-transform: capitalize;
            margin-bottom: 20px;
        }
        
        .details {
            display: flex;
            justify-content: space-around;
            text-align: center;
            margin-top: 20px;
        }
        
        .detail-item p:first-child {
            font-size: 0.9rem;
            color: #a0aec0;
        }
        
        .detail-item p:last-child {
            font-size: 1.1rem;
            font-weight: 500;
        }

    </style>
</head>
<body>
    <div class="weather-card">
        <h1>WeatherPy</h1>
        <form id="weather-form" class="search-form">
            <input type="text" id="city-input" placeholder="Enter a city name..." required>
            <button type="submit">Search</button>
        </form>
        
        <div id="status">Enter a city to get the weather forecast.</div>
        
        <div id="results" class="results-container">
            <p id="location"></p>
            <p id="temperature"></p>
            <p id="description"></p>
            <div class="details">
                <div class="detail-item">
                    <p>Humidity</p>
                    <p id="humidity"></p>
                </div>
                <div class="detail-item">
                    <p>Wind Speed</p>
                    <p id="wind"></p>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('weather-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const city = document.getElementById('city-input').value;
            const statusEl = document.getElementById('status');
            const resultsEl = document.getElementById('results');

            // Reset UI
            statusEl.textContent = `Searching for ${city}...`;
            resultsEl.classList.remove('visible');

            try {
                const response = await fetch(`/weather?city=${encodeURIComponent(city)}`);
                const data = await response.json();

                if (data.error) {
                    throw new Error(data.error);
                }

                // Update UI with data
                statusEl.textContent = '';
                document.getElementById('location').textContent = data.city;
                document.getElementById('temperature').textContent = data.temperature;
                document.getElementById('description').textContent = data.description;
                document.getElementById('humidity').textContent = data.humidity;
                document.getElementById('wind').textContent = data.wind;
                
                resultsEl.classList.add('visible');

            } catch (error) {
                statusEl.textContent = `Error: ${error.message}`;
            }
        });
    </script>
</body>
</html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/weather')
def weather_endpoint():
    """API endpoint to get weather data."""
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City parameter is required"}), 400
    
    weather_data, error = get_weather(city)
    
    if error:
        return jsonify({"error": error}), 404
        
    return jsonify(weather_data)


# --- Main Execution ---

if __name__ == "__main__":
    print("Starting Flask server...")
    print("Open your web browser and go to http://127.0.0.1:5000")
    app.run(debug=True)
    