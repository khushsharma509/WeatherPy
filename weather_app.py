import requests
import sys
import tkinter as tk
from tkinter import font

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
        95: "Thunderstorm: Slight or moderate",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, "Unknown")

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
    Returns None on failure.
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
        return None, f"Error fetching weather data: {e}"

# --- GUI Application ---

def fetch_and_display_weather():
    """
    Gets city from entry, fetches weather, and updates GUI labels.
    """
    city = city_entry.get()
    if not city:
        status_label.config(text="Please enter a city name.")
        return

    # Clear previous results and show loading status
    status_label.config(text=f"Searching for {city}...")
    location_label.config(text="")
    temp_label.config(text="")
    desc_label.config(text="")
    humidity_label.config(text="")
    wind_label.config(text="")
    
    # Run data fetching in a separate thread to not freeze the GUI
    app.update_idletasks()
    weather_info, error = get_weather(city)
    app.update_idletasks()

    if error:
        status_label.config(text=error)
        return

    # Update GUI with new weather data
    status_label.config(text="Weather information:")
    location_label.config(text=weather_info['city'])
    temp_label.config(text=f"🌡️ {weather_info['temperature']}")
    desc_label.config(text=f"☀️ {weather_info['description']}")
    humidity_label.config(text=f"💧 {weather_info['humidity']}")
    wind_label.config(text=f"💨 {weather_info['wind']}")


if __name__ == "__main__":
    # --- Window Setup ---
    app = tk.Tk()
    app.title("Weather App")
    app.geometry("400x450")
    app.configure(bg="#f0f0f0")

    # --- Font Definitions ---
    title_font = font.Font(family="Helvetica", size=18, weight="bold")
    label_font = font.Font(family="Helvetica", size=12)
    result_font = font.Font(family="Helvetica", size=14)
    temp_font = font.Font(family="Helvetica", size=28, weight="bold")

    # --- Main Frame ---
    main_frame = tk.Frame(app, bg="#f0f0f0", padx=20, pady=20)
    main_frame.pack(expand=True, fill="both")

    # --- Input Frame ---
    input_frame = tk.Frame(main_frame, bg="#f0f0f0")
    input_frame.pack(fill="x", pady=(0, 20))

    city_entry = tk.Entry(input_frame, font=label_font, relief="solid", borderwidth=1)
    city_entry.pack(side="left", expand=True, fill="x", ipady=5)
    city_entry.bind("<Return>", lambda event: fetch_and_display_weather())

    search_button = tk.Button(input_frame, text="Search", font=label_font, command=fetch_and_display_weather, relief="flat", bg="#007BFF", fg="white", padx=10)
    search_button.pack(side="right", padx=(10, 0))

    # --- Results Frame ---
    results_frame = tk.Frame(main_frame, bg="white", relief="solid", borderwidth=1)
    results_frame.pack(expand=True, fill="both")
    
    status_label = tk.Label(results_frame, text="Enter a city to begin", font=label_font, bg="white", fg="#555")
    status_label.pack(pady=10)

    location_label = tk.Label(results_frame, text="", font=title_font, bg="white", fg="#333")
    location_label.pack(pady=(5, 10))

    temp_label = tk.Label(results_frame, text="", font=temp_font, bg="white", fg="#007BFF")
    temp_label.pack(pady=5)

    desc_label = tk.Label(results_frame, text="", font=result_font, bg="white", fg="#333")
    desc_label.pack(pady=5)

    humidity_label = tk.Label(results_frame, text="", font=result_font, bg="white", fg="#333")
    humidity_label.pack(pady=5)

    wind_label = tk.Label(results_frame, text="", font=result_font, bg="white", fg="#333")
    wind_label.pack(pady=5)

    # --- Start the application ---
    app.mainloop()