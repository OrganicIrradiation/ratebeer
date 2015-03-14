from exceptions import AliasedBeer, PageNotFound

class Beer(object):
    def __init__(self, soup):
        """The Beer object. Contains information about an individual beer.

        Args:
            soup (Soup): the BeautifulSoup object for the beer page.

        """

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
        if "beer reference" in s_contents_rows[0].find_all('td')[1].h1.contents.lower():
            raise RateBeer.PageNotFound(url)

        if "also known as " in s_contents_rows[1].find_all('td')[1].div.div.contents.lower():
            raise RateBeer.AliasedBeer(url, s_contents_rows[1].find_all('td')[1].div.div.a['href'])

        brew_info_row = s_contents_rows[1].find_all('td')[1].div.small
        brew_info = brew_info_row.text.split(u'\xa0\xa0')
        brew_info = [s.split(': ') for s in brew_info]
        print("Brew Info")
        keywords = {
            "RATINGS": "num_ratings",
            "MEAN": "mean",
            "WEIGHTED AVG": "weighted_avg",
            "SEASONAL": "seasonal",
            "CALORIES": "calories",
            "ABV": "abv",
            "IBU": "ibu",
        }
        self.meta = {}
        for meta_name, meta_data in brew_info:
            for keyword in keywords:
                if keyword in meta_name and meta_data:
                    if keyword == "MEAN":
                        meta_data = meta_data[:meta_data.find("/")]
                    if keyword == "ABV":
                        meta_data = meta_data[:-1]
                    try:
                        meta_data = float(meta_data)
                    except ValueError:
                        pass
                    self.meta[keywords[keyword]] = meta_data
                    break

        info = s_contents_rows[1].tr.find_all('td')

        brewery_info = info[1].find('div').contents
        brewery = brewery_info[0].findAll('a')[0]
        brewed_at = None
        if 'brewed at' in brewery_info[0].text.lower():
            brewed_at = brewery_info[0].findAll('a')[1]

        style = brewery_info[3]

        if ',' in brewery_info[5]:
            # Non-USA addresses
            brewery_country = brewery_info[5].split(',')[1]
        else:
            # USA addresses
            brewery_country = brewery_info[8]

        description = s_contents_rows[1].find_all('td')[1].find(
            'div', style=(
                'border: 1px solid #e0e0e0; background: #fff; '
                'padding: 14px; color: #777;'
            )
        )

        name = s_contents_rows[0].find_all('td')[1].h1
        ratings = info[0].findAll('div')
        if len(ratings) > 1:
            overall_rating = ratings[1].findAll('span')
            style_rating = ratings[3].findAll('span')
        else:
            overall_rating = None
            style_rating = None

        if overall_rating and overall_rating[1].text != 'n/a':
            output['overall_rating'] = int(overall_rating[1].text)
        if style_rating and style_rating[0].text != 'n/a':
            output['style_rating'] = int(style_rating[0].text)
        if brewery:
            output['brewery'] = brewery.text.strip()
            output['brewery_url'] = brewery.get('href')
        if brewed_at:
            output['brewed_at'] = brewed_at.text.strip()
            output['brewed_at_url'] = brewed_at.get('href')
        if style:
            output['style'] = style.text.strip()
        if brewery_country:
            output['brewery_country'] = brewery_country.strip()
        if 'No commercial description' not in description.text:
            _ = [s.extract() for s in description('small')]
            output['description'] = ' '.join([s for s in description.strings]).strip()

        self.url = soup.find('link', rel='canonical')['href'].replace(RateBeer._BASE_URL, '')
        self.name = name.text.strip()

