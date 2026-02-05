from urllib.parse import urlparse

def normalize_url(url: str):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return urlparse(url)