ratebeer.py
===========

Changes
-------

Note that the nature of web scraping means this will be in **perpetual beta.**

###v1.2

* Everything conforms to PEP8 now. Thanks to the fine folks [here](http://codereview.stackexchange.com/questions/69909/ratebeer-com-scraper).
* Minor refactoring.

###v1.1

* Added ``reviews``.
* Better exceptions (no more ``LookupError`` for 404s)

### v1.0

* Initial release.


What is this?
-------------

[RateBeer](http://www.ratebeer.com/) is a database of user-created reviews about beers and breweries. However, their API has been down for some time, making it difficult to get that information programmatically. This simplifies that process, allowing you to access it in the most painless way possible. Data is returned to you in a friendly, Pythonic way:

    {'beers': [{'id': '61118',
            'name': u'21st Amendment Summit IPA',
            'num_ratings': u'4',
            'rating': u'',
            'url': '/beer/21st-amendment-summit-ipa/61118/'},
             {'id': '258783',
              'name': u'4T\x92s Summit Hoppy',
              'num_ratings': u'1',
              'rating': u'',
              'url': '/beer/4ts-summit-hoppy/258783/'},
             ....
             {'id': '170187',
              'name': u'Maumee Bay Summit Street Pale Ale',
              'num_ratings': u'3',
              'rating': u'',
              'url': '/beer/maumee-bay-summit-street-pale-ale/170187/'
            }],
      'breweries': [{'id': '1233',
                'location': u'St. Paul, Minnesota',
                'name': [u'Summit Brewing Company'],
                'url': '/brewers/summit-brewing-company/1233/'},
               ...
               {'id': '346',
                'location': u'Gaithersburg, Maryland',
                'name': [u'Summit Station Restaurant & Brewery'],
                'url': '/brewers/summit-station-restaurant-brewery/346/'}
              ]
      }


Why not BeerAdvocate.com?
-------------------------

Because they're evil, and they issue takedown notices left and right.


Requirements
------------

Requires [Requests](http://docs.python-requests.org/en/latest/) and [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) with `lxml`.


Installation
------------
Use `pip`:

    pip install ratebeer

Or clone the package:

    git clone https://github.com/alilja/ratebeer.git


Usage
-----
Because `ratebeer` doesn't use the API, no key is required. Simply:

```python
from ratebeer import RateBeer

RateBeer().search("summit extra pale ale")
```
### Methods
* `search` -- A generic search. A dictionary with two keys: `beers` and `breweries`. Each of those contains a list of dictionaries.

<pre><code>
    >>> rb = RateBeer()
    >>> rb.search("summit extra pale ale")
    {'beers': [{'name': [u'Summit Extra Pale Ale'],
            'num_ratings': <td align="right">678</td>,
            'rating': <td align="right">73  </td>,
            'url': u'/beer/summit-extra-pale-ale/7344/'}],
    'breweries': []}
</code></pre>

* `beer` -- Returns information about that beer. Now if we were using an API, you'd use an `id` of some variety. Unfortunately, scraping makes things a little more challenging, so as a UUID here, we're using the `url` of the beer.

<pre><code>
    >>> rb.beer("/beer/new-belgium-tour-de-fall/279122/")
    {'abv': u'6%',
     'brewery': u'New Belgium Brewing Company',
     'brewery_url': '/brewers/new-belgium-brewing-company/77/',
     'calories': u'180',
     'ibu': u'38',
     'name': u'New Belgium Tour de Fall',
     'num_ratings': u'209',
     'overall_rating': u'81',
     'style': u'American Pale Ale',
     'style_rating': u'78'}
 </code></pre>

* `brewery` -- Returns information about the brewery. Takes a `url`, and can include a flag to disable returning the list of beers from that brewery.

<pre><code>
    >>> rb.brewery("/brewers/deschutes-brewery/233/")
    {'city': u'Bend',
     'country': u'USA',
     'name': u'Deschutes Brewery',
     'postal_code': u'97702',
     'state': u'Oregon',
     'street': u'901 SW Simpson Ave',
     'type': u'Microbrewery',
     'beers': [{'id': '282308',
                'name': u'Deschutes (Dry-Hopped) Table Beer',
                'num_ratings': u'1',
                'rating': u'',
                'url': '/beer/deschutes-dry-hopped-table-beer/282308/'},
                ...
               {'id': '180887',
                'name': u'Deschutes Zymerge (Low Gluten Beer)',
                'num_ratings': u'2',
                'rating': u'',
                'url': '/beer/deschutes-zymerge-low-gluten-beer/180887/'}]}

    >>> rb.brewery("/brewers/summit-brewing-company/1233/",include_beers=False)
    {'city': u'St. Paul',
     'country': u'USA',
     'name': u'Summit Brewing Company',
     'postal_code': u'55102',
     'state': u'Minnesota',
     'street': u'910 Montreal Circle',
     'type': u'Microbrewery'}
</code></pre>

* `reviews` -- Returns a list of dictionaries containing reviews. Requires a `url`, can also take `start_page`, `pages`, or `review_order` ("most recent", "top raters", "highest score"):

<pre><code>
    >>> rb.reviews("/beer/deschutes-inversion-ipa/55610/")
    [{'appearance': u'4/5',
      'aroma': u'7/10',
      'overall': u'15/20',
      'palate': u'3/5',
      'taste': u'8/10',
      'text': u'Pours copper with a thick off white head that leaves nice lacing in the glass. Aroma is malt and grapefruit. Has medium carbonation the mouth with a bit of a bitter kick on the back end. Good grapefruit bitterness and a tad sweet and malty. This a nice IPA. '},
      ...
     {'appearance': u'4/5',
      'aroma': u'7/10',
      'overall': u'15/20',
      'palate': u'3/5',
      'taste': u'7/10',
      'text': u'Tasted from bottle. Pours a nice copper color with tan head. Good lacing. Aroma of floral notes, caramel and some toasted malt. Taste is pretty well balanced and sweeter than most IPAs. Caramel, toffee, brown auger malt backbone give it moderate sweetness with some pine and floral flavors giving it a clean consistent moderate bitterness. Above average IPA. \n\n---Rated via Beer Buddy for iPhone '}]
</code></pre>

<pre><code>
    >>> rb.reviews("/beer/deschutes-inversion-ipa/55610/", start_page=2, pages=10)
    [{'appearance': u'4/5',
      'aroma': u'7/10',
      'overall': u'15/20',
      'palate': u'4/5',
      'taste': u'6/10',
      'text': u'Pours a brownish amber color with a nice off-white 1 finger head. Aroma of Citrus, pine, caramel, and malt. Orange flavor up front with a nice bitter sweetness, bit of caramel and grapefruit. '},
     ...
     {'appearance': u'5/5',
      'aroma': u'7/10',
      'overall': u'14/20',
      'palate': u'4/5',
      'taste': u'7/10',
      'text': u'Bottle pour at the Deschutes tasting. Pours a clear amber with a beige head of foam. The aroma is citrussy ang grassy. Taste is fairly bitter with complex layers of tea, earth, citrus, and herbs coming across in waves of bitterness. Medium bodied with medium carbonation. Decent IPA. '}]
</code></pre>

* `beer_style_list` -- Returns a dictionary containing the beer style name and a link to that page.

<pre><code>
    >>> rb.beer_style_list()
    {u'Abbey Dubbel': '/beerstyles/abbey-dubbel/71/',
     ...
     u'Zwickel/Keller/Landbier': '/beerstyles/zwickel-keller-landbier/74/'}
</code></pre>


Tests
-----
`ratebeer` uses the standard Python unit testing library.


License
-------

**Author**: Andrew Lilja

All code released under [the Unlicense](http://unlicense.org/) (a.k.a. Public
Domain).