from bs4 import BeautifulSoup
import requests
from pprint import pprint

class RateBeer():
    def __init__(self):
        self.search_url = "http://www.ratebeer.com/search.php"

    def search(self, query):
        # this feels bad to me
        # but if it fits, i sits
        payload = {"id": "myform2", "BeerName": query, "SortBy": 1}
        r = requests.post(self.search_url, data = payload)
        soup = BeautifulSoup(r.text)

rb = RateBeer()
pprint(rb.search("summit extra pale ale"))