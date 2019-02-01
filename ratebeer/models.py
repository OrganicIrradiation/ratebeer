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
import json
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
        id (int): id of the beer
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
    def __init__(self, url, fetch=None, id=None):
        """Initialize with URL and do not fetch"""
        self.url = url
        self.id = id
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

    def _format(self, value):
        """Sets what is now a blank string or int to None, otherwise returns value"""
        if value == "" or value == 0:
            return None
        else:
            return value

    def _populate(self):
        if not self.id:
            self.id = self.url.split('/')[-2]

        data = [
                 {"operationName":"beer",
                  "variables":{"beerId":self.id},
                  "query":"query beer($beerId: ID!) { \n info: beer(id: $beerId) { \n id \n name \n description \n style { \n id \n name \n glasses { \n id \n name \n __typename \n } \n __typename \n } \n styleScore \n overallScore \n averageRating \n abv \n ibu \n calories \n brewer { \n id \n name \n __typename \n } \n ratingCount \n isRetired \n isUnrateable \n seasonal \n labels \n availability { \n bottle \n tap \n distribution \n __typename \n } \n __typename \n } \n} \n"},
                 # {"operationName":"beerReviews",
                 #  "variables":
                 #   {"beerId":self.id,
                 #    "order":"RECENT",
                 #    "first":10
                 #   },
                 #  "query":"query beerReviews($beerId: ID!, $authorId: ID, $order: ReviewOrder, $after: ID) { \n beerReviewsArr: beerReviews(beerId: $beerId, authorId: $authorId, order: $order, after: $after) { \n items { \n id \n comment \n score \n scores { \n appearance \n aroma \n flavor \n mouthfeel \n overall \n __typename \n } \n author { \n id \n username \n reviewCount \n __typename \n } \n checkin { \n id \n place { \n name \n city \n state { \n name \n __typename \n } \n country { \n name \n __typename \n } \n __typename \n } \n __typename \n } \n createdAt \n updatedAt \n __typename \n } \n totalCount \n last \n __typename \n } \n} \n"},
                 {"operationName":"beerByAlias",
                  "variables":{"aliasId":self.id},
                  "query":"query beerByAlias($aliasId: ID!) {\n beerByAlias(aliasId: $aliasId) {\n id\n name \n overallScore \n __typename \n } \n } \n"},
                 {"operationName":"tagDisplay",
                  "variables":{"beerId":self.id},
                  "query":"query tagDisplay($beerId: ID!, $first: Int) { \n tagDisplayArr: beerTags(beerId: $beerId, first: $first) { \n items { \n id \n urlName: plain \n __typename \n } \n __typename \n } \n} \n"
                 }
                ]
        
        request = requests.post(
            "https://beta.ratebeer.com/v1/api/graphql/"
           ,data=json.dumps(data)
           ,headers={"content-type": "application/json"}
        )

        try:
            results = json.loads(request.text)
        except:
            raise rb_exceptions.JSONParseException(self.id)

        beer_data = results[0]['data']['info']

        if beer_data == None:
            raise rb_exceptions.PageNotFound(self.id)

        alias_data = results[1]['data']['beerByAlias']

        if alias_data != None:
            raise rb_exceptions.AliasedBeer(self.id, alias_data['id'])

        tag_data = results[2]['data']['tagDisplayArr']['items']

        self.name = beer_data['name']
        self.brewery = Brewery('/brewers/{0}/{1}/'.format(re.sub('[/ ]','-',beer_data['brewer']['name'].lower()),beer_data['brewer']['id']))
        self.brewery.name = beer_data['brewer']['name']
        self.brewed_at = None #no longer supported
        self.overall_rating = self._format(beer_data['overallScore'])
        self.style_rating = self._format(beer_data['styleScore'])
        self.style = beer_data['style']['name']
        self.style_url = "/beerstyles/{0}/{1}/".format(re.sub('/','-',self.style.lower()), beer_data['style']['id'])
        self.img_url = "https://res.cloudinary.com/ratebeer/image/upload/w_152,h_309,c_pad,d_beer_img_default.png,f_auto/beer_{0}".format(self.id)
        self.num_ratings = self._format(beer_data['ratingCount'])
        self.mean_rating = self._format(beer_data['averageRating'])
        self.weighted_avg = None # does not appear to exist anymore
        if(beer_data['seasonal'] != 'UNKNOWN'):
            self.seasonal = beer_data['seasonal']
        else:
            self.seasonal = None
        self.ibu = self._format(beer_data['ibu'])
        self.calories = self._format(beer_data['calories'])
        self.abv = self._format(beer_data['abv'])
        self.retired = beer_data['isRetired']
        self.description = re.sub(r'\x92', '\'', beer_data['description'])
        if tag_data:
            self.tags = [t['urlName'] for t in tag_data]
        else:
            self.tags = None

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
        # gets every second entry in a list
        review_title_attr = review_soup.find_all('div')[1].get('title')

        # some ratings may now just contain the x/5.0 rating, with no sub-ratings
        if '<small>' in review_title_attr: 
            raw_ratings = re.search(r'<small>(.+?)</small>', review_title_attr).group(1).split('<br />')
            # strip html and everything else
            for rating_text in raw_ratings:
                parts = rating_text.split(' ')
                # only set a rating if all of the information exists
                if rating_text:
                    label = parts[0]
                    rating_int = int(parts[1][:parts[1].find("/")])
                    setattr(
                        self,
                        label.lower().strip(),
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
            if abv and abv != '-':
                beer.abv = float(abv)
            if weighted_avg:
                beer.weighted_avg = float(weighted_avg)
            if style_rating:
                beer.style_rating = int(style_rating)
            if num_ratings:
                beer.num_ratings = int(num_ratings)
            yield beer
