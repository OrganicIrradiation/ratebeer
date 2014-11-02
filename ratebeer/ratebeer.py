from bs4 import BeautifulSoup
import requests
import re

class RateBeer():
    """
    Makes getting information about beers and breweries from RateBeer.com as easy as

    >>> summit_epa = RateBeer().beer("summit extra pale ale")

    Includes utilities for searching the RateBeers site, and will return information
    in a friendly, Pythonic way.

    """

    class NotFoundError(Exception):
        pass

    def __init__(self):
        self.BASE_URL = "http://www.ratebeer.com"

    def _search(self, query):
        # this feels bad to me
        # but if it fits, i sits
        payload = {"BeerName": query}
        r = requests.post(self.BASE_URL+"/findbeer.asp", data = payload)
        return BeautifulSoup(r.text)

    def _parse(self, soup):
        s_results = soup.find_all('table',{'class':'results'})
        output = {"breweries":[],"beers":[]}
        beer_location = 0
        # find brewery information
        if any("brewers" in s for s in soup.find_all("h1")):
            s_breweries = s_results[0].find_all('tr')
            beer_location = 1
            for row in s_breweries:
                location = row.find('td',{'align':'right'})
                output['breweries'].append({
                    "name":row.a.contents,
                    "url":row.a.get('href'),
                    "id":re.search("/(?P<id>\d*)/",row.a.get('href')).group('id'),
                    "location":location.contents[0].strip(),
                })
        # find beer information
        if any("beers" in s for s in soup.find_all("h1")) or not soup.find_all(text="0 beers"):
            s_beers = iter(s_results[beer_location].find_all('tr'))
            next(s_beers)
            for row in s_beers: 
                link = row.find('td','results').a
                align_right = row.find_all("td",{'align':'right'})
                output['beers'].append({
                        "name":link.contents[0],
                        "url":link.get('href'),
                        "id":re.search("/(?P<id>\d*)/",link.get('href')).group('id'),
                        "rating":align_right[-2].contents[0].strip(),
                        "num_ratings":align_right[-1].contents[0],
                    })
        return output

    def search(self, query):
        return self._parse(self._search(query))

    def beer(self,url):
        r = requests.get(self.BASE_URL+url, allow_redirects=True)
        soup = BeautifulSoup(r.text)
        # check for 404s
        try:
            s_contents = soup.find('div',id='container').find('table').find_all('tr')
        except AttributeError:
            raise self.NotFoundError
        # ratebeer pages don't actually 404, they just send you to this weird "beer reference" 
        # page but the url doesn't actually change, it just seems like it's all getting done
        # server side -- so we have to look for the contents h1 to see if we're looking at the
        # beer reference or not
        if "beer reference" in s_contents[0].find_all('td')[1].h1.contents:
            raise NotFoundError

        meta_info =  s_contents[1].tr.find_all('td')
        output = {'name':s_contents[0].find_all('td')[1].h1.contents[0],
            'overall_rating':meta_info[0].find_all('span', attrs={'itemprop':'average'})[0].contents[0],
            'style_rating':meta_info[0].find_all('div')[2].div.span.contents[0],
}
        return output

    def brewery(self,url):
        pass

