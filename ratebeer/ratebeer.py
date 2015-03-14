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

from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup

from exceptions import PageNotFound
from beer import Beer



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
    _BASE_URL = "http://www.ratebeer.com"

    def _get_soup(self, url):
        req = requests.get(RateBeer._BASE_URL + url, allow_redirects=True)
        if "ratebeer robot oops" in req.text.lower():
            raise RateBeer.PageNotFound(url)
        return BeautifulSoup(req.text, "lxml")

    def search(self, query):
        """Returns a list of beers and breweries that matched the search query.

        Args:
            query (string): The text of the search.

        Returns:
            A dictionary containing two lists, ``breweries`` and ``beers``.
            Each list contains a dictionary of attributes of that brewery or
            beer.
        """
        query = unicode(query,'UTF8').encode('iso-8859-1')
        if isinstance(query, unicode):
            query = query.encode('iso-8859-1')

        request = requests.post(
            RateBeer._BASE_URL + "/findbeer.asp",
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



    def reviews(self, url, review_order="most recent"):
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

        review_order = review_order.lower()
        url_codes = {
            "most recent": 1,
            "top raters": 2,
            "highest score": 3
        }
        url_flag = url_codes.get(review_order)
        if url_flag is None:
            raise ValueError("Invalid ``review_order``.")

        page_number = 1
        while True:
            complete_url = u'{0}{1}/{2}/'.format(url, url_flag, page_number)
            soup = self._get_soup(complete_url)
            content = soup.find('table', style='padding: 10px;').tr.td
            reviews = content.find_all('div', style='padding: 0px 0px 0px 0px;')

            if len(reviews) < 1:
                raise StopIteration

            for review in reviews:
                rating_details = review.find_all('div')
                # gets every second entry in a list
                individual_ratings = zip(*[iter(review.find('strong').find_all(["big", "small"]))]*2)

                details = {}
                details.update(dict([(
                    label.text.lower().strip().encode("ascii", "ignore"),
                    rating.text,
                ) for (label, rating) in individual_ratings]))
                userinfo = review.next_sibling

                details['rating'] = float(rating_details[1].text)
                details['user_name'] = re.findall(r'(.*?)\xa0\(\d*?\)', userinfo.a.text)[0]
                details['user_location'] = re.findall(r'-\s(.*?)\s-', userinfo.a.next_sibling)[0]
                details['date'] = re.findall(r'-\s.*?\s-\s(.*)', userinfo.a.next_sibling)[0]
                details['date'] = datetime.strptime(details['date'].strip(), '%b %d, %Y').date()
                details['text'] = userinfo.next_sibling.next_sibling.text.strip()
                yield details

            page_number += 1

    def brewery(self, url):
        """Returns information about a specific brewery.

        Args:
            url (string): The specific url of the beer. Looks like:
                "/brewers/new-belgium-brewing-company/77/"

        Returns:
            A dictionary of attributes about that brewery."""
        def _find_span(search_soup, item_prop):
            output = search_soup.find('span', attrs={'itemprop': item_prop})
            output = output.text if output else None
            return output

        def __beers(url):
            page_number = 1
            while True:
                complete_url = u'{0}/0/{1}/'.format(url, page_number)
                soup = self._get_soup(complete_url)
                beer_brewery = soup.h1.text
                beer_brewery_url = url
                s_beer_trs = soup.find('table', 'maintable nohover').findAll('tr')

                if len(s_beer_trs) < 2:
                    raise StopIteration

                for row in s_beer_trs[1:]:
                    if 'Brewed at ' in row.text:
                        if 'by/for' in row.text:
                            beer_brewery = row.a.text.strip()
                            beer_brewery_url = row.a['href']
                            beer_brewed_at =  output['name']
                            beer_brewed_at_url = output['url']
                        else:
                            beer_brewery =  output['name']
                            beer_brewery_url =  output['url']
                            if row.a.text.strip() == output['name']:
                                beer_brewed_at = u''
                                beer_brewed_at_url = u''
                            else:
                                beer_brewed_at = row.a.text.strip()
                                beer_brewed_at_url = row.a['href']
                    elif len(row.findAll('a', class_='rate')) > 0 :
                        link = row.a
                        row_data = row.findAll('td')
                        abv = row_data[2].text.strip()
                        weighted_avg = row_data[3].text.strip()
                        overall_rating = row_data[4].text.strip()
                        style_rating = row_data[5].text.strip()
                        num_ratings = row_data[6].text.strip()
                        beer ={}
                        beer['name'] = link.text.strip()
                        beer['url'] = link.get('href')
                        beer['id'] = int(re.search(r"/(?P<id>\d*)/", link.get('href')).group('id'))
                        beer['brewery'] = beer_brewery
                        beer['brewery_url'] = beer_brewery_url
                        if 'beer_brewed_at' in locals() and len(beer_brewed_at)>0:
                            beer['brewed_at'] = beer_brewed_at
                            beer['brewed_at_url'] = beer_brewed_at_url
                        if len(abv)>0:
                            beer['abv'] = float(abv)
                        if len(abv)>0:
                            beer['abv'] = float(abv)
                        if len(weighted_avg)>0:
                            beer['weighted_avg'] = float(weighted_avg)
                        if len(overall_rating)>0:
                            beer['overall_rating'] = int(overall_rating)
                        if len(style_rating)>0:
                            beer['style_rating'] = int(style_rating)
                        if len(num_ratings)>0:
                            beer['num_ratings'] = int(num_ratings)
                        yield beer
                page_number += 1

        soup = self._get_soup(url)
        try:
            s_contents = soup.find('div', id='container').find('table').find_all('tr')[0].find_all('td')
        except AttributeError:
            raise RateBeer.PageNotFound(url)

        output = dict()
        output['name'] = soup.h1.text
        output['url'] = url
        output['url_name'] = re.findall(r'/brewers/(.*?)/', url)[0]
        output['type'] = re.findall(r'Type: (.*?)<br\/>', soup.renderContents())[0]
        output['street'] = _find_span(s_contents[0], 'streetAddress')
        output['city'] = _find_span(s_contents[0], 'addressLocality')
        output['state'] = _find_span(s_contents[0], 'addressRegion')
        output['country'] = _find_span(s_contents[0], 'addressCountry')
        output['postal_code'] = _find_span(s_contents[0], 'postalCode')
        output = dict((k, v.strip()) for k, v in output.iteritems() if v)
        output['beers'] = __beers(url)

        return output

    def beer_style_list(self):
        """Returns the list of beer styles from the beer styles page.

        Returns:
            A dictionary, with beer styles for keys and urls for values.
        """
        styles = {}

        soup = self._get_soup("/beerstyles/")
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
            RateBeer._BASE_URL +
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
