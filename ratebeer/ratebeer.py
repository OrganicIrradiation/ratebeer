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

try:
    import models
    import soup as soup_helper
except ImportError as e:  # No implicit package imports in py3.
    from ratebeer import models
    from ratebeer import soup as soup_helper


class RateBeer(object):
    """
    RateBeer.com data scraper. Makes getting information from RateBeer.com as easy as:

    .. code:: python

        >>> import ratebeer
        >>> rb = ratebeer.RateBeer()
        >>> results = rb.search("summit extra pale ale")
            {'beers': [<Beer('/beer/summit-extra-pale-ale/7344/')>,
                       <Beer('/beer/summit-extra-pale-ale--rose-petals/317841/')>],
             'breweries': []}
        >>> results['beers'][0]._populate()
        >>> results['beers'][0].__dict__
            {'_has_fetched': True,
             'abv': 5.1,
             'brewed_at': None,
             'brewery': <Brewery('/brewers/summit-brewing-company/1233/')>,
             'calories': 153,
             'description': 'Summit Extra Pale Ale is not a beer brewed only for beer '
                            'snobs. Just the opposite. It\x92s a beer for everyone to '
                            'enjoy: construction workers, stock brokers, farmers, sales '
                            'people, clerks, teachers, lawyers, doctors, even other '
                            'brewers. Its light bronze color and distinctly hoppy flavor '
                            'have made it a favorite in St. Paul, Minneapolis and the '
                            'rest of the Upper Midwest ever since we first brewed it '
                            'back in 1986.',
             'ibu': None,
             'img_url': 'http://res.cloudinary.com/ratebeer/image/upload/w_120,c_limit,q_85,d_no%20image.jpg/beer_7344.jpg',
             'mean_rating': None,
             'name': 'Summit Extra Pale Ale',
             'num_ratings': 701,
             'overall_rating': 67,
             'seasonal': None,
             'style': 'American Pale Ale',
             'style_rating': 58,
             'style_url': '/beerstyles/american-pale-ale/18/',
             'tags': ['fuggles', 'cascade', 'canned', 'extra pale ale', 'horizon'],
             'url': '/beer/summit-extra-pale-ale/7344/',
             'weighted_avg': 3.27}

    See the full README at https://github.com/alilja/ratebeer
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

        try:
            query = unicode(query, 'UTF8').encode('iso-8859-1')
        except (TypeError, NameError):  # Python 3 does not have unicode()
            query = query.encode('iso-8859-1')

        request = requests.post(
            soup_helper._BASE_URL + "/findbeer.asp",
            data={"BeerName": query}
        )
        soup = BeautifulSoup(request.text, "lxml")
        output = {"breweries": [], "beers": []}

        # Locate rows that contain the brewery and beer info
        beer_table = soup.find('h2', string='beers')
        if beer_table:
            for row in beer_table.next_sibling('tr'):
                # Only include ratable beers
                if row.find(title='Rate This Beer'):
                    url = row('td')[0].a.get('href')
                    url = re.sub(r"\s+", "", url, flags=re.UNICODE)
                    beer = models.Beer(url)
                    beer.name = row('td')[0].a.string.strip()
                    overall_rating = row('td')[3].string
                    num_ratings = row('td')[4].string
                    if overall_rating:
                        beer.overall_rating = int(overall_rating.strip())
                    if num_ratings:
                        beer.num_ratings = int(num_ratings.strip())
                    output['beers'].append(beer)

        brewer_table = soup.find('h2', string='brewers')
        if brewer_table:
            for row in brewer_table.next_sibling('tr'):
                url = row.a.get('href')
                url = re.sub(r"\s+", "", url, flags=re.UNICODE)
                brewer = models.Brewery(url)
                brewer.name = row.a.string
                brewer.location = row('td')[1].string.strip()
                output['breweries'].append(brewer)
        return output

    def get_beer(self, url, fetch=None):
        """Returns a Beer object for the requested URL"""
        if fetch is None:
            fetch = False
        return models.Beer(url, fetch)

    def beer(self, url):
        """Returns a dict with beer information for the requested URL"""
        return self.get_beer(url, True).__dict__

    def get_brewery(self, url, fetch=None):
        """Returns a Brewery object for the requested URL"""
        if fetch is None:
            fetch = False
        return models.Brewery(url, fetch)

    def brewery(self, url):
        """Returns a dict with brewery information for the requested URL"""
        return self.get_brewery(url, True).__dict__

    def beer_style_list(self):
        """Returns the beer styles from the beer styles page.

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
            A list of generator of beers.
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

        for row in rows:
            data = row.find_all('td')
            link = data[1].a
            dataout = models.Beer(link.get('href'))
            dataout.name = link.text
            yield dataout
        raise StopIteration
