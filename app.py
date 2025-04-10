from flask import Flask, request, render_template, jsonify, session, redirect, url_for

import os
import numpy as np
import pandas as pd
import joblib
import holidays  # Import holidays package
import math

from dotenv import load_dotenv
from getBikeData import getBikeData
from getWeatherData import getCurrentWeatherData
from storeContactInfo import sentData
from accountApiFunction import accessData
from datetime import datetime, timedelta

# Load csv file data into app

availability_data = pd.read_csv("data/availability.csv")
weather_data = pd.read_csv("data/weather_data.csv")
default_lags = pd.read_csv("data/default_lags.csv")
station_info = pd.read_csv("data/stations.csv")

# Load the model and pre-generated data
model = joblib.load("bike_availability_rf_model_with_new_features.joblib")
weather_encoder = joblib.load("weather_label_encoder.joblib")

# Initialize Ireland holidays
ie_holidays = holidays.Ireland()

load_dotenv(override=True) # Load environment variables from .env file

app = Flask(__name__)

print(os.getenv('GOOGLE_APP_SCRIPT_ACCOUNT_URL'))

app.secret_key = os.getenv('SECRET_KEY')

@app.context_processor
def globalData():
    return { 
        'name': session.get('name'), 
        'team': [
            { 'name': 'Tan', 'pic': 'tan.png', 'id': 24211515, 'email': "hsuan-yu.tan@ucdconnect.ie" }, 
            { 'name': 'Kexun', 'pic': 'kexun.jpeg', 'id': 24204204, 'email': "kexun.liu@ucdconnect.ie" },
            { 'name': 'Herman', 'pic': 'herman.JPG', 'id': 24103685, 'email': "herman.dolhyi@ucdconnect.ie" },
        ] 
    }

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/api/bikesInfo", methods=['POST'])
def getBikesInfo():
    res = getBikeData()
    if res.status_code == 200:
        return jsonify(res.json())
    
@app.route("/api/weather", methods=['POST', 'GET'])
def getCurrentWeatherInfo():
    res = getCurrentWeatherData()
    if res.status_code == 200:
        return jsonify(res.json())
    
@app.route("/api/stations/<int:id>", methods=['POST'])
def getStationData(id):
    filtered_data = availability_data[availability_data["number"] == id]
    data = filtered_data[['available_bikes', 'available_bike_stands', 'last_update']]
    data_for_chart = [['Time', 'Bikes', 'Stands']]
    for _, row in data.iterrows():
        time_str = pd.to_datetime(row['last_update']).strftime('%H:%M:%S')
        data_for_chart.append([
            time_str, row['available_bikes'], row['available_bike_stands']
        ])
    return jsonify(data_for_chart)

@app.route("/api/oneDayWeather", methods=['POST'])
def getOneDayWeatherData():
    data = []
    for _, row in weather_data.iterrows():
        formatted_time = (datetime.strptime(row['last_update'], '%Y-%m-%d %H:%M:%S') + timedelta(minutes=1)).strftime('%-H:%M') 
        data.append({
            'time': formatted_time,
            'temperature': round(row['temperature'], 1),
            'icon': row['icon']
        })
    return jsonify(data)
    
@app.route("/api/contact_form", methods=["POST"])
def sentInfo():
    res = sentData(os.getenv('GOOGLE_APP_SCRIPT_URL'))
    if res.status_code == 200:
        return res
    
@app.route("/api/account", methods=["POST"])
def loginApi():
    res = accessData(os.getenv('GOOGLE_APP_SCRIPT_ACCOUNT_URL'))
    if res.status_code == 200:
        return res
    
# Define a route for predictions
@app.route("/predict", methods=["POST"])
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
        res = getCurrentWeatherData(lat, lon)
        weather_data = res.json()
        temp_max = weather_data["main"]["temp_max"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
        pressure = weather_data["main"]["pressure"]
        clouds_all = weather_data["clouds"]["all"]
        weather_main = weather_data["weather"][0]["main"]

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
        prediction_int = max(math.floor(prediction[0]), 0)

        return jsonify({"predicted_available_bikes": prediction_int})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/map')
def map():
    return render_template(
        "map.html",
        lat=os.getenv('LAT'),
        lon=os.getenv('LON'),
        api=os.getenv('GOOGLE_MAP_API'),
    )

@app.route('/use')
def use():
    return render_template("use.html")

@app.route('/rent')
def rent():
    return render_template("rent.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/faq')
def faq():
    return render_template("faq.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)