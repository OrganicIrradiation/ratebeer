import re
from datetime import datetime

from bs4 import BeautifulSoup

import rb_exceptions
from ratebeer import RateBeer


class Beer(object):
    def __init__(self, soup, url):
        """The Beer object. Contains information about an individual beer.

        Args:
            soup (Soup): the BeautifulSoup object for the beer page.

        """
        # check for 404s
        try:
            soup_rows = soup.find('div', id='container').find('table').find_all('tr')
        except AttributeError:
            raise rb_exceptions.PageNotFound(url)
        # ratebeer pages don't actually 404, they just send you to this weird
        # "beer reference" page but the url doesn't actually change, it just
        # seems like it's all getting done server side -- so we have to look
        # for the contents h1 to see if we're looking at the beer reference or
        # not
        if "beer reference" in soup_rows[0].find_all('td')[1].h1.contents:
            raise rb_exceptions.PageNotFound(url)

        if "Also known as " in soup_rows[1].find_all('td')[1].div.div.contents:
            raise rb_exceptions.AliasedBeer(url, soup_rows[1].find_all('td')[1].div.div.a['href'])

        # get beer meta information
        # grab the html and split it into a keyword and value
        brew_info_html = soup_rows[1].find_all('td')[1].div.small
        brew_info = [s.split(': ') for s in brew_info_html.text.split(u'\xa0\xa0')]
        keyword_lookup = {
            "RATINGS": "num_ratings",
            "MEAN": "mean",
            "WEIGHTED AVG": "weighted_avg",
            "SEASONAL": "seasonal",
            "CALORIES": "calories",
            "EST. CALORIES": "calories",
            "ABV": "abv",
            "IBU": "ibu",
        }
        # match the data pulled from the brew info and match it to they keyword
        # in the lookup table
        self.meta = {}
        for meta_name, meta_data in brew_info:
            match = keyword_lookup.get(meta_name.strip())
            if match == "mean":
                meta_data = meta_data[:meta_data.find("/")]
            elif match == "abv":
                meta_data = meta_data[:-1]
            elif not match:
                continue
            # convert to float if possible
            try:
                meta_data = float(meta_data)
            except ValueError:
                pass
            self.meta[match] = meta_data

        info = soup_rows[1].tr.find_all('td')

        # get basic brewery information
        brewery_info = info[1].find('div').contents
        brewery = brewery_info[0].findAll('a')[0]
        brewed_at = None
        if 'brewed at' in brewery_info[0].text.lower():
            brewed_at = brewery_info[0].findAll('a')[0]
        if brewery:
            self.brewery = brewery.text.strip()
            self.brewery_url = brewery.get('href')
        if brewed_at:
            self.brewed_at = brewed_at.text.strip()
            self.brewed_at_url = brewed_at.get('href')

        # get ratings
        ratings = info[0].findAll('div')
        if len(ratings) > 1:
            overall_rating = ratings[1].findAll('span')
            style_rating = ratings[3].findAll('span')
        else:
            overall_rating = None
            style_rating = None
        if overall_rating and overall_rating[1].text != 'n/a':
            self.overall_rating = int(overall_rating[1].text)
        if style_rating and style_rating[0].text != 'n/a':
            self.style_rating = int(style_rating[0].text)

        # get the beer style
        if brewery_info[3]:
            self.style = brewery_info[3].text.strip()

        # get the beer description
        description = soup_rows[1].find_all('td')[1].find(
            'div',
            style=(
                'border: 1px solid #e0e0e0; background: #fff; '
                'padding: 14px; color: #777;'
            )
        )
        if 'no commercial description' not in description.text.lower():
            # strip ads
            _ = [s.extract() for s in description('small')]
            self.description = ' '.join([s for s in description.strings]).strip()

        # get url
        self.url = soup.find('link', rel='canonical')['href'].replace(RateBeer._BASE_URL, '')

        # get name
        self.name = soup_rows[0].find_all('td')[1].h1.text.strip()

    def __str__(self):
        return self.name

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
            soup = RateBeer._get_soup(complete_url)
            content = soup.find('table', style='padding: 10px;').tr.td
            reviews = content.find_all('div', style='padding: 0px 0px 0px 0px;')
            if len(reviews) < 1:
                raise StopIteration

            for review_soup in reviews:
                yield Review(review_soup, complete_url)

            page_number += 1


class Review(object):
    def __init__(self, review_soup, url):
        # get ratings
        # gets every second entry in a list
        raw_ratings = zip(*[iter(review_soup.find('strong').find_all(["big", "small"]))] * 2)
        # strip html and everything else
        for (label, rating) in raw_ratings:
            setattr(
                self,
                label.text.lower().strip().encode("ascii", "ignore"),
                rating.text
            )
        self.rating = float(review_soup.find_all('div')[1].text)

        # get user information
        userinfo = review_soup.next_sibling
        self.text = userinfo.next_sibling.next_sibling.text.strip().encode("ascii", "ignore")
        self.user_name = re.findall(r'(.*?)\xa0\(\d*?\)', userinfo.a.text)[0]
        self.user_location = re.findall(r'-\s(.*?)\s-', userinfo.a.next_sibling)[0]

        # get date it was posted
        date = re.findall(r'-\s.*?\s-\s(.*)', userinfo.a.next_sibling)[0]
        self.date = datetime.strptime(date.strip(), '%b %d, %Y').date()

    def __str__(self):
        return self.text

class Brewery(object):
    def __init__(self, url):
        """Returns information about a specific brewery.

        Args:
            url (string): The specific url of the beer. Looks like:
                "/brewers/new-belgium-brewing-company/77/"

        Returns:
            A dictionary of attributes about that brewery."""

        soup = RateBeer._get_soup(url)
        try:
            s_contents = soup.find('div', id='container').find('table').find_all('tr')[0].find_all('td')
        except AttributeError:
            raise rb_exceptions.PageNotFound(url)

        self.name = soup.h1.text
        self.url = url
        self.type = re.findall(r'Type: (.*?)<br\/>', soup.renderContents())[0]
        self.street = Brewery._find_span(s_contents[0], 'streetAddress')
        self.city = Brewery._find_span(s_contents[0], 'addressLocality')
        self.state = Brewery._find_span(s_contents[0], 'addressRegion')
        self.country = Brewery._find_span(s_contents[0], 'addressCountry')
        self.postal_code = Brewery._find_span(s_contents[0], 'postalCode')

    @staticmethod
    def _find_span(search_soup, item_prop):
        output = search_soup.find('span', attrs={'itemprop': item_prop})
        output = output.text if output else None
        return output

    def get_beers(self):
        page_number = 1
        while True:
            complete_url = '{0}0/{1}/'.format(self.url, page_number)
            soup = RateBeer._get_soup(complete_url)
            soup_beer_rows = soup.find('table', 'maintable nohover').findAll('tr')

            if len(soup_beer_rows) < 2:
                raise StopIteration

            for row in soup_beer_rows[1:]:
                url = row.a.get('href')
                # sometimes the beer is listed but it doesn't have a page
                # ignore it for now
                try:
                    beer = Beer(RateBeer._get_soup(url), url)
                except rb_exceptions.PageNotFound:
                    continue
                yield beer

            page_number += 1
