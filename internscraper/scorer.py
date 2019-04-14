def score_link_heuristic(link, company):
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
