ratebeer.py
===========

What is this?
-------------

[RateBeer](http://www.ratebeer.com/) is a database of user-created reviews about beers and breweries. However, their API has been down for some time, making it difficult to get that information programmatically. This simplifies that process, allowing you to access it in the most painless way possible. Data is returned to you in a friendly, Pythonic way:

```python
>>> from ratebeer import RateBeer
>>> rb = RateBeer()
>>> rb.search('Summit')
{'beers': [{'id': 61118,
            'name': u'21st Amendment Summit IPA',
            'num_ratings': 4,
            'url': '/beer/21st-amendment-summit-ipa/61118/'},
            ...
           {'id': 227196,
            'name': u'Loch Lomond Southern Summit',
            'num_ratings': 14,
            'overall_rating': 69,
            'url': '/beer/loch-lomond-southern-summit/227196/'}],
'breweries': [{'id': 1233,
            'location': u'St. Paul, Minnesota',
            'name': u'Summit Brewing Company',
            'url': '/brewers/summit-brewing-company/1233/'},
            ...
           {'id': 346,
            'location': u'Gaithersburg, Maryland',
            'name': u'Summit Station Restaurant & Brewery',
            'url': '/brewers/summit-station-restaurant-brewery/346/'}]}
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

### ``RateBeer`` Class

**Methods**

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

* `get_beer` -- Returns a Beer object containing information about the beer. See the ``Beer`` section below. You can replicate the ``RateBeer.beer`` functionality by using ``get_beer().__dict__``.

* `beer` -- Returns information about that beer. Now if we were using an API, you'd use an `id` of some variety. Unfortunately, scraping makes things a little more challenging, so as a UUID here, we're using the `url` of the beer.

```python
>>> rb.beer("/beer/new-belgium-tour-de-fall/279122/")
{'brewery': u'New Belgium Brewing Company',
 'brewery_url': '/brewers/new-belgium-brewing-company/77/',
 'description': u'New Belgium\x92s love for beer, bikes and benefits is best described by being at Tour de Fat. Our love for Cascade and Amarillo hops is best tasted in our Tour de Fall Pale Ale. We\x92re cruising both across the country during our favorite time of year. Hop on and find Tour de Fall Pale Ale in fall 2014.',
 'meta': {'abv': 6.0,
          'calories': 180.0,
          'ibu': 38.0,
          'num_ratings': 254.0,
          'seasonal': u'Autumn',
          'weighted_avg': 3.33},
 'name': u'New Belgium Tour de Fall',
 'overall_rating': 80,
 'style': u'American Pale Ale',
 'style_rating': 78,
 'url': '/beer/new-belgium-tour-de-fall/279122/'}
```

* `get_brewery` -- Returns a Brewery object containing information about that brewery. See the ``Brewery`` section below. You can replicate the ``RateBeer.brewery`` functionality by using ``get_brewery().__dict__``.

* `brewery` -- Returns information about the brewery. Includes a 'beer' generator that provides information about the brewery's beers.

```python
>>> brewery = rb.brewery("/brewers/deschutes-brewery/233/")
>>> print brewery
{'city': u'Bend',
 'country': u'USA',
 'name': u'Deschutes Brewery',
 'postal_code': u'97702',
 'state': u'Oregon',
 'street': u'901 SW Simpson Ave',
 'type': 'Microbrewery',
 'url': '/brewers/deschutes-brewery/233/'}
```

* `beer_style_list` -- Returns a dictionary containing the beer style name and a link to that page.

```python
>>> rb.beer_style_list()
{u'Abbey Dubbel': '/beerstyles/abbey-dubbel/71/',
 ...
 u'Zwickel/Keller/Landbier': '/beerstyles/zwickel-keller-landbier/74/'}
```

* `beer_style` -- Returns a generator of ``Beer`` objects from the beer style page. Takes a `url` to a beer style and an optional `sort_type`: `overall` returns the highest-rated beers (default behavior) and `trending` returns, well, the trending beers.

```python
>>> rb.beer_style("/beerstyles/abbey-dubbel/71/")
```

### ``Beer`` Class

``Beer`` requires the url of the beer you're looking for, like ``RateBeer.beer`` and ``RateBeer.get_beer``.

**Attributes**

* ``abv`` (float): percentage alcohol*
* ``brewery`` (string): the name of the beer's brewery
* ``brewery_url`` (string): that brewery's url
* ``calories`` (float): estimated calories for the beer*
* ``description`` (string): the beer's description
* ``mean_rating`` (float): the mean rating for the beer (out of 5)*
* ``name`` (string): the full name of the beer (may include the brewery name)
* ``num_ratings`` (int): the number of reviews*
* ``overall_rating`` (int): the overall rating (out of 100)
* ``seasonal`` (string): which season the beer is produced in. Acts as a catch-all for any kind of miscellanious brew information.*
* ``style`` (string): beer style
* ``style_rating`` (int): rating of the beer within its style (out of 100)
* ``url`` (string): the beer's url
* ``weighted_avg`` (float): the beer rating average, weighted using some unknown algorithm (out of 5)*

\* may not be available for all beers

**Methods**

* ``get_reviews`` -- Returns a generator of ``Review`` objects for all the reviews in the beer. Takes a ``review_order`` argument, which can be "most recent", "top raters", or "highest score".


### ``Review`` Class

``Review`` returns a datatype that contains information about a specific review. For efficiency reasons, it requires the soup of the individual review. Probably best to not try to make one yourself: use ``beer.get_reviews`` instead.

**Attributes**

* ``appearance`` (int): rating for appearance (out of 5)
* ``aroma`` (int): aroma rating (out of 10)
* ``date`` (datetime): review date
* ``overall`` (int): overall rating (out of 20, for some reason)
* ``palate`` (int): palate rating (out of 5)
* ``rating`` (float): another overall rating provided in the review. Not sure how this different from ``overall``.
* ``text`` (string): actual text of the review.
* ``user_location`` (string): writer's location
* ``user_name`` (string): writer's username


### ``Brewery`` Class

``Brewery`` requires the url of the brewery you want information on.

**Attributes**

* ``city`` (string): the brewery's city
* ``country`` (string): the brewery's country
* ``name`` (string): the brewery's name
* ``postal_code`` (string): the brewery's postal code
* ``state`` (string): the brewery's state/municipality/province.
* ``street`` (string): the street address of the brewery.
* ``type`` (string): the type of brewery. Typically "microbrewery" or "macrobrewery".
* ``url`` (string): the url of the brewery

**Methods**

* ``get_beers`` -- Returns a generator of ``Beer`` objects for every beer produced by the brewery. Some brewery pages list beers that are produced by do not have any pages, ratings, or information besides a name. For now, these beers are omitted from the results.

Tests
-----
`ratebeer` uses the standard Python unit testing library.


Changes
-------

Note that the nature of web scraping means this will be in **perpetual beta.**

###v2.0

Major changes.

* New ``Beer``, ``Review``, and ``Brewery`` classes.
* Substantial overhaul in ``ratebeer.py``, addition of new files including separation of responsibilities
* New generator functions in new classes.

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
