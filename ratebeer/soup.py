import requests

from bs4 import BeautifulSoup

import rb_exceptions

_BASE_URL = "http://www.ratebeer.com"


def _get_soup(url):
    if _BASE_URL in url:
        url.replace(_BASE_URL, '')
    req = requests.get(_BASE_URL + url, allow_redirects=True)
    if "ratebeer robot oops" in req.text.lower():
        raise rb_exceptions.PageNotFound(url)
    return BeautifulSoup(req.text, "lxml")
