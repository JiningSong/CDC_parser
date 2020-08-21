import requests
from bs4 import BeautifulSoup

ROOT_URL = "https://emergency.cdc.gov{}"
ARCHIVE_URL = "https://emergency.cdc.gov/han/{}.asp"

def get_article_urls():
    article_urls = []
    for year in range(2015,2021):
        markup = requests.get(ARCHIVE_URL.format(year)).content
        soup = BeautifulSoup(markup, "lxml")
        articles = soup.find('ul', class_='block-list').findAll('li')

        for article in articles:
            link = ROOT_URL.format(article.find('a')['href'])
            article_urls.append(link)
    return article_urls

print(get_article_urls())

