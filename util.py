from requests_html import HTMLSession
from bs4 import BeautifulSoup


def generate_soup(url):
    session = HTMLSession()
    try:
        r = session.get(url)
        r.html.render()

        if r.status_code == 200:
            return BeautifulSoup(r.html.html, "lxml")
    except Exception as e:
        print(e)