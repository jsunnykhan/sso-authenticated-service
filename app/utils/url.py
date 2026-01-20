from urllib.parse import urlparse

def normalize_url(url: str) :
    url = url.replace("https://", "").replace("http://", "")
    url.strip("/")
    return urlparse(url)