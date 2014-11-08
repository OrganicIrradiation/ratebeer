from bs4 import BeautifulSoup
import requests
import re

import exceptions

class RateBeer():
    """
    Makes getting information about beers and breweries from RateBeer.com as easy as:

    >>> summit_epa = RateBeer().beer("summit extra pale ale")

    A utility for searching RateBeer.com, finding information about beers, breweries, and reviews.

    The nature of web scraping means that this package is offered in perpetual beta.

    Requires BeautifulSoup, Requests, and lxml.

    See https://github.com/alilja/ratebeer for the full README.

    """

    class PageNotFound(Exception):
        pass

    def __init__(self):
        self.BASE_URL = "http://www.ratebeer.com"

    def _search(self, query):
        # this feels bad to me
        # but if it fits, i sits
        payload = {"BeerName": query}
        r = requests.post(self.BASE_URL+"/findbeer.asp", data = payload)
        return BeautifulSoup(r.text, "lxml")

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
                    "location":location.text.strip(),
                })
        # find beer information
        if any("beers" in s for s in soup.find_all("h1")) or not soup.find_all(text="0 beers"):
            s_beer_trs = iter(s_results[beer_location].find_all('tr'))
            next(s_beer_trs)
            for row in s_beer_trs: 
                link = row.find('td','results').a
                align_right = row.find_all("td",{'align':'right'})
                output['beers'].append({
                        "name":link.text,
                        "url":link.get('href'),
                        "id":re.search("/(?P<id>\d*)/",link.get('href')).group('id'),
                        "rating":align_right[-2].text.strip(),
                        "num_ratings":align_right[-1].text,
                    })
        return output

    def search(self, query):
        return self._parse(self._search(query))

    def beer(self, url):
        r = requests.get(self.BASE_URL+url, allow_redirects=True)
        soup = BeautifulSoup(r.text,"lxml")
        output = {}

        # check for 404s
        try:
            s_contents_rows = soup.find('div',id='container').find('table').find_all('tr')
        except AttributeError:
            raise RateBeer.PageNotFound(url)
        # ratebeer pages don't actually 404, they just send you to this weird "beer reference" 
        # page but the url doesn't actually change, it just seems like it's all getting done
        # server side -- so we have to look for the contents h1 to see if we're looking at the
        # beer reference or not
        if "beer reference" in s_contents_rows[0].find_all('td')[1].h1.contents:
            raise RateBeer.PageNotFound(url)

        info = s_contents_rows[1].tr.find_all('td')
        additional_info = s_contents_rows[1].find_all('td')[1].div.small
        abbr = additional_info.find_all(["abbr","a"])
        big = additional_info.find_all("big")
        if additional_info.find(text=re.compile("SEASONAL")):
            del big[2]
        for location, label in enumerate(abbr):
            key = None
            if "RATINGS" in label.text:  key = "num_ratings"
            if "CALORIES" in label.text: key = "calories"
            if "ABV" in label.text:      key = "abv"
            if "SEASONAL" in label.text: key = "season"
            if "IBU" in label.text:      key = "ibu"
            
            if key is not None:
                output[key] = big[location].text

        output.update({'name':s_contents_rows[0].find_all('td')[1].h1.text,
            'overall_rating':info[0].find_all('span', attrs={'itemprop':'average'})[0].text,
            'style_rating':info[0].find_all('div')[2].div.span.text,
            'brewery': info[1].a.text,
            'brewery_url':info[1].a.get('href'),
            'style':info[1].div.find_all('a')[1].text,
        })
        return output

    def reviews(self, url, pages=1,start_page=1,review_order="most recent"):
        assert pages > 0, "``pages`` must be greater than 0"
        assert start_page > 0, "``start_page`` must be greater than 0"
        review_order = review_order.lower()
        url_codes = {
            "most recent":1,
            "top raters":2,
            "highest score":3
            }
        url_flag = url_codes.get(review_order)
        if not url_flag: raise ValueError, "Invalid ``review_order``."

        output = []
        for page_number in range(start_page,start_page+pages):
            complete_url = "{0}{1}{2}/{3}/".format(self.BASE_URL, url, url_flag, page_number)
            r = requests.get(complete_url, allow_redirects=True)
            soup = BeautifulSoup(r.text, "lxml")
            content = soup.find('div',id='container').find('table').find_all('tr')[5]
            [x.extract() for x in content.find_all('table')] # strip ad section
            review_tuples = zip(*[iter(content.find_all('div'))] * 4) # basically magic
            for review in review_tuples:
                detail_tuples = zip(*[iter(review[0].find_all(["big","small"]))] * 2)
                details = dict([(
                        label.text.lower().strip().encode("ascii","ignore"), 
                        rating.text,
                    ) for (label, rating) in detail_tuples])
                details.update({'text':review[3].text})
                output.append(details)
        return output


    def brewery(self, url, include_beers=True):
        r = requests.get(self.BASE_URL+url, allow_redirects=True)
        soup = BeautifulSoup(r.text, "lxml")
        try:
            s_contents = soup.find('div',id='container').find('table').find_all('tr')[0].find_all('td')
        except AttributeError:
            raise RateBeer.PageNotFound(url)

        output = {
            'name':s_contents[8].h1.text,
            'type':re.search("Type: +(?P<type>[^ ]+)",s_contents[8].find_all('span','beerfoot')[1].text).group('type'),
            'street':s_contents[0].find('span',attrs={'itemprop':'streetAddress'}).text,
            'city':s_contents[0].find('span',attrs={'itemprop':'addressLocality'}).text,
            'state':s_contents[0].find('span',attrs={'itemprop':'addressRegion'}).text,
            'country':s_contents[0].find('span',attrs={'itemprop':'addressCountry'}).text,
            'postal_code':s_contents[0].find('span',attrs={'itemprop':'postalCode'}).text,
            }
        if include_beers:
            output.update({'beers':[]})
            s_beer_trs = iter(s_contents[8].find('table','maintable nohover').find_all('tr'))
            next(s_beer_trs)
            for row in s_beer_trs:
                beer = {
                    'name':row.a.text,
                    'url':row.a.get('href'),
                    'id':re.search("/(?P<id>\d*)/",row.a.get('href')).group('id'),
                    'rating':row.find_all('td')[4].text.strip(),
                    'num_ratings':row.find_all('td')[6].text.strip(),
                }
                output['beers'].append(beer)
        return output
