from googlesearch import search
from scorer import score_link_heuristic

from bs4 import BeautifulSoup
from selenium import webdriver

from queue import PriorityQueue
from urllib.parse import urlparse

MAX_DEPTH = 4
MAX_ENTRY_LINKS = 3

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--incognito')
driver = webdriver.Chrome(options=options)


def scrape_company(company, max_depth=MAX_DEPTH):
    # At least one of these must be present in each link we visit
    # for that link to be considered explorable
    necessary_keywords = ['job', 'career', 'intern']

    # PQ contains the initial links we obtained from the Google search
    frontier = PriorityQueue()
    visited = set()
    search_term = company + ' internship apply'
    for entry_link in search(search_term, stop=MAX_ENTRY_LINKS):
        print(entry_link)
        heuristic = score_link_heuristic(entry_link, company)
        frontier.put((heuristic, (entry_link, 1)))
        visited.add(heuristic)

    while frontier:
        # Extract current link we are on and the link's root (excludes path)
        score, (current, depth) = frontier.get()
        current_root = 'http://' + urlparse(current).netloc

        # TODO: Convert from printing to logging
        print(current, depth, score)

        # Use Selenium to fetch our page
        driver.get(current)
        content = driver.page_source

        # Determine whether a page is explorable without doing
        # any HTML parsing by doing some primitive checks
        lcontent = content.lower()
        explorable = False
        for keyword in necessary_keywords:
            if keyword in lcontent:
                explorable = True
                break
        if not explorable:
            continue

        # Parse HTML using BS4, discard links in header and footer
        soup = BeautifulSoup(content, 'html.parser')
        if soup.header:
            soup.header.decompose()
        if soup.footer:
            soup.footer.decompose()

        # TODO: Assign score to page based off of BS4 parse

        # Only explore children of this page if they don't exceed
        # the maximum depth set
        if depth < max_depth:
            for anchor in soup.find_all('a'):
                link = anchor.get('href')
                if link and len(link) > 2 and \
                        link[0] != '#' and \
                        'javascript:void' not in link and \
                        not link.startswith('mailto'):
                    if link[0] == '/':
                        link = current_root + link
                    if link[0] == '.':
                        if current[-1] == '/':
                            link = current + link
                        else:
                            link = current + '/' + link
                    if link not in visited:
                        heuristic = score_link_heuristic(link, company)
                        frontier.put((heuristic, (link, depth + 1)))
                        visited.add(link)


print(scrape_company('Akuna Capital'))

driver.close()
