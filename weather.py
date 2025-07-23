import requests
import sys

def get_weather_description(code):
    """
    Converts WMO weather code to a human-readable description.
    Codes from Open-Meteo documentation.
    """
    codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Drizzle: Light intensity",
        53: "Drizzle: Moderate intensity",
        55: "Drizzle: Dense intensity",
        56: "Freezing Drizzle: Light intensity",
        57: "Freezing Drizzle: Dense intensity",
        61: "Rain: Slight intensity",
        63: "Rain: Moderate intensity",
        65: "Rain: Heavy intensity",
        66: "Freezing Rain: Light intensity",
        67: "Freezing Rain: Heavy intensity",
        71: "Snow fall: Slight intensity",
        73: "Snow fall: Moderate intensity",
        75: "Snow fall: Heavy intensity",
        77: "Snow grains",
        80: "Rain showers: Slight",
        81: "Rain showers: Moderate",
        82: "Rain showers: Violent",
        85: "Snow showers: Slight",
        86: "Snow showers: Heavy",
        95: "Thunderstorm: Slight or moderate",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, "Unknown weather condition")

def get_location_coords(city):
    """
    Converts a city name to latitude and longitude using the Open-Meteo Geocoding API.
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
        return location['latitude'], location['longitude'], location.get('country', '')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location data: {e}")
        return None, None, None

def get_weather(city):
    """
    Fetches and displays weather data for a given city using the Open-Meteo API.
    """
    latitude, longitude, country = get_location_coords(city)

    if latitude is None or longitude is None:
        print(f"Error: Could not find location for '{city}'. Please check the spelling.")
        return

    # Base URL for the Open-Meteo API
    base_url = "https://api.open-meteo.com/v1/forecast"

    # Parameters for the API request
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
        'wind_speed_unit': 'ms'
    }

    try:
        # Make the GET request to the API
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        # Parse the JSON response
        weather_data = response.json()

        # --- Extract and display weather information ---
        current = weather_data.get('current', {})
        temperature = current.get('temperature_2m')
        humidity = current.get('relative_humidity_2m')
        wind_speed = current.get('wind_speed_10m')
        weather_code = current.get('weather_code')

        description = get_weather_description(weather_code)

        # --- Display the formatted weather information ---
        print("\n" + "="*40)
        print(f"Weather Forecast for {city.title()}, {country}")
        print("="*40)
        print(f"  Description: {description}")
        print(f"  Temperature: {temperature}°C")
        print(f"  Humidity:    {humidity}%")
        print(f"  Wind Speed:  {wind_speed} m/s")
        print("="*40 + "\n")

    except requests.exceptions.HTTPError as http_err:
        print(f"An HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"A connection error occurred: {conn_err}")
        print("Please check your internet connection.")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
    except (KeyError, TypeError):
        print("Error: Could not parse weather data. The API response format might have changed.")


if __name__ == "__main__":
    print("--- Simple Weather App (using Open-Meteo) ---")
    print("Enter 'quit' or 'exit' to stop the application.")

    while True:
        # Get city name from user input
        city_input = input("\nPlease enter a city name: ").strip()

        # Check if the user wants to quit
        if city_input.lower() in ['quit', 'exit']:
            print("Exiting the weather app. Goodbye!")
            break

        if not city_input:
            print("City name cannot be empty.")
            continue

        # Call the function to get and display weather
        get_weather(city_input)