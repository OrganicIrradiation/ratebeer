import exceptions

class Beer(object):
    def __init__(self, soup):
        """The Beer object. Contains information about an individual beer.

        Args:
            soup (Soup): the BeautifulSoup object for the beer page.

        """
        # check for 404s
        try:
            soup_rows = soup.find('div', id='container').find('table').find_all('tr')
        except AttributeError:
            raise Exceptions.PageNotFound(url)
        # ratebeer pages don't actually 404, they just send you to this weird
        # "beer reference" page but the url doesn't actually change, it just
        # seems like it's all getting done server side -- so we have to look
        # for the contents h1 to see if we're looking at the beer reference or
        # not
        if "beer reference" in soup_rows[0].find_all('td')[1].h1.contents:
            raise Exceptions.PageNotFound(url)

        if "Also known as " in soup_rows[1].find_all('td')[1].div.div.contents:
            raise Exceptions.AliasedBeer(url, soup_rows[1].find_all('td')[1].div.div.a['href'])

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
            brewed_at = brewery_info[0].findAll('a')[1]
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
        self.url = soup.find('link', rel='canonical')['href']

        # get name
        self.name = soup_rows[0].find_all('td')[1].h1.text.strip()

    def __str__(self):
        return self.name
