import re
import requests
import string
from tqdm import tqdm
from bs4 import BeautifulSoup
from pandas import DataFrame
from util import generate_soup

# Constants
ROOT_URL = "https://emergency.cdc.gov{}"
ARCHIVE_URL = "https://emergency.cdc.gov/han/{}.asp"
UL_CLASS = 'block-list'


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


def get_message_id(url):
    return "CDC" + url.split('/')[-1].split('.')[0].upper()


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


def get_message_body(soup):

    content = list(list(soup.find('div', class_='col content').children)[-2])[-3].select('div.col-md-12')
    if len(content) == 1:
        return parse_text(content[0])

    elif len(content) == 2:
        if len(content[0].select('p')) > 3:
            return parse_text(content[0])
        else:
            return parse_text(content[1])
    else:
        pass

    print()


def parse_text(tag):
    full_text = ""
    # paragraphs = tag.select('p')
    # for paragraph in paragraphs:
    #     print(paragraph.findAll(text=True, recursive=True))
    children = list(tag.findAll(recursive=False))
    for child in children:
        if child.name in ['p', 'h2', 'h3', 'ul', 'ol']:
            texts = (child.findAll(text=True, recursive=True))
            for text in texts:
                text = str(text)
                if "for more information" in text.lower():
                    return full_text
                if text != '\n' and re.match("^\[\d+\]$", text) is None and text.strip('\n') not in string.punctuation:
                    full_text += '\n' + text
    return full_text


def get_links(soup):
    cdc_links = []
    links = soup.select('a')
    for link in links:
        try:
            href = link['href']

            if re.match("^https://www.cdc.gov/.*(html|htm)$", href) is not None and\
                '/other' not in href.lower() and\
                '/contact' not in href.lower() and\
                '/index' not in href.lower() and\
                '/cdc-info' not in href.lower() and\
                '/about' not in href.lower():
                cdc_links.append(href)
        except:
            pass

    return cdc_links


def parse_data(url):
    soup = generate_soup(message_url)
            
    # Get message ID
    message_id = get_message_id(message_url)

    # Find message title
    title = soup.find('h1').contents[0]        
    # Find message type
    message_type = get_message_type(soup)
    # Find message publish date
    publish_date = get_message_time(soup)
    # Find CDC links
    links = get_links(soup)
    # Find texts
    text = get_message_body(soup)
    
    result_dict = {
        "message_id": message_id, 
        "title": title,
        "url": message_url,
        "message_type": message_type,
        "publish_date": publish_date,
        "text": text,
        "links": links
    }

    return result_dict


if __name__ == "__main__":
    # Output result list
    results = []
    
    # Get all messages' URLs and store in a list
    message_urls = get_message_urls()
    
    # loops through all message_urls and store parsed data into results list as dicts
    with tqdm(total=len(message_urls), desc="Crawling HAN Messages: ") as pbar:
       
        for message_url in message_urls:
            result_dict = parse_data(message_url)
            results.append(result_dict)
            pbar.update(1)
        pbar.close()
        df = DataFrame(results)
        df.to_csv('HAN_Archive.csv', index=False)
        print(df)