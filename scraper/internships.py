from googlesearch import search
from scorer import score_link_heuristic, score_page

from bs4 import BeautifulSoup
from selenium import webdriver

from queue import PriorityQueue
from urllib.parse import urlparse

import argparse
import time

MAX_DEPTH = 4
MAX_ENTRY_LINKS = 5
MAX_TOTAL_LINKS = 20


def normalize_link(link, parent=None, parent_base=None):
    # Fix relative links
    if link[0] == '/':
        link = parent_base + link
    if link[0] == '.':
        if parent[-1] == '/':
            link = parent + link
        else:
            link = parent + '/' + link

    # Trim ending slash in link
    if link[-1] == '/':
        link = link[:-1]

    return link.strip()


def scrape_company(company, max_depth=MAX_DEPTH,
                   max_entry_links=MAX_ENTRY_LINKS,
                   max_total_links=MAX_TOTAL_LINKS):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--incognito')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64 '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.77 Safari/537.36')
    driver = webdriver.Chrome(options=options)

    # At least one of these must be present in each link we visit
    # for that link to be considered explorable
    necessary_keywords = ['job', 'career', 'intern']

    # Find the company website, all entry links should come from here
    for url in search(company + ' careers website', stop=1):
        company_website = urlparse(url).netloc

    print('Company is {0}.'.format(company))
    print('Company careers website is {0}.'.format(company_website))

    # PQ contains the initial links we obtained from the Google search
    frontier = PriorityQueue()
    visited = set()
    search_term = company + ' internship apply'
    for entry_link in search(search_term, stop=max_entry_links):
        if urlparse(entry_link).netloc != company_website:
            continue
        entry_link = normalize_link(entry_link)
        heuristic = score_link_heuristic(entry_link, company)
        frontier.put((heuristic, (entry_link, 1)))
        visited.add(entry_link)

    results = []

    idx = 0
    while frontier and idx < max_total_links:
        # Extract current link we are on and the link's root (excludes path)
        score, (current, depth) = frontier.get()
        current_parse = urlparse(current)
        current_loc = current_parse.netloc
        current_base = current_parse.scheme + '://' + current_loc

        # TODO: Convert from printing to logging
        print('{0} (depth={1}, lh={2})'.format(current, depth, score))

        # Use Selenium to fetch our page, wait a bit for the page to load
        driver.get(current)
        time.sleep(2)
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
        soup = BeautifulSoup(content, 'lxml')
        if soup.header:
            soup.header.decompose()
        if soup.footer:
            soup.footer.decompose()

        # Assign score to page based off of BS4 parse
        company_short = company.lower() \
            .replace(' ', '').replace('.', '')
        page_score = score_page(soup, company_short)
        if page_score > 0:
            results.append((current, page_score))

        idx += 1

        # Child exploration cannot exceed the given maximum depth
        if depth < max_depth:
            # Collect links from both iframes and anchor tags
            links = []
            for anchor in soup.find_all('a', href=True):
                links.append(anchor.get('href'))
            for iframe in soup.find_all('iframe', src=True):
                links.append(iframe.get('src'))

            for link in links:
                # Filter out obviously bad links
                if not link or len(link) <= 2 or link[0] == '#' or \
                        'javascript:void' in link or link.startswith('mailto'):
                    continue

                # Fix relative links, trim trailing slashes, etc
                link = normalize_link(link, parent=current,
                                      parent_base=current_base)

                # Links must either be tied to the company or
                # an external job application website
                domain = urlparse(link).netloc
                if domain != company_website and \
                        company_short not in domain and \
                        'taleo' not in domain and \
                        'workday' not in domain and \
                        'greenhouse' not in domain and \
                        'jobvite' not in domain and \
                        'icims' not in domain:
                    continue

                # PDF or image links should not be followed
                if link.endswith('.pdf') or link.endswith('.jpg') or \
                        link.endswith('.jpg'):
                    continue

                # Skip links that have already been added to the frontier
                if link in visited:
                    continue

                heuristic = score_link_heuristic(link, company_short)
                frontier.put((heuristic, (link, depth + 1)))
                visited.add(link)
    driver.close()

    max_score = max([score for _, score in results])
    return [link for link, score in results if score == max_score]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Fetch internship links for a company.')
    parser.add_argument('company', type=str,
                        help='the target company')

    args = parser.parse_args()
    results = scrape_company(args.company)

    print('Results:')
    print(results)
