def score_link_heuristic(link, company_abbrev):
    '''
    The higher the heuristic, the more likely
    the link contains something related to job
    applications.
    '''
    tags = [
        ('intern', 10), ('career', 3), ('job', 2),
        ('student', 0.5), ('university', 0.5),
        ('software', 0.25), ('hardware', 0.25),
        ('engineer', 0.25), ('greenhouse', 0.25),
        ('workday', 0.25), ('taleo', 0.25),
        ('jobvite', 0.25), ('icims', 0.25)
    ]
    score = 0
    llink = link.lower()
    for tag, weight in tags:
        if tag in llink:
            score += weight
    return score


def score_page(soup, company_abbrev):
    '''
    The higher the score, the more
    likely the page is a job application.
    '''
    score = 0

    # An apply button suggests that this is where
    # users would submit some kind of a job application
    buttons = []
    buttons.extend(soup.find_all('a'))
    buttons.extend(soup.find_all('button'))
    for button in buttons:
        btext = button.text.lower()
        if 'apply' in btext:
            score += 67
            break

    # See if we can find a header that contains something
    # related to software engineering or internships
    # If we do find one, we want to find the largest possible
    # one (fixes issues with Google's careers site)
    for header_type in range(1, 7):
        header_found = False
        for header in soup.find_all('h{0}'.format(header_type)):
            htext = header.text.lower()
            if not htext:
                continue
            if company_abbrev in htext:
                continue
            bonus = 6 - header_type
            if 'intern ' in htext or 'intern\n' in htext or \
                    htext.endswith('intern'):
                score += 17 + bonus / 2
                header_found = True
            if 'software' in htext and 'engineer' in htext:
                score += 16 + bonus / 2
                header_found = True
            if header_found:
                break
        if header_found:
            break

    return score
