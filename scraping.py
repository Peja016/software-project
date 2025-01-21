import requests
from bs4 import BeautifulSoup

# sentd HTTP request.
url = ''
response = requests.get(url)

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

formatted_html = soup.prettify()

# print(soup.prettify())