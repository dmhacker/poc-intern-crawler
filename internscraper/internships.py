from googlesearch import search
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium import webdriver
from queue import PriorityQueue

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)


def search_company(company):
    search_term = company + ' student careers'
    for url in search(search_term, stop=10):
        result = search_link(company, url)
        if result:
            return result
    return None


def score_link(company, raw_link):
    score = 0
    link = raw_link.lower()
    if 'intern' in link:
        score -= 10
    if 'student' in link:
        score -= 2
    if 'career' in link:
        score -= 1
    if 'job' in link:
        score -= 1
    if company.lower() in link:
        score -= 1
    if 'software' in link:
        score -= 0.25
    if 'hardware' in link:
        score -= 0.25
    if 'engineer' in link:
        score -= 0.25
    if 'greenhouse' in link:
        score -= 0.25
    if 'workday' in link:
        score -= 0.25
    if 'taleo' in link:
        score -= 0.25
    return score


def search_link(company, top_level_link, max_depth=4):
    frontier = PriorityQueue()
    frontier.put((score_link(company, top_level_link), (top_level_link, 1)))
    visited = set([top_level_link])
    while frontier:
        score, datum = frontier.get()
        current, depth = datum
        current_root = 'http://' + urlparse(current).netloc
        print(current, depth, score)
        driver.get(current)
        content = driver.page_source
        lcontent = content.lower()
        if 'job' not in lcontent and \
                'career' not in lcontent and \
                'intern' not in lcontent:
            continue
        soup = BeautifulSoup(content, 'html.parser')
        if depth < max_depth:
            for anchor in soup.find_all('a'):
                link = anchor.get('href')
                if link and len(link) > 1 and link[0] != '#':
                    if link[0] == '/':
                        link = current_root + link
                    if link[0] == '.':
                        if current[-1] == '/':
                            link = current + link
                        else:
                            link = current + '/' + link
                    if 'javascript:void' not in link and \
                            link not in visited:
                        frontier.put((score_link(company, link),
                                      (link, depth + 1)))
                        visited.add(link)


print(search_company('Workday'))

driver.close()
