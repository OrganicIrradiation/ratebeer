# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

import re
import requests
from bs4 import BeautifulSoup

import models
import soup as soup_helper


class RateBeer(object):
    """
    Makes getting information about beers and breweries from RateBeer.com easy.

    >>> summit_search = RateBeer().search("summit extra pale ale")

    A utility for searching RateBeer.com, finding information about beers,
    breweries, and reviews. The nature of web scraping means that this package
    is offered in perpetual beta.

    Requires BeautifulSoup4, Requests, and lxml. See
    https://github.com/alilja/ratebeer for the full README.

    """
    def search(self, query):
        """Returns a list of beers and breweries that matched the search query.

        Args:
            query (string): The text of the search.

        Returns:
            A dictionary containing two lists, ``breweries`` and ``beers``.
            Each list contains a dictionary of attributes of that brewery or
            beer.
        """
        query = unicode(query, 'UTF8').encode('iso-8859-1')
        if isinstance(query, unicode):
            query = query.encode('iso-8859-1')

        request = requests.post(
            soup_helper._BASE_URL + "/findbeer.asp",
            data={"BeerName": query}
        )
        soup = BeautifulSoup(request.text, "lxml")
        soup_results = soup.find_all('table', {'class': 'results'})
        output = {"breweries": [], "beers": []}

        # Locate rows that contain the brewery and beer info
        for index, val in enumerate(soup.find_all("h1")):
            if "brewers" in val:
                # find brewery information
                soup_breweries = soup_results[index - 1].find_all('tr')
                for row in soup_breweries:
                    location = row.find('td', {'align': 'right'})

                    output['breweries'].append({
                        "name": row.a.text,
                        "url": row.a.get('href'),
                        "id": int(re.search(r"/(?P<id>\d*)/", row.a.get('href')).group('id')),
                        "location": location.text.strip(),
                    })

            elif "beers" in val:
                # find beer information
                if not soup.find_all(text="0 beers"):
                    soup_beer_rows = iter(soup_results[index - 1].find_all('tr'))
                    next(soup_beer_rows)
                    for row in soup_beer_rows:
                        link = row.find('td', 'results').a
                        row_data = row.findAll('td')
                        overall_rating = row_data[3].text.strip()
                        num_ratings = row_data[4].text.strip()
                        beer = {}
                        beer['name'] = link.text
                        beer['url'] = link.get('href')
                        beer['id'] = int(re.search(r"/(?P<id>\d*)/", link.get('href')).group('id'))
                        if len(overall_rating) > 0:
                            beer['overall_rating'] = int(overall_rating)
                        if len(num_ratings) > 0:
                            beer['num_ratings'] = int(num_ratings)
                        output['beers'].append(beer)
        return output

    def get_beer(self, url):
        return models.Beer(url)

    def beer(self, url):
        return self.get_beer(url).__dict__

    def get_brewery(self, url):
        return models.Brewery(url)

    def brewery(self, url):
        return self.get_brewery(url).__dict__

    def beer_style_list(self):
        """Returns the list of beer styles from the beer styles page.

        Returns:
            A dictionary, with beer styles for keys and urls for values.
        """
        styles = {}

        soup = soup_helper._get_soup("/beerstyles/")
        columns = soup.find_all('table')[2].find_all('td')
        for column in columns:
            lines = [li for li in column.find_all('li')]
            for line in lines:
                styles[line.text] = line.a.get('href')
        return styles

    def beer_style(self, url, sort_type="overall"):
        """Get all the beers from a specific beer style page.

        Args:
            url (string): The specific url of the beer style. Looks like:
                "/beerstyles/abbey-dubbel/71/"
            sort_type (string): The sorting of the results. "overall" returns
                the highest- rated beers, while "trending" returns the newest
                and trending ones.

        Returns:
            A list of dictionaries containing the beers.
        """
        sort_type = sort_type.lower()
        url_codes = {"overall": 0, "trending": 1}
        sort_flag = url_codes.get(sort_type)
        if sort_flag is None:
            raise ValueError("Invalid ``sort_type``.")
        style_id = re.search(r"/(?P<id>\d*)/", url).group('id')

        req = requests.post(
            soup_helper._BASE_URL +
            (
                "/ajax/top-beer-by-style.asp?style={0}&sort={1}"
                "&order=0&min=10&max=9999&retired=0&new=0&mine=0&"
            )
            .format(style_id, sort_flag),
            allow_redirects=True
        )
        soup = BeautifulSoup(req.text, "lxml")
        rows = iter(soup.table.find_all('tr'))
        next(rows)

        output = []
        for row in rows:
            data = row.find_all('td')
            output.append({
                'name': data[1].text,
                'url': data[1].a.get('href'),
                'rating': float(data[4].text)
            })
        return output

if __name__ == "__main__":
    print "hello"
    rb = RateBeer()
    brewery = rb.get_brewery("/brewers/deschutes-brewery/233/")
    beers = brewery.get_beers()
    for i in range(10):
        reviews = beers.next().get_reviews()
        for j in range(10):
            print reviews.next()

