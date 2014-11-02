from bs4 import BeautifulSoup
import requests
from pprint import pprint

class RateBeer():
    def __init__(self):
        self.BASE_URL = "http://www.ratebeer.com"

    def search(self, query):
        # this feels bad to me
        # but if it fits, i sits
        output = {"breweries":[],"beers":[]}

        payload = {"BeerName": query}
        r = requests.post(self.BASE_URL+"/findbeer.asp", data = payload)
        soup = BeautifulSoup(r.text)
        s_results = soup.find_all('table',{'class':'results'})

        # find the brewery information
        s_breweries = s_results[0].find_all('tr')
        for row in s_breweries:
            location = row.find('td',{'align':'right'})
            output['breweries'].append({
                "name":row.a.contents,
                "url":row.a.get('href'),
                "location":location.contents[0].strip()
            })
        return output

    def beer(self, name):
        pass

    def brewery(self, name):
        pass

rb = RateBeer()
pprint(rb.search("summit"))