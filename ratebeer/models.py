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
from datetime import datetime

try:
    import rb_exceptions
    import soup as soup_helper
except ImportError:  # No implicit package imports in py3.
    from ratebeer import rb_exceptions
    from ratebeer import soup as soup_helper


class Beer(object):
    """The Beer object. Contains information about an individual beer.

    Args:
        url (string): the URL of the beer you're looking for.

    Returns:
        abv (float): percentage alcohol
        brewery (Brewery object): the beer's brewery
        brewed_at (Brewery object): actual brewery if contract brewed
        calories (float): estimated calories for the beer
        description (string): the beer's description
        img_url (string): a url to an image of the beer
        mean_rating (float): the mean rating for the beer (out of 5)
        name (string): the full name of the beer (may include the brewery name)
        num_ratings (int): the number of reviews*
        overall_rating (int): the overall rating (out of 100)
        seasonal (string): Summer, Winter, Autumn, Spring, Series, Special, None
        style (string): beer style
        style_url (string): beer style URL
        style_rating (int): rating of the beer within its style (out of 100)
        tags (list of strings): tags given to the beer
        url (string): the beer's url
        weighted_avg (float): the beer rating average, weighted using some unknown
            algorithm (out of 5)

        Any attributes not available will be returned as None

    """
    def __init__(self, url, fetch=None):
        """Initialize with URL and do not fetch"""
        self.url = url
        if fetch is None:
            fetch = False
        if fetch:
            self._populate()
        self._has_fetched = fetch

    def __getattr__(self, item):
        """Return the value of the `attr` attribute."""
        if item in self.__dict__.keys():
            return self.__dict__[item]
        elif not self._has_fetched:
            self._populate()
            return getattr(self, item)
        raise AttributeError('{0} has no attribute {1}'.format(type(self), item))

    def __setattr__(self, name, value):
        """Set the `name` attribute to `value."""
        object.__setattr__(self, name, value)

    def __getstate__(self):
        """Provide state information for pickling"""
        result = self.__dict__.copy()
        return result

    def __setstate__(self, statedata):
        """Reset the state after pickling"""
        self.__dict__ = statedata

    def __repr__(self):
        """Unambiguous representation to recreate object"""
        return "<Beer('{0}')>".format(self.url)

    def __str__(self):
        """Provide a nicely formatted representation"""
        return self.name

    def _populate(self):
        soup = soup_helper._get_soup(self.url)
        # check for 404s
        container = soup.find('div', id='container')
        try:
            container.find('div')
        except AttributeError:
            raise rb_exceptions.PageNotFound(self.url)
        # ratebeer pages don't actually 404, they just send you to this weird
        # "beer reference" page but the url doesn't actually change, it just
        # seems like it's all getting done server side -- so we have to look
        # for the contents h1 to see if we're looking at the beer reference or
        # not
        if "beer reference" in container.find('div').find('h1').text.strip():
            raise rb_exceptions.PageNotFound(self.url)

        if "Also known as " in container.find('div',class_="columns-container").text:
            raise rb_exceptions.AliasedBeer(self.url, container.find('div',class_="columns-container").find('a',href=re.compile('^/beer')).get('href'))

        # General information from the top of the page
        self.name = soup.find(itemprop='name').text.strip()
        breweries = soup.find_all('a', href=re.compile('brewers'))
        self.brewery = Brewery(breweries[1].get('href'))
        self.brewery.name = breweries[1].text
        if len(breweries) == 3:
            self.brewed_at = Brewery(breweries[2].get('href'))
            self.brewed_at.name = breweries[2].text
        else:
            self.brewed_at = None
        try:
            self.overall_rating = int(soup.find(class_='ratingValue').text)
        except ValueError: # 'n/a'
            self.overall_rating = None
        except AttributeError:
            self.overall_rating = None
        try:
            self.style_rating = int(soup.find(class_="style-text").previous_sibling.previous_sibling)
        except ValueError: # 'n/a'
            self.style_rating = None
        except AttributeError:
            self.style_rating = None
        self.style = soup.find(text='Style: ').next_sibling.text
        self.style_url = soup.find(text='Style: ').next_sibling.get('href')
        self.img_url = soup.find(id="beerImg").get('src')
        # Data from the info bar
        self.num_ratings = int(soup.find('span', itemprop="ratingCount").text)
        try:
            self.mean_rating = float(soup.find(text='MEAN: ').next_sibling.text.split('/')[0])
        except ValueError: # Empty mean rating: '/5.0'
            self.mean_rating = None
        except AttributeError: # No mean rating
            self.mean_rating = None
        try:
            self.weighted_avg = float(soup.find(text='WEIGHTED AVG: ').next_sibling.text.split('/')[0])
        except ValueError: # Empty weighted average rating: '/5'
            self.weighted_avg = None
        except AttributeError: # No weighted average rating
            self.weighted_avg = None
        try:
            self.seasonal = soup.find(text=u'\xa0\xa0 SEASONAL: ').next_sibling.text
        except AttributeError:
            self.seasonal = None
        try:
            self.ibu = int(soup.find(title="International Bittering Units - Normally from hops").next_sibling.next_sibling.text)
        except AttributeError:
            self.ibu = None
        try:
            self.calories = int(soup.find(title="Estimated calories for a 12 fluid ounce serving").next_sibling.next_sibling.text)
        except AttributeError:
            self.calories = None
        try:
            self.abv = float(soup.find(title="Alcohol By Volume").next_sibling.next_sibling.text[:-1])
        except ValueError: # Empty ABV: '-'
            self.abv = None
        if soup.find(title="Currently out of production"):
            self.retired = True
        else:
            self.retired = False
        # Description
        description = soup.find('span',itemprop="description")
        if hasattr(description,'text'):
            # strip ads and replace non-ASCII apostrophe with ASCII apostrophe
            [s.extract() for s in description('small')]
            self.description = ' '.join([s for s in description.strings]).strip()
            self.description = re.sub(r'\x92','\'',self.description)
        self.tags = [t.text[1:] for t in soup.find_all(class_='tags')]

        self._has_fetched = True

        return self

    def get_reviews(self, review_order="most recent"):
        """Returns reviews for a specific beer.

        Args:
            url (string): The specific url of the beer. Looks like:
                "/beer/deschutes-inversion-ipa/55610/"
            review_order (string): How to sort reviews. Three inputs:
                most recent: Newer reviews appear earlier.
                top raters: RateBeer.com top raters appear earlier.
                highest score: Reviews with the highest overall score appear
                earlier.

        Returns:
            A generator of dictionaries, containing the information about the review.
        """

        if not self._has_fetched:
            self._populate()

        review_order = review_order.lower()
        url_codes = {
            "most recent": 1,
            "top raters": 2,
            "highest score": 3
        }
        url_flag = url_codes.get(review_order)
        if not url_flag:
            raise ValueError("Invalid ``review_order``.")

        page_number = 1
        while True:
            complete_url = u'{0}{1}/{2}/'.format(self.url, url_flag, page_number)
            soup = soup_helper._get_soup(complete_url)
            content = soup.find('div', class_='reviews-container')
            reviews = content.find_all('div', style='padding: 0px 0px 0px 0px;')
            if len(reviews) < 1:
                raise StopIteration

            for review_soup in reviews:
                yield Review(review_soup)

            page_number += 1


class Review(object):
    """
    Args:
        review_soup (soup): the soup of the review

    Returns:
        appearance (int): rating for appearance (out of 5)
        aroma (int): aroma rating (out of 10)
        date (datetime): review date
        overall (int): overall rating (out of 20, for some reason)
        palate (int): palate rating (out of 5)
        rating (float): another overall rating provided in the review. Not sure how this different from overall.
        taste (int): taste rating (out of 10)
        text (string): actual text of the review.
        user_location (string): writer's location
        user_name (string): writer's username
    """

    def __init__(self, review_soup):
        # get ratings
        # gets every second entry in a list
        raw_ratings = zip(*[iter(review_soup.find('strong').find_all(["big", "small"]))] * 2)
        # strip html and everything else
        for (label, rating) in raw_ratings:
            rating_int = int(rating.text[:rating.text.find("/")])
            setattr(
                self,
                label.text.lower().strip(),
                rating_int
            )
        self.rating = float(review_soup.find_all('div')[1].text)

        # get user information
        userinfo = review_soup.next_sibling
        self.text = userinfo.next_sibling.next_sibling.text.strip()
        self.user_name = re.findall(r'(.*?)\xa0\(\d*?\)', userinfo.a.text)[0]
        self.user_location = re.findall(r'-\s(.*?)\s-', userinfo.a.next_sibling)[0]

        # get date it was posted
        date = re.findall(r'-(?:\s.*?\s-)+\s(.*)', userinfo.a.next_sibling)[0]
        self.date = datetime.strptime(date.strip(), '%b %d, %Y').date()

    def __str__(self):
        """Provide a nicely formatted representation"""
        return self.text


class Brewery(object):
    def __init__(self, url, fetch=None):
        """Initialize with URL and do not fetch"""
        self.url = url
        if fetch is None:
            fetch = False
        if fetch:
            self._populate()
        self._has_fetched = fetch

    def __getattr__(self, item):
        """Return the value of the `attr` attribute."""
        if item in self.__dict__.keys():
            return self.__dict__[item]
        elif not self._has_fetched:
            self._populate()
            return getattr(self, item)
        raise AttributeError('{0} has no attribute {1}'.format(type(self), item))

    def __setattr__(self, name, value):
        """Set the `name` attribute to `value."""
        object.__setattr__(self, name, value)

    def __getstate__(self):
        """Provide state information for pickling"""
        result = self.__dict__.copy()
        return result

    def __setstate__(self, statedata):
        """Reset the state after pickling"""
        self.__dict__ = statedata

    def __repr__(self):
        """Unambiguous representation to recreate object"""
        return "<Brewery('{0}')>".format(self.url)

    def __str__(self):
        """Provide a nicely formatted representation"""
        return self.name

    def _populate(self):
        """Returns information about a specific brewery.

        Args:
            url (string): The specific url of the beer. Looks like:
                "/brewers/new-belgium-brewing-company/77/"

        Returns:
            A dictionary of attributes about that brewery."""

        soup = soup_helper._get_soup(self.url)
        s_contents = soup.find_all('div', {'itemtype':'http://schema.org/LocalBusiness'})
        if not s_contents:
            raise rb_exceptions.PageNotFound(self.url)

        self.name = soup.h1.text
        self.type = s_contents[0].find_all('div')[1].text.strip()
        website = s_contents[0].find_all('div',{'class':'media-links'})[0].find_all('a')[0]
        if website:
            self.web = website['href']
        self.telephone = Brewery._find_span(s_contents[0], 'telephone')
        self.street = Brewery._find_span(s_contents[0], 'streetAddress')
        self.city = Brewery._find_span(s_contents[0], 'addressLocality')
        self.state = Brewery._find_span(s_contents[0], 'addressRegion')
        self.country = Brewery._find_span(s_contents[0], 'addressCountry')
        self.postal_code = Brewery._find_span(s_contents[0], 'postalCode')
        self._has_fetched = True

        return self

    @staticmethod
    def _find_span(search_soup, item_prop):
        output = search_soup.find('span', attrs={'itemprop': item_prop})
        output = output.text.strip() if output else None
        return output

    def get_beers(self):
        """Generator that provides Beer objects for the brewery's beers"""
        if not self._has_fetched:
            self._populate()

        _id = self.url.split('/')[-2]
        complete_url = u'/Ratings/Beer/ShowBrewerBeers.asp?BrewerID={0}'.format(_id)
        soup = soup_helper._get_soup(complete_url)
        soup_beer_rows = soup.find('table', id='brewer-beer-table').findAll('tr')

        for row in soup_beer_rows[1:]:
            url = row.a.get('href')
            # Only return rows that are ratable
            if not row.find('a',title="Rate this beer"):
                continue
            # Remove any whitespace characters. Rare, but possible.
            url = re.sub(r"\s+", "", url, flags=re.UNICODE)
            beer = Beer(url)
            beer.name = row.a.text.strip()
            # Add attributes from row
            abv = row.findAll('td')[1].text
            weighted_avg = row.findAll('td')[4].text.strip()
            style_rating = row.findAll('td')[5].text.strip()
            num_ratings = row.findAll('td')[6].text.strip()
            if abv:
                beer.abv = float(abv)
            if weighted_avg:
                beer.weighted_avg = float(weighted_avg)
            if style_rating:
                beer.style_rating = int(style_rating)
            if num_ratings:
                beer.num_ratings = int(num_ratings)
            yield beer
