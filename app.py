from flask import Flask, request, render_template, jsonify, session, redirect, url_for

import os
import numpy as np
import pandas as pd
import pickle

from dotenv import load_dotenv
from getBikeData import getBikeData
from getWeatherData import getCurrentWeatherData
from storeContactInfo import sentData
from accountApiFunction import accessData
from datetime import datetime, timedelta

# Load csv file data into app

availability_data = pd.read_csv("data/availability.csv")
weather_data = pd.read_csv("data/weather_data.csv")

model_filename = "bike_availability_rf_model_with_new_features.pkl"

with open(model_filename, "rb") as file:
    model = pickle.load(file)

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
    
@app.route("/api/weather", methods=['POST'])
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
@app.route("/api/predict", methods=["GET"])
def predict():
    try:
        # Get date and time from request
        date = request.args.get("date")
        time = request.args.get("time")
        station_id = request.args.get("station_id")  #station_id as an input parameter
        
        if not date or not time or not station_id:
            return jsonify({"error": "Missing date, time, or station_id parameter"}), 400

        # Combine date and time into a single datetime object
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        day_of_week = dt.weekday()

        # Combine data into input features
        input_features = [
            station_id,
            
            hour,
            day_of_week,
        ]
        input_array = np.array(input_features).reshape(1, -1)

        # Make a prediction
        prediction = model.predict(input_array)
        
        return jsonify({"predicted_available_bikes": prediction[0]})

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
    app.config['ENV'] = 'development'
    app.run(debug=True)