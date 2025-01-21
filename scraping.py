import requests
from bs4 import BeautifulSoup

# sentd HTTP request.
url = 'https://hehethebox.com'
response = requests.get(url)

# parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# print(soup.prettify())