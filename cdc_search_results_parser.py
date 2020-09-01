import re
import ast
import json
import string
import pandas as pd
from tqdm import tqdm
from pandas import DataFrame
from util import generate_soup


SEARCH_RESULTS_BASE_URL = "https://search.cdc.gov/search/index.html?any=%22drug%20use%22%20%22drug%20abuse%22&url=mmwr&date1=01%2F01%2F2016&dpage={}#content"
MAX_PAGE = 108

def get_search_result_urls():
    search_result_urls = []
    with tqdm(total=MAX_PAGE, desc="Crawling HAN Messages: ") as pbar:
        for i in range(MAX_PAGE):
            soup = generate_soup(SEARCH_RESULTS_BASE_URL.format(i+1))
            results = soup.findAll('div', class_='searchResultsUrl')
            for result in results:
                search_result_urls.append(result.contents[0])
            pbar.update(1)
        pbar.close()

    return search_result_urls

def read_list():
    f = open('search_result_urls.txt', 'r')
    search_result_urls = ast.literal_eval(f.read())
    f.close()
    return search_result_urls

search_result_urls = read_list()

# check if url contain html or htm. (only consider these cases)
message_urls = []
for url in search_result_urls:
    if re.match("^https://www.cdc.gov/mmwr/volumes/.*(html|htm)$", url) is not None:
        message_urls.append(url)

# get title
def get_message_title(soup):
    try:
        title = soup.find('span', attrs={'class': 'mobile-title'}).get_text()
    except:
        title = 'null'
    
    return title

# get date
def get_message_time(soup):
    try:
        date = str(soup.select_one('.dateline > p')).split('/')[2]
    except:
        date = 'null'
    
    return date

# get links within message body
def get_links(soup):
    cdc_links = []
    try:
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
    except:
        pass

    return cdc_links

# get the entire message body
def get_message_body(soup):
    full_text = ""
    
    # finding upper gray area of text
    try:
        gray_contents = soup.find('div', {"class": re.compile('.*order-0.*')}).find_all('p')
        for elem in gray_contents:
            text = elem.get_text()
            text = re.sub('\(\d+[^)]*\)', '', text, 100)
            text = re.sub('\((Table|Figure) \d+\)', '', text, 100)
            full_text += text
    except:
        pass

    # finding lower white area of text
    texts = []
    try:
        contents = soup.findAll('div',attrs={"class":"order-4 w-100"})

        for elem in contents:
            children = elem.find_all(['div', 'p'], recursive=False)
            for child in children:
                if child.name == 'div':
                    y = child.findChildren('p')
                    texts += list(map(lambda x: x.get_text(), y))
                else:
                    texts.append(child.get_text())

        for text in texts:
            text = re.sub('\(\d+[^)]*\)', '', text, 100)
            text = re.sub('\((Table|Figure) \d+\)', '', text, 100)
            full_text += text
    except:
        pass

    return full_text

# find title, date, text, links(consider: get_links from han_parser.py)
def parse_data(url):
    soup = generate_soup(url)

    # Find message title
    title = get_message_title(soup)      
    # Find message publish date
    publish_date = get_message_time(soup)
    # Find CDC links
    links = get_links(soup)
    # Find texts
    text = get_message_body(soup)
    
    # result_dict = {
    #     "message_id": message_id, 
    #     "title": title,
    #     "url": message_url,
    #     "message_type": message_type,
    #     "publish_date": publish_date,
    #     "text": text,
    #     "links": links
    # }
    result_dict = {
        "title": title,
        "url": url,
        "publish_date": publish_date,
        "links": links,
        "text": text
    }

    return result_dict


if __name__ == "__main__":
    # Output result list
    results = []
    
    # loops through all message_urls and store parsed data into results list as dicts
    with tqdm(total=len(message_urls), desc="Crawling search result Messages: ") as pbar:
       
        for message_url in message_urls:
            result_dict = parse_data(message_url)
            results.append(result_dict)
            pbar.update(1)
        pbar.close()
        pd.set_option('display.max_columns', None)
        df = DataFrame(results)
        df.to_csv('CDC_search_results.csv', index=False)
        print(df)

# finding lower white area of text
# texts = []
# contents = soup.findAll('div',attrs={"class":"order-4 w-100"})

# for elem in contents:
#     children = elem.find_all(['div', 'p'], recursive=False)
#     for child in children:
#         if child.name == 'div':
#             y = child.findChildren('p')
#             texts += list(map(lambda x: x.get_text(), y))
#         else:
#             texts.append(child.get_text())

# for text in texts:
#     text = re.sub('\(\d+[^)]*\)', '', text, 100)
#     text = re.sub('\((Table|Figure) \d+\)', '', text, 100)
#     full_text += text
# print(full_text)