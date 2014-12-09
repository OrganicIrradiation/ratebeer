from exceptions import Exception
from bs4 import BeautifulSoup
import re
import requests


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

    class PageNotFound(Exception):
        """Returns the URL of the page not found."""
        pass

    class AliasedBeer(Exception):
        """Returns the old and new urls for an aliased beer."""
        def __init__(self, oldurl, newurl):
            self.oldurl = oldurl
            self.newurl = newurl

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
        r = requests.post(RateBeer._BASE_URL + "/findbeer.asp",
                          data={"BeerName": query})
        soup = BeautifulSoup(r.text, "lxml")
        s_results = soup.find_all('table', {'class': 'results'})
        output = {"breweries": [], "beers": []}
        beer_location = 0

        # find brewery information
        if any("brewers" in s for s in soup.find_all("h1")):
            s_breweries = s_results[0].find_all('tr')
            beer_location = 1
            for row in s_breweries:
                location = row.find('td', {'align': 'right'})
                output['breweries'].append({
                    "name": row.a.contents,
                    "url": row.a.get('href'),
                    "id": re.search(r"/(?P<id>\d*)/", row.a.get('href')).group('id'),
                    "location": location.text.strip(),
                })

        # find beer information
        if any("beers" in s for s in soup.find_all("h1")) or not soup.find_all(text="0 beers"):
            s_beer_trs = iter(s_results[beer_location].find_all('tr'))
            next(s_beer_trs)
            for row in s_beer_trs:
                link = row.find('td', 'results').a
                align_right = row.find_all("td", {'align': 'right'})
                output['beers'].append({
                    "name": link.text,
                    "url": link.get('href'),
                    "id": re.search(r"/(?P<id>\d*)/", link.get('href')).group('id'),
                    "rating": align_right[-2].text.strip(),
                    "num_ratings": align_right[-1].text,
                })
        return output

    def beer(self, url):
        """Returns information about a specific beer.

        Args:
            url (string): The specific url of the beer. Looks like:
                "/beer/deschutes-inversion-ipa/55610/"

        Returns:
            A dictionary of attributes about that beer."""
        soup = self._get_soup(url)
        output = {}

        # check for 404s
        try:
            s_contents_rows = soup.find('div', id='container').find('table').find_all('tr')
        except AttributeError:
            raise RateBeer.PageNotFound(url)
        # ratebeer pages don't actually 404, they just send you to this weird
        # "beer reference" page but the url doesn't actually change, it just
        # seems like it's all getting done server side -- so we have to look
        # for the contents h1 to see if we're looking at the beer reference or
        # not
        if "beer reference" in s_contents_rows[0].find_all('td')[1].h1.contents:
            raise RateBeer.PageNotFound(url)

        if "Also known as " in s_contents_rows[1].find_all('td')[1].div.div.contents:
            raise RateBeer.AliasedBeer(url, s_contents_rows[1].find_all('td')[1].div.div.a['href'])

        brew_info_row = s_contents_rows[1].find_all('td')[1].div.small
        brew_info = brew_info_row.text.split(u'\xa0\xa0')
        brew_info = [s.split(': ') for s in brew_info]
        keywords = {
            "RATINGS": "num_ratings",
            "MEAN": "mean",
            "WEIGHTED AVG": "weighted_avg",
            "SEASONAL": "seasonal",
            "CALORIES": "calories",
            "ABV": "abv",
            "IBU": "ibu",
        }
        for meta_name, meta_data in brew_info:
            for keyword in keywords:
                if keyword in meta_name:
                    if keyword == "MEAN":
                        meta_data = meta_data[:meta_data.find("/")]
                    output[keywords[keyword]] = meta_data
                    break

        info = s_contents_rows[1].tr.find_all('td')

        brewery_info = info[1].find('div').contents
        brewery = brewery_info[0].findAll('a')[0]
        brewed_at = None
        if 'Brewed at' in brewery_info[0].text:
            brewed_at = brewery_info[0].findAll('a')[1]

        style = brewery_info[3]
        description = s_contents_rows[1].find_all('td')[1].find(
            'div', style=(
                'border: 1px solid #e0e0e0; background: #fff; '
                'padding: 14px; color: #777;'
            )
        )

        name = s_contents_rows[0].find_all('td')[1].h1
        overall_rating = info[0].find_all('span', itemprop='average')
        style_rating = info[0].find_all('div')
        if len(style_rating) < 2:
            style_rating = None

        output['name'] = name.text.strip()
        if overall_rating:
            output['overall_rating'] = overall_rating[0].text.strip()
        if style_rating:
            output['style_rating'] = style_rating[2].div.span.text.strip()
        if brewery:
            output['brewery'] = brewery.text.strip()
            output['brewery_url'] = brewery['href']
        if brewed_at:
            output['brewed_at'] = brewed_at.text.strip()
            output['brewed_at_url'] = brewed_at['href']
        if style:
            output['style'] = style.text.strip()
        if 'No commercial description' not in description.text:
            [s.extract() for s in description('small')]
            output['description'] = ' '.join([s for s in description.strings]).strip()
        return output

    def reviews(self, url, pages=1, start_page=1, review_order="most recent"):
        """Returns reviews for a specific beer.

        Args:
            url (string): The specific url of the beer. Looks like:
                "/beer/deschutes-inversion-ipa/55610/"
            pages (int): Number of pages to return. Must be > 0.
            start_page (int): Which page to begin results. Must be > 0.
            review_order (string): How to sort reviews. Three inputs:
                most recent: Newer reviews appear earlier.
                top raters: RateBeer.com top raters appear earlier.
                highest score: Reviews with the highest overall score appear
                earlier.

        Returns:
            A list of dictionaries, containing the information about the review.
        """
        assert pages > 0, "``pages`` must be greater than 0"
        assert start_page > 0, "``start_page`` must be greater than 0"
        review_order = review_order.lower()
        url_codes = {
            "most recent": 1,
            "top raters": 2,
            "highest score": 3
        }
        url_flag = url_codes.get(review_order)
        if url_flag is None:
            raise ValueError("Invalid ``review_order``.")

        output = []
        for page_number in range(start_page, start_page + pages):
            complete_url = "{0}{1}/{2}/".format(url, url_flag, page_number)
            soup = self._get_soup(complete_url)
            content = soup.find('div', id='container').find('table').find_all('tr')[5]
            _ = [x.extract() for x in content.find_all('table')]  # strip ad section
            review_tuples = zip(*[iter(content.find_all('div'))] * 4)  # basically magic

            for review in review_tuples:
                detail_tuples = zip(*[iter(review[0].find_all(["big", "small"]))] * 2)
                details = dict([(
                    label.text.lower().strip().encode("ascii", "ignore"),
                    rating.text,
                ) for (label, rating) in detail_tuples])

                details.update({'text': review[3].text})
                output.append(details)
        return output

    def brewery(self, url, include_beers=True):
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

        soup = self._get_soup(url)
        try:
            s_contents = soup.find('div', id='container').find('table').find_all('tr')[0].find_all('td')
        except AttributeError:
            raise RateBeer.PageNotFound(url)

        output = {
            'name': s_contents[8].h1.text,
            'type': re.search(r"Type: +(?P<type>[^ ]+)",
                              s_contents[8].find_all('span', 'beerfoot')[1].text).group('type'),
            'street': _find_span(s_contents[0], 'streetAddress'),
            'city': _find_span(s_contents[0], 'addressLocality'),
            'state': _find_span(s_contents[0], 'addressRegion'),
            'country': _find_span(s_contents[0], 'addressCountry'),
            'postal_code': _find_span(s_contents[0], 'postalCode'),
        }

        if include_beers:
            output.update({'beers': []})
            s_beer_trs = iter(s_contents[8].find('table', 'maintable nohover').find_all('tr'))
            next(s_beer_trs)
            for row in s_beer_trs:
                if len(row.find_all('td')) > 1:
                    beer = {
                        'name': row.a.text,
                        'url': row.a.get('href'),
                        'id': re.search(r"/(?P<id>\d*)/", row.a.get('href')).group('id'),
                        'rating': row.find_all('td')[4].text.strip(),
                        'num_ratings': row.find_all('td')[6].text.strip(),
                    }
                    output['beers'].append(beer)
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
                'rating': data[4].text
            })
        return output
