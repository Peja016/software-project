from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from bikesData import getBikesData
from storeInfo import sentData
import requests

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/api/bikesInfo", methods=['POST'])
def getBikesInfo():
    res = getBikesData()
    if res.status_code == 200:
        return jsonify(res.json())
    
@app.route("/api/contact_form", methods=["POST"])
def sentInfo():
    res = sentData()
    if res.status_code == 200:
        return res

@app.route('/map')
def map():
    return render_template(
        "map.html",
        lat=os.getenv('LAT'),
        lon=os.getenv('LON'),
        api=os.getenv('GOOGLE_MAP_API'),
        bikes_api_url="/api/bikesInfo",
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

if __name__ == "__main__":
    app.config['ENV'] = 'development'
    app.run(debug=True)