import urlparse

def clean_url(url):
    url_split = urlparse.urlparse(url)[:]
    match = url_split[1]
    if match[0:4] == 'www.':
        match = match[4:-1]
    query = url_split[4]
    sanitized_query = '&'.join([i for i in query.split('&') if not i.startswith('utm_')])
    clean_url_list = [i for i in url_split]
    clean_url_list[0] = ''
    clean_url_list[1] = match
    clean_url_list[4] = sanitized_query
    return urlparse.urlunparse(clean_url_list)
