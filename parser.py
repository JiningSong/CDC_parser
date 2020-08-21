import requests
from bs4 import BeautifulSoup

ROOT_URL = "https://emergency.cdc.gov{}"
ARCHIVE_URL = "https://emergency.cdc.gov/han/{}.asp"
UL_CLASS = 'block-list'

def generate_soup(url):
    markup = requests.get(url).content
    soup = BeautifulSoup(markup, "lxml")
    return soup


def get_message_urls():
    message_urls = []
    for year in range(2015,2021):
        url = ARCHIVE_URL.format(year)
        soup = generate_soup(url)
        messages = soup.find('ul', class_=UL_CLASS).findAll('li')

        for message in messages:
            link = ROOT_URL.format(message.find('a')['href'])
            message_urls.append(link)
    return message_urls

def get_message_type(soup):
    message_type = soup.findAll('img', class_='img-fluid')[1]['alt'].lower()
    if "health advisory" in message_type:
        return "Health Advisory"
    elif "health alert" in message_type:
        return "Health Alert"
    elif "health update" in message_type:
        return "Health Update"
    elif "info service" in message_type:
        return "Info Service"
    else:
        return "Unknown"


    return message_type

def get_message_time(soup):
    content = list(list(soup.find('div', class_='col content').children)[-2])[-3]
    if content.find('div', class_="text-red")!= None:
        try:
            time = content.select_one('div.col-md-12 > div.text-red > p').contents[2]
        except:
            return "NULL"
    else:
        try:
            if len(content.select_one('div.col-md-12 > p').contents) > 1:
                time = content.select_one('div.col-md-12 > p').contents[2]
            else:
                time = content.select_one('div.col-md-12 > p:nth-child(2)').contents[0]
        except:
            return "NULL"
    
    #FIXME: Hardcoded for an edge case that contains a redundant <p> tag under 'col-md-12'
    if "Distributed" in time:
        return "NULL"

    return time.strip()

if __name__ == "__main__":
    results = []

    message_urls = get_message_urls()

    for message_url in message_urls:
        result_dict = {"url": message_url}

        soup = generate_soup(message_url)

        # Find message type
        message_type = get_message_type(soup)
        result_dict['type'] = message_type

        # Find message title
        title = soup.find('h1').contents[0]
        result_dict['title'] = title

        # Find message time
        time = get_message_time(soup)
        result_dict['time'] = time

        results.append(result_dict)

    for el in results:
        print(el)
    # message1 = "https://emergency.cdc.gov/han/han00382.asp"

    # print(message1)
    # soup = generate_soup(message1)
    # print()


