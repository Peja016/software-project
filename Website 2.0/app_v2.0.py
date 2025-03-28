from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from bikesData import getBikesData
from storeInfo import sentData
import requests

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

# HOME Index page (1)
@app.route('/')
def index():
    return render_template('index.html')

# FUNCTIONALITY...?
@app.route("/api/bikesInfo", methods=['POST'])
def getBikesInfo():
    res = getBikesData()
    if res.status_code == 200:
        return jsonify(res.json())
    
# FUNCTIONALITY...?
@app.route("/api/contact_form", methods=["POST"])
def sentInfo():
    res = sentData()
    if res.status_code == 200:
        return res

# Map page - CHANGE (2)
@app.route('/map')
def map():
    return render_template(
        "map.html",
        lat=os.getenv('LAT'),
        lon=os.getenv('LON'),
        api=os.getenv('GOOGLE_MAP_API'),
        bikes_api_url="/api/bikesInfo",
    )

# How to Use page (3)
@app.route('/how')
def how():
    return render_template("how.html")

# About page (4)
@app.route('/about')
def about():
    return render_template("about.html")

# FAQ page (5)
@app.route('/faq')
def faq():
    return render_template("faq.html")

# Contact page (6)
@app.route('/contact')
def contact():
    return render_template("contact.html")

# Pay page (7)
@app.route('/pay')
def pay():
    return render_template("pay.html")

# Safety page (8)
@app.route('/safety')
def safety():
    return render_template("safety.html")

if __name__ == "__main__":
    app.config['ENV'] = 'development'
    app.run(debug=True)