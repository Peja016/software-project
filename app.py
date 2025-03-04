from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import getBikesData

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/bikesInfo', methods=['POST'])
def getBikesInfo():
    res = getBikesData.getBikesData()
    if res.status_code == 200:
        return jsonify(res.json())

@app.route('/map')
def map():
    return render_template(
        "map.html",
        lat=os.getenv('LAT'),
        lon=os.getenv('LON'),
        api=os.getenv('GOOGLE_MAP_API'),
        bikes_api_url="/api/bikesInfo",
    )

@app.route('/how')
def how():
    return render_template("how.html")

@app.route('/use')
def use():
    return render_template("use.html")

if __name__ == "__main__":
    print('hi')
    app.config['ENV'] = 'development'
    app.run(debug=True)