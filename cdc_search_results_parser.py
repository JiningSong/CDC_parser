import ast
import json
from tqdm import tqdm
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

print(read_list())