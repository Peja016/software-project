import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from flask import Flask, request, jsonify
from datetime import datetime
import numpy as np
import pandas as pd
import joblib
import os
import requests

# Load the model and pre-generated data
try:
    model = joblib.load("bike_availability_xgb_model_with_weather.joblib")
    print("Model loaded successfully")
except Exception as e:
    print(f"Failed to load model: {e}")
    raise

try:
    station_info = pd.read_csv("station_info.csv", dtype={
        "station_id": int,
        "area_cluster": int,
        "capacity": int,
        "lat": float,
        "lon": float,
        "name": str
    })
    default_lags = pd.read_csv("default_lags.csv", dtype={
        "station_id": int,
        "hour": int,
        "lag_8h": float
    })
    restock_schedule = pd.read_csv("restock_schedule.csv", dtype={
        "station_id": int,
        "hour_window": int,
        "frequency": float
    })
    print("CSV files loaded successfully")
    print(f"station_info dtypes:\n{station_info.dtypes}")
    print(f"default_lags dtypes:\n{default_lags.dtypes}")
except Exception as e:
    print(f"Failed to load CSV files: {e}")
    raise

# OpenWeather API configuration
OPENWEATHER_API_KEY = "079a46f41479f3ae68020178377774ef"
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Function to fetch weather data
def fetch_openweather_data(lat, lon, dt):
    print(f"Fetching weather for lat={lat}, lon={lon}, time={dt}")
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
        weather_data = {
            "temp": float(data["main"]["temp"]),
            "humidity": float(data["main"]["humidity"]),
            "pressure": float(data["main"]["pressure"])
        }
        print(f"Weather data: {weather_data}")
        return weather_data
    except Exception as e:
        print(f"Failed to fetch weather data: {e}")
        default_weather = {
            "temp": 13.955,
            "humidity": 83.75,
            "pressure": 1002.41
        }
        print(f"Using default weather: {default_weather}")
        return default_weather

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def home():
    try:
        with open("index.html", encoding="utf-8") as f:
            print("Serving index.html")
            return f.read()
    except FileNotFoundError:
        print("index.html not found")
        return jsonify({"error": "index.html not found"}), 500

# Define prediction route
@app.route("/predict", methods=["GET"])
def predict():
    try:
        print("Received /predict request")
        # Get user input
        date = request.args.get("date")
        time = request.args.get("time")
        station_name = request.args.get("station_name")
        print(f"Input: date={date}, time={time}, station_name={station_name}")

        if not date or not time or not station_name:
            print("Missing parameters")
            return jsonify({"error": "Missing date, time, or station_name parameter"}), 400

        # Parse date and time
        try:
            dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
            print(f"Parsed datetime: {dt}")
        except ValueError as e:
            print(f"Date parsing error: {e}")
            return jsonify({"error": f"Invalid date or time format: {e}"}), 400

        year, month, day = dt.year, dt.month, dt.day
        hour = dt.hour

        # Get station info
        print(f"Querying station_info for station_name={station_name}")
        station_row = station_info[station_info["name"] == station_name]
        if station_row.empty:
            print(f"Station not found: {station_name}")
            return jsonify({"error": f"Station name {station_name} not found in station_info.csv"}), 404

        # Convert station info
        try:
            station_id = int(station_row["station_id"].iloc[0])
            area_cluster = int(station_row["area_cluster"].iloc[0])
            capacity = int(station_row["capacity"].iloc[0])
            lat = float(station_row["lat"].iloc[0])
            lon = float(station_row["lon"].iloc[0])
            print(f"Station info: id={station_id}, cluster={area_cluster}, capacity={capacity}, lat={lat}, lon={lon}")
        except (ValueError, TypeError) as e:
            print(f"Station info error: {e}")
            return jsonify({"error": f"Invalid station data: {e}"}), 500

        # Compute time features
        try:
            hour_sin = float(np.sin(2 * np.pi * hour / 24))
            hour_cos = float(np.cos(2 * np.pi * hour / 24))
            is_weekend = int(dt.weekday() >= 5)
            day_of_week = int(dt.weekday())
            is_peak_hour = int(hour in [7, 8, 17, 18])
            print(f"Time features: hour_sin={hour_sin}, hour_cos={hour_cos}, is_weekend={is_weekend}, day_of_week={day_of_week}, is_peak_hour={is_peak_hour}")
        except Exception as e:
            print(f"Time feature error: {e}")
            return jsonify({"error": f"Time feature error: {e}"}), 500

        # Get lag_8h
        print(f"Querying default_lags for station_id={station_id}, hour={hour}")
        default_row = default_lags[
            (default_lags["station_id"] == station_id) &
            (default_lags["hour"] == hour)
        ]
        try:
            if not default_row.empty:
                lag_8h = float(default_row["lag_8h"].iloc[0])
            else:
                lag_8h_mean = default_lags[
                    default_lags["station_id"] == station_id
                ]["lag_8h"].mean()
                if pd.isna(lag_8h_mean):
                    raise ValueError("No valid lag_8h data for station")
                lag_8h = float(lag_8h_mean)
            print(f"lag_8h: {lag_8h}")
        except (ValueError, TypeError) as e:
            print(f"lag_8h error: {e}")
            return jsonify({"error": f"Invalid lag_8h data: {e}"}), 500

        # Get is_restocked
        print(f"Querying restock_schedule for station_id={station_id}, hour={hour}")
        hour_window = [(hour-1)%24, hour, (hour+1)%24]
        matches = restock_schedule[
            (restock_schedule["station_id"] == station_id) &
            (restock_schedule["hour_window"].isin(hour_window)) &
            (restock_schedule["frequency"] >= 0.3)
        ]
        is_restocked = int(not matches.empty)
        print(f"is_restocked: {is_restocked}")

        # Fetch weather data
        weather_data = fetch_openweather_data(lat, lon, dt)
        try:
            temp = float(weather_data["temp"])
            humidity = float(weather_data["humidity"])
            pressure = float(weather_data["pressure"])
            print(f"Weather features: temp={temp}, humidity={humidity}, pressure={pressure}")
        except (ValueError, TypeError) as e:
            print(f"Weather data error: {e}")
            return jsonify({"error": f"Invalid weather data: {e}"}), 500

        # Combine input features
        input_features = [
            station_id, area_cluster, hour_sin, hour_cos,
            capacity, is_weekend, lag_8h, is_restocked,
            day_of_week, is_peak_hour, temp, humidity, pressure
        ]

        # Debug features
        print("Input features:", input_features)
        print("Feature types:", [type(x) for x in input_features])

        # Create input array
        try:
            # 确保 numpy 数组为纯 float
            input_array = np.array(input_features, dtype=np.float64).reshape(1, -1)
            print("Input array:", input_array)
            print("Input array dtype:", input_array.dtype)
        except Exception as e:
            print(f"Input array error: {e}")
            return jsonify({"error": f"Failed to create input array: {e}"}), 500

        # Make prediction
        try:
            relative_pred = model.predict(input_array)[0]
            absolute_pred = int(np.floor(relative_pred * capacity))
            absolute_pred = max(absolute_pred, 0)
            print(f"Prediction: relative={relative_pred}, absolute={absolute_pred}")
        except Exception as e:
            print(f"Prediction error: {e}")
            return jsonify({"error": f"Prediction failed: {e}"}), 500

        return jsonify({"predicted_available_bikes": absolute_pred})

    except Exception as e:
        print(f"Unexpected error in /predict: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/stations", methods=["GET"])
def get_stations():
    try:
        print("Received /stations request")
        stations = station_info[['station_id', 'name', 'capacity']].sort_values(by='name').drop_duplicates()
        if stations.empty:
            print("No stations found")
            return jsonify({"error": "No stations found in station_info.csv"}), 404
        station_list = [
            {
                "station_id": int(row["station_id"]),
                "name": str(row["name"]),
                "capacity": int(row["capacity"])
            }
            for _, row in stations.iterrows()
        ]
        print(f"Returning {len(station_list)} stations")
        return jsonify(station_list)
    except Exception as e:
        print(f"Error in /stations: {e}")
        return jsonify({"error": f"Failed to load stations: {str(e)}"}), 500

if __name__ == "__main__":
    print("Starting Flask app")
    app.run(debug=True, host="0.0.0.0", port=5000)