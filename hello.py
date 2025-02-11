from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import scrapBikesData 

app = Flask(__name__)


@app.route('/')
def index():
    url = 'https://ooopenlab.cc/en'

    response = requests.get(url)

    # parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    formatted_html = soup.prettify()
    # print(formatted_html)

    return render_template('home.html')

@app.route('/blog')
def blog():
    return "Hello, it's blog!"

if __name__ == "__main__":
    app.run(debug=True)