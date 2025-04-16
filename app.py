from flask import Flask, request, render_template, jsonify, session, redirect, url_for

import os
import numpy as np
import pandas as pd
import joblib

from dotenv import load_dotenv
from helpers.getBikeData import getBikeData
from helpers.getWeatherData import getCurrentWeatherData
from helpers.accountApiFunction import accessData
from helpers.storeContactInfo import sentData
from datetime import datetime, timedelta

# Load csv file data into app

availability_data = pd.read_csv("data/availability.csv")
weather_data = pd.read_csv("data/weather_data.csv")
default_lags = pd.read_csv("data/default_lags.csv")
station_info = pd.read_csv("data/stations.csv")
restock_schedule = pd.read_csv("data/restock_schedule.csv")

# Load the model and pre-generated data
model = joblib.load("ml/bike_availability_xgb_model_with_weather.joblib")

load_dotenv(override=True) # Load environment variables from .env file

app = Flask(__name__)

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
    res = sentData(os.getenv('GOOGLE_APP_SCRIPT_URL') + 'form')
    if res.status_code == 200:
        return res
    
@app.route("/api/account", methods=["POST"])
def loginApi():
    res = accessData(os.getenv('GOOGLE_APP_SCRIPT_URL') + 'account')
    if res.status_code == 200:
        return res
    
# Define a route for predictions
@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get user input
        date = request.args.get("date")  # Format: YYYY-MM-DD
        time = request.args.get("time")  # Format: HH:MM:SS
        station_id = int(request.args.get("station_id"))  # User-provided station_id

        if not date or not time or not station_id:
            return jsonify({"error": "Missing date, time, or station_id parameter"}), 400

        # Parse date and time
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        hour = dt.hour

        # Get station info
        station_row = station_info[station_info["station_id"] == station_id]
        if station_row.empty:
            return jsonify({"error": f"Station id {station_id} not found in stations.csv"}), 404

        area_cluster = station_row["area_cluster"].iloc[0]
        capacity = station_row["capacity"].iloc[0]
        lat = float(station_row["lat"].iloc[0])
        lon = float(station_row["lon"].iloc[0])

        # Compute time features
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        is_weekend = dt.weekday() >= 5
        day_of_week = dt.weekday()
        is_peak_hour = hour in [7, 8, 17, 18]

         # Get lag_8h from default_lags.csv
        default_row = default_lags[
            (default_lags["station_id"] == station_id) &
            (default_lags["hour"] == hour)
        ]
        if not default_row.empty:
            lag_8h = default_row["lag_8h"].iloc[0]
        else:
            lag_8h = default_lags[
                default_lags["station_id"] == station_id
            ]["lag_8h"].mean()

        # Get is_restocked from restock_schedule.csv
        hour_window = [(hour-1)%24, hour, (hour+1)%24]
        matches = restock_schedule[
            (restock_schedule["station_id"] == station_id) &
            (restock_schedule["hour_window"].isin(hour_window)) &
            (restock_schedule["frequency"] >= 0.3)
        ]
        is_restocked = not matches.empty

           # Fetch weather data
        weather_data = getCurrentWeatherData(lat, lon).json()
        temp = float(weather_data["main"]["temp"])
        humidity = float(weather_data["main"]["humidity"])
        pressure = float(weather_data["main"]["pressure"])

        # Combine input features (same order as in training)
        input_features = [
            station_id,      # From station_info.csv
            area_cluster,    # From station_info.csv
            hour_sin,        # Calculated
            hour_cos,        # Calculated
            capacity,        # From station_info.csv
            int(is_weekend), # Calculated
            lag_8h,          # From default_lags.csv
            int(is_restocked), # From restock_schedule.csv
            day_of_week,     # Calculated
            int(is_peak_hour), # Calculated
            temp,            # float
            humidity,        # float
            pressure         # float
        ]
        input_array = np.array(input_features).reshape(1, -1)

        # Make prediction
        relative_pred = model.predict(input_array)[0]
        absolute_pred = int(np.floor(relative_pred * capacity))
        absolute_pred = max(absolute_pred, 0)

        return jsonify({"predicted_available_bikes": absolute_pred})

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