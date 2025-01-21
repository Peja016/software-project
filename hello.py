from flask import Flask
import requests
from bs4 import BeautifulSoup
import scraping 

app = Flask(__name__)


@app.route('/')
def index():
    url = ''

    response = requests.get(url)

    # parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    formatted_html = soup.prettify()

    return scraping.formatted_html

@app.route('/blog')
def blog():
    return "Hello, it's blog!"

if __name__ == "__main__":
    app.run(debug=True)