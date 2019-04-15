import re


def score_link_heuristic(link, company_short):
    tags = [
        ('intern', -10), ('career', -3), ('job', -2),
        ('student', -0.5), ('university', -0.5),
        ('software', -0.25), ('hardware', -0.25),
        ('engineer', -0.25), ('greenhouse', -0.25),
        ('workday', -0.25), ('taleo', -0.25),
        ('jobvite', -0.25), ('icims', -0.25)
    ]
    score = 0
    llink = link.lower()
    for tag, tscore in tags:
        if tag in llink:
            score += tscore
    return score


def score_page(soup, company_short):
    score = 0

    portals = []
    portals.extend(soup.find_all('a'))
    portals.extend(soup.find_all('button'))
    for portal in portals:
        txt = portal.text.lower()
        if 'apply' in txt:
            score += 67
            break

    for header_type in range(1, 7):
        header = soup.find('h{0}'.format(header_type))
        if header:
            txt = header.text.lower()
            if company_short in txt:
                continue
            print(txt)
            bonus = 6 - header_type
            if 'intern' in txt:
                score += 17 + bonus / 2
            if 'software' in txt and 'engineer' in txt:
                score += 16 + bonus / 2
            break

    return score
