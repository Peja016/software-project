from flask import Flask
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route('/')
def index():
    url = 'https://hehethebox.com'
    response = requests.get(url)

    # parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    formatted_html = soup.prettify()

    return formatted_html

@app.route('/blog')
def blog():
    return "Hello, it's blog!"

if __name__ == "__main__":
    app.run(debug=True)