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
import string
import json
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
             'retired': False,
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

        data = {
                 "query":"query beerSearch($query: String, $order: SearchOrder, $first: Int, $after: ID) { searchResultsArr: beerSearch(query: $query, order: $order, first: $first, after: $after) { totalCount last items { beer { id name imageUrl overallScore ratingCount __typename } review { id score __typename } __typename   }   __typename } }", 
                 "variables": {"query":query, "order":"MATCH", "first":20},
                 "operationName":"beerSearch"
                }

        # options = requests.options("https://beta.ratebeer.com/v1/api/graphql/")

        request = requests.post(
            "https://beta.ratebeer.com/v1/api/graphql/"
           ,data=json.dumps(data)
           ,headers={"content-type": "application/json"}
        )
        output = {"breweries": [], "beers": []}

        try:
            search_results = json.loads(request.text)
        except:
            raise rb_exceptions.JSONParseException(query)

        for result in search_results['data']['searchResultsArr']['items']:
            if 'beer' in result:
                beer_data = result['beer']
                # double check this...
                url = '/beer/{0}/{1}/'.format(beer_data['name'].replace(' ', '-').lower(), beer_data['id'])
                beer = models.Beer(url, id=beer_data['id'])

                beer.name = beer_data['name']
                beer.overall_rating = beer_data['overallScore']
                beer.num_ratings = beer_data['ratingCount']
            output['beers'].append(beer)
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
            A dictionary, with beer styles strings for keys and integer ids
            for values.
        """
        styles = {}
        soup = soup_helper._get_soup("/top/")
        for item in [i for i in soup.find('select', id="StyleMenu").find_all('option') if i.get('name')]:
            styles[item.text.strip()] = int(item.get('value'))
        return styles

    def beer_style(self, ident, sort_type=None, sort_order=None):
        """Get all the beers from a specific beer style page.

        Args:
            ident (integer): The ID of the beer style from beer_style_list().
                For example, for 'Abbey Dubbel' it would be 71.
            sort_type (string): The sorting of the results. The valid choices
                are "score" (default), "count", and "abv".
            sort_order (string): "ascending" (low-to-high) or
                "descending" (high-to-low, default)

        Returns:
            A list of generator of beers.
        """
        if sort_type is None:
            sort_type = 'score'
        if sort_order is None:
            sort_order = 'descending'
        sort_type = sort_type.lower()
        sort_order = sort_order.lower()
        so = {'score': 0, 'count': 1, 'abv': 2}.get(sort_type)
        o = {'descending': 0, 'ascending': 1}.get(sort_order)

        soup = soup_helper._get_soup('/ajax/top-beer.asp?s={}&so={}&o={}'.format(ident, so, o))
        rows = iter(soup.table.find_all('tr'))
        next(rows)  # Get rid of the header
        for row in rows:
            data = row.find_all('td')
            link = data[1].a
            dataout = models.Beer(link.get('href'))
            dataout.name = link.text
            yield dataout

    def brewers_by_alpha(self, letter):
        """Returns a list of breweries that start with the provided letter.

        Args:
            letter (string): a single letter to search.

        Returns:
            A list of breweries.
            Each entry contains a name and a reference so you can look it up
            with the ``brewery`` method.
        """

        if letter not in string.ascii_uppercase and letter != '0-9':
            raise ValueError("Please only provide a single letter.")

        request = requests.post(
            soup_helper._BASE_URL + "/browsebrewers-" + letter + ".htm"
        )
        soup = BeautifulSoup(request.text, "lxml")
        breweries = []

        for entry in soup.select('a[href*=/brewers/]'):
            url = entry.get('href')
            brewer = models.Brewery(url)

            breweries.append(brewer)

        return breweries
