import urlparse

def clean_url(url):
    url_split = urlparse.urlsplit(url)
    match = url_split.netloc
    if match[0:3] == 'www':
        match = match[4:-1]
    query = url_split.query
    sanitized_query = '&'.join([p for p in query.split('&') if not p.startswith('utm_')])
    return match+ url_split.path + '?' + sanitized_query
