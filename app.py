from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup

import getBikesData

app = Flask(__name__)


@app.route('/')
def index():
    # url = 'https://ooopenlab.cc/en'

    # response = requests.get(url)

    # parse HTML
    # soup = BeautifulSoup(response.text, 'html.parser')

    # formatted_html = soup.prettify()
    # print(formatted_html)

    return render_template('index.html')

@app.route('/api/bikesInfo')
def getBikesInfo():
    res = getBikesData.getBikesData()
    if res.status_code == 200:
        return res.json()
    else:
        return print('Cannot get data')

@app.route('/blog')
def blog():
    return "Hello, it's blog!"

if __name__ == "__main__":
    app.run(debug=True)