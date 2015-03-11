ratebeer.py
===========

What is this?
-------------

[RateBeer](http://www.ratebeer.com/) is a database of user-created reviews about beers and breweries. However, their API has been down for some time, making it difficult to get that information programmatically. This simplifies that process, allowing you to access it in the most painless way possible. Data is returned to you in a friendly, Pythonic way:

```python
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
```


Why not BeerAdvocate.com?
-------------------------

Because they're evil, and they issue takedown notices left and right. We like RateBeer. Scratch that, we **love** RateBeer.


Requirements
------------

Requires [requests](https://pypi.python.org/pypi/requests), [beautifulsoup4](https://pypi.python.org/pypi/beautifulsoup4/4.3.2), and [lxml](https://pypi.python.org/pypi/lxml/3.4.1).


Installation
------------
Use `pip`:

    pip install ratebeer

Or clone the package:

    git clone https://github.com/alilja/ratebeer.git


Usage
-----
Because `ratebeer` doesn't use an API, no key is required. Simply:

```python
from ratebeer import RateBeer

RateBeer().search("summit extra pale ale")
```

### Methods
* `search` -- A generic search. A dictionary with two keys: `beers` and `breweries`. Each of those contains a list of dictionaries.

```python
>>> rb = RateBeer()
>>> rb.search("summit extra pale ale")
{'beers': [{'id': 7344,
  'name': u'Summit Extra Pale Ale',
  'num_ratings': 682,
  'overall_rating': 72,
  'url': '/beer/summit-extra-pale-ale/7344/'},
  {'id': 317841,
  'name': u'Summit Extra Pale Ale - Rose Petals',
  'num_ratings': 2,
  'url': '/beer/summit-extra-pale-ale--rose-petals/317841/'}],
  'breweries': []}
```

* `beer` -- Returns information about that beer. Now if we were using an API, you'd use an `id` of some variety. Unfortunately, scraping makes things a little more challenging, so as a UUID here, we're using the `url` of the beer.

```python
>>> rb.beer("/beer/new-belgium-tour-de-fall/279122/")
{'abv': 6.0,
  'brewery': u'New Belgium Brewing Company',
  'brewery_country': u'USA',
  'brewery_url': '/brewers/new-belgium-brewing-company/77/',
  'calories': 180.0,
  'description': u'New Belgium\x92s love for beer, bikes and benefits is best described by being at Tour de Fat. Our love for Cascade and Amarillo hops is best tasted in our Tour de Fall Pale Ale. We\x92re cruising both across the country during our favorite time of year. Hop on and find Tour de Fall Pale Ale in fall 2014.',
  'ibu': 38.0,
  'name': u'New Belgium Tour de Fall',
  'num_ratings': 254.0,
  'overall_rating': 80,
  'seasonal': u'Autumn',
  'style': u'American Pale Ale',
  'style_rating': 78,
  'url': '/beer/new-belgium-tour-de-fall/279122/',
  'weighted_avg': 3.33}
```

* `brewery` -- Returns information about the brewery. Includes a generator that provides information about the breweries beers, even if they span multiple pages

```python
>>> brewery = rb.brewery("/brewers/deschutes-brewery/233/")
>>> print brewery
{'beers': <generator object __beers at 0x10ce0d730>,
 'city': u'Bend',
 'country': u'USA',
 'name': u'Deschutes Brewery',
 'postal_code': u'97702',
 'state': u'Oregon',
 'street': u'901 SW Simpson Ave',
 'type': 'Microbrewery',
 'url': '/brewers/deschutes-brewery/233/',
 'url_name': 'deschutes-brewery'}
>>> brewery['beers'].next()
{'abv': 6.5,
 'brewery': u'Deschutes Brewery',
 'brewery_url': '/brewers/deschutes-brewery/233/',
 'id': 176946,
 'name': u'Deschutes / Hopworks India Red Lager',
 'num_ratings': 12,
 'overall_rating': 85,
 'style_rating': 99,
 'url': '/beer/deschutes--hopworks-india-red-lager/176946/',
 'weighted_avg': 3.37}
```

* `reviews` -- Returns a generator of dictionaries containing reviews. Requires a `url`, can also take `review_order` ("most recent", "top raters", "highest score"):

```python
>>> reviews = rb.reviews("/beer/alchemist-heady-topper/32329/1/118/")
>>> reviews.next()
{'appearance': u'3/5',
 'aroma': u'9/10',
 'date': datetime.date(2010, 9, 26),
 'overall': u'19/20',
 'palate': u'3/5',
 'rating': 4.3,
 'taste': u'9/10',
 'text': u'...',
 'user_location': u'Montreal, Quebec, CANADA',
 'user_name': u'MJGG'}
```

* `beer_style_list` -- Returns a dictionary containing the beer style name and a link to that page.

```python
>>> rb.beer_style_list()
{u'Abbey Dubbel': '/beerstyles/abbey-dubbel/71/',
 ...
 u'Zwickel/Keller/Landbier': '/beerstyles/zwickel-keller-landbier/74/'}
```

* `beer_style` -- A list of dictionaries containing beers from the beer style page. Takes a `url` to a beer style and an optional `sort_type`: `overall` returns the highest-rated beers (default behavior) and `trending` returns, well, the trending beers.

```python
>>> rb.beer_style("/beerstyles/abbey-dubbel/71/")
[{'name': u'St. Bernardus Prior 8',
  'rating': 3.85,
  'url': '/beer/st-bernardus-prior-8/2531/'},
 {'name': u'Westmalle Dubbel',
  'rating': 3.84,
  'url': '/beer/westmalle-dubbel/2205/'},
   ...
 {'name': u'Chama River Demolition Dubbel',
  'rating': 3.46,
  'url': '/beer/chama-river-demolition-dubbel/33903/'}]
```


Tests
-----
`ratebeer` uses the standard Python unit testing library.


Changes
-------

Note that the nature of web scraping means this will be in **perpetual beta.**

###v1.4

* ``reviews`` is now a generator.

###v1.3.5

* Several improvements to results, particularly for edge cases and situations where search results are not in the expected order.

###v1.3.4

* Metadata for beers returns floats when appropriate.

###v1.3.3

* Captures more meta data.
* Plays better with foreign beers.
* Now if information is missing from a beer entry, its key is not added to the ``beer`` output.

###v1.3.2

* Captures aliases for beer names.

###v1.3

* Added ``beer_style_list`` and ``beer_style``.

###v1.2

* Everything conforms to PEP8 now. Thanks to the fine folks [here](http://codereview.stackexchange.com/questions/69909/ratebeer-com-scraper).
* Minor refactoring.

###v1.1

* Added ``reviews``.
* Better exceptions (no more ``LookupError`` for 404s)

### v1.0

* Initial release.


License
-------

**Creator**: Andrew Lilja

**Contributor**: Steven A. Cholewiak

All code released under [the Unlicense](http://unlicense.org/) (a.k.a. Public Domain).
