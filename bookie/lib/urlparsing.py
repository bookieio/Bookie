import re

def trim_utm(url):
    if "utm_" not in url:
        return url
    matches = re.findall('(.+\?)([^#]*)(.*)', url)
    if len(matches) == 0:
        return url
    match = matches[0]
    query = match[1]
    sanitized_query = '&'.join([p for p in query.split('&') if not p.startswith('utm_')])
    return match[0]+sanitized_query+match[2]
