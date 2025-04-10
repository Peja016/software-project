import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from flask import Flask, request, jsonify
from datetime import datetime
import numpy as np
import pandas as pd
import joblib
import requests
import os
from sklearn.preprocessing import LabelEncoder
import holidays  # Import holidays package

# Load the model and pre-generated data
model = joblib.load("bike_availability_rf_model_with_new_features.joblib")
weather_encoder = joblib.load("weather_label_encoder.joblib")
default_lags = pd.read_csv("default_lags.csv")
station_info = pd.read_csv("station_info.csv")

# Initialize Ireland holidays
ie_holidays = holidays.Ireland()

# OpenWeather API configuration
OPENWEATHER_API_KEY = "079a46f41479f3ae68020178377774ef"
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Function to fetch weather data
def fetch_openweather_forecast(lat, lon, date):
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(OPENWEATHER_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "temp_max": data["main"]["temp_max"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "clouds_all": data["clouds"]["all"],
            "weather_main": data["weather"][0]["main"]
        }
    except Exception as e:
        print(f"Failed to fetch weather data: {e}")
        return {
            "temp_max": 20.0,
            "humidity": 60.0,
            "wind_speed": 3.0,
            "pressure": 1013.0,
            "clouds_all": 50.0,
            "weather_main": "Clouds"
        }

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def home():
    with open("index.html", encoding="utf-8") as f:
        return f.read()

# Define prediction route
@app.route("/predict", methods=["GET"])
def predict():
    try:
        # Get user input
        date = request.args.get("date")  # Format: YYYY-MM-DD
        time = request.args.get("time")  # Format: HH:MM:SS
        station_id = request.args.get("station_id")  # User-provided station_id

        if not date or not time or not station_id:
            return jsonify({"error": "Missing date, time, or station_id parameter"}), 400

        # Convert station_id to integer
        station_id = int(station_id)

        # Combine date and time into datetime object
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        is_weekend = dt.weekday() >= 5  # Saturday or Sunday is True

        # Automatically determine if the date is a public holiday in Ireland
        is_holiday = dt.date() in ie_holidays  # Check if date is in Ireland's holiday list

        # Compute time features
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)

        # Get area_cluster and capacity from station_info.csv
        station_row = station_info[station_info["station_id"] == station_id]
        if station_row.empty:
            return jsonify({"error": f"Station ID {station_id} not found in station_info.csv"}), 404

        area_cluster = station_row["area_cluster"].values[0]
        capacity = station_row["capacity"].values[0]
        lat = station_row["lat"].values[0]
        lon = station_row["lon"].values[0]

        # Get weather data from OpenWeather
        weather_data = fetch_openweather_forecast(lat, lon, date)
        temp_max = weather_data["temp_max"]
        humidity = weather_data["humidity"]
        wind_speed = weather_data["wind_speed"]
        pressure = weather_data["pressure"]
        clouds_all = weather_data["clouds_all"]
        weather_main = weather_data["weather_main"]

        # Encode weather_main
        weather_main_encoded = weather_encoder.transform([weather_main])[0]

        # Get lag_1h and lag_24h from default_lags.csv
        default_row = default_lags[(default_lags["station_id"] == station_id) &
                                   (default_lags["hour"] == hour)]
        if not default_row.empty:
            lag_1h = default_row["lag_1h"].values[0]
            lag_24h = default_row["lag_24h"].values[0]
        else:
            lag_1h = default_lags["lag_1h"].mean()
            lag_24h = default_lags["lag_24h"].mean()

        # Combine input features (same order as in training)
        input_features = [
            station_id,          # User input
            area_cluster,        # Retrieved from station_info.csv
            hour_sin,            # Automatically calculated
            hour_cos,            # Automatically calculated
            temp_max,            # Retrieved from OpenWeather
            humidity,            # Retrieved from OpenWeather
            capacity,            # Retrieved from station_info.csv
            int(is_weekend),     # Automatically calculated (0 or 1)
            lag_1h,              # Retrieved from default_lags.csv
            lag_24h,             # Retrieved from default_lags.csv
            wind_speed,          # Retrieved from OpenWeather
            pressure,            # Retrieved from OpenWeather
            clouds_all,          # Retrieved from OpenWeather
            int(is_holiday),     # Automatically determined (0 or 1)
            weather_main_encoded # Encoded from OpenWeather
        ]
        input_array = np.array(input_features).reshape(1, -1)

        # Make prediction
        prediction = model.predict(input_array)
        prediction_int = int(np.floor(prediction[0]))
        prediction_int = max(prediction_int, 0)

        return jsonify({"predicted_available_bikes": prediction_int})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stations", methods=["GET"])
def get_stations():
    try:
        # Sort by name alphabetically and remove duplicates
        stations = station_info[['station_id', 'name', 'capacity']].sort_values(by='name').drop_duplicates()
        station_list = [
            {
                "station_id": row["station_id"],
                "name": row["name"],
                "capacity": row["capacity"]
            }
            for _, row in stations.iterrows()
        ]
        return jsonify(station_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)