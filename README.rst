ratebeer.py
===========

What is this?
-------------

`RateBeer <http://www.ratebeer.com/>`__ is a database of user-created
reviews about beers and breweries. However, their API has been down for
some time, making it difficult to get that information programmatically.
This simplifies that process, allowing you to access it in the most
painless way possible. Data is returned to you in a friendly, Pythonic
way:

.. code:: python

    >>> import ratebeer
    >>> rb = ratebeer.RateBeer()
    >>> rb.search('Summit')
    {'beers': [<Beer('/beer/21st-amendment-summit-ipa/61118/')>,
               <Beer('/beer/4ts-summit-hoppy/258783/')>,
               ...
               <Beer('/beer/lander-summit-ipa/148623/')>,
               <Beer('/beer/le-cheval-blanc-summit-ipa/125100/')>],
     'breweries': [<Brewery('/brewers/sound-to-summit-brewing/22497/')>,
                   <Brewery('/brewers/summit-brewing-company/1233/')>,
                   ...
                   <Brewery('/brewers/summit-hard-cider-and-perry/18260/')>,
                   <Brewery('/brewers/summit-station-restaurant-brewery/346/')>]}

Why not BeerAdvocate.com?
-------------------------

Because they're evil, and they issue takedown notices left and right. We
like RateBeer. Scratch that, we **love** RateBeer.

Requirements
------------

Requires `requests[security] <https://pypi.python.org/pypi/requests>`__,
`beautifulsoup4 <https://pypi.python.org/pypi/beautifulsoup4/4.3.2>`__,
and `lxml <https://pypi.python.org/pypi/lxml/3.4.1>`__.

Installation
------------

Use ``pip``:

::

    pip install ratebeer

Or clone the package:

::

    git clone https://github.com/alilja/ratebeer.git

Usage
-----

Because ``ratebeer.py`` does not use an API, since one is not provided,
no key is required. Simply:

.. code:: python

    >>> import ratebeer
    >>> rb = ratebeer.RateBeer()
    >>> rb.search("summit extra pale ale")

``RateBeer`` Class
~~~~~~~~~~~~~~~~~~

**Methods**

-  ``get_beer`` -- Pass in the URL for a beer page and this function
   will return a ``Beer`` object containing information about the beer.
   In addition the the URL, it accepts an optional ``fetch`` argument
   (default: False), which can be set to true to immediately download
   the object's attributes. See the ``Beer`` class below. You can
   replicate the ``RateBeer.beer(URL)`` functionality using
   ``RateBeer.get_beer(URL, True).__dict__``.

-  ``beer`` -- Returns a dictionary with information about that beer.

.. code:: python

    >>> rb.beer("/beer/new-belgium-tour-de-fall/279122/")
    {'_has_fetched': True,
     'abv': 6.0,
     'brewery': 'New Belgium Brewing Company',
     'brewery_country': 'USA',
     'brewery_url': '/brewers/new-belgium-brewing-company/77/',
     'calories': 180.0,
     'description': 'New Belgium\x92s love for beer, bikes and benefits is best described by being at Tour de Fat. Our love for Cascade and Amarillo hops is best tasted in our Tour de Fall Pale Ale. We\x92re cruising both across the country during our favorite time of year. Hop on and find Tour de Fall Pale Ale in fall 2014.',
     'ibu': 38.0,
     'name': 'New Belgium Tour de Fall',
     'num_ratings': 257,
     'overall_rating': 77,
     'seasonal': 'Autumn',
     'style': 'American Pale Ale',
     'style_rating': 75,
     'url': '/beer/new-belgium-tour-de-fall/279122/',
     'weighted_avg': 3.34}

-  ``get_brewery`` -- Pass in the URL for a brewery page and this
   function will return a ``Brewery`` object containing information
   about that brewery. In addition the the URL, it accepts an optional
   ``fetch`` argument (default: False), which can be set to true to
   immediately download the object's attributes. See the ``Brewery``
   class below. You can replicate the ``RateBeer.brewery(URL)``
   functionality using ``RateBeer.get_brewery(URL, True).__dict__``.

-  ``brewery`` -- Returns a dictionary with information about the
   brewery. Includes a 'get\_beers()' generator that provides
   information about the brewery's beers.

.. code:: python

    >>> rb.brewery("/brewers/deschutes-brewery/233/")
    {'_has_fetched': True,
     'city': 'Bend',
     'country': 'USA',
     'name': 'Deschutes Brewery',
     'postal_code': '97702',
     'state': 'Oregon',
     'street': '901 SW Simpson Ave',
     'type': 'Microbrewery',
     'url': '/brewers/deschutes-brewery/233/'}

-  ``search`` -- A generic search. A dictionary with two keys: beers and
   breweries. Each of those contains a list of objects, beers and
   breweries, respectively.

.. code:: python

    >>> rb = RateBeer()
    >>> results = rb.search("summit extra pale ale")
    >>> results
    {'beers': [<Beer('/beer/summit-extra-pale-ale/7344/')>,
               <Beer('/beer/summit-extra-pale-ale--rose-petals/317841/')>],
     'breweries': []}
    >>> results['beers'][0].__dict__
    {'_has_fetched': True,
     'abv': 5.1,
     'brewery': 'Summit Brewing Company',
     'brewery_country': 'USA',
     'brewery_url': '/brewers/summit-brewing-company/1233/',
     'calories': 153.0,
     'description': 'Summit Extra Pale Ale is not a beer brewed only for beer snobs. Just the opposite. It\x92s a beer for everyone to enjoy: construction workers, stock brokers, farmers, sales people, clerks, teachers, lawyers, doctors, even other brewers. Its light bronze color and distinctly hoppy flavor have made it a favorite in St. Paul, Minneapolis and the rest of the Upper Midwest ever since we first brewed it back in 1986.',
     'name': 'Summit Extra Pale Ale',
     'num_ratings': 698,
     'overall_rating': 68,
     'style': 'American Pale Ale',
     'style_rating': 59,
     'url': '/beer/summit-extra-pale-ale/7344/',
     'weighted_avg': 3.27}

-  ``beer_style_list`` -- Returns a dictionary containing the beer style
   name and a link to that page.

.. code:: python

    >>> rb.beer_style_list()
    {'Abbey Dubbel': '/beerstyles/abbey-dubbel/71/',
     'Abbey Tripel': '/beerstyles/abbey-tripel/72/',
     ...
     'Witbier': '/beerstyles/witbier/48/',
     'Zwickel/Keller/Landbier': '/beerstyles/zwickel-keller-landbier/74/'}

-  ``beer_style`` -- Returns a generator of ``Beer`` objects from the
   beer style page. Takes a ``url`` to a beer style and an optional
   ``sort_type``: ``overall`` returns the highest-rated beers (default
   behavior) and ``trending`` returns, well, the trending beers.

.. code:: python

    >>> [b for b in rb.beer_style("/beerstyles/abbey-dubbel/71/")]:
    [<Beer('/beer/st-bernardus-prior-8/2531/')>,
     <Beer('/beer/westmalle-dubbel/2205/')>,
     ...
     <Beer('/beer/trillium-rubbel/311473/')>,
     <Beer('/beer/weyerbacher-althea/230962/')>]

``Beer`` Class
~~~~~~~~~~~~~~

``Beer`` requires the url of the beer you're looking for, like
``RateBeer.beer`` and ``RateBeer.get_beer``.

**Attributes**

-  ``abv`` (float): percentage alcohol\*
-  ``brewery`` (string): the name of the beer's brewery
-  ``brewery_url`` (string): that brewery's url
-  ``calories`` (float): estimated calories for the beer\*
-  ``description`` (string): the beer's description
-  ``mean_rating`` (float): the mean rating for the beer (out of 5)\*
-  ``name`` (string): the full name of the beer (may include the brewery
   name)
-  ``num_ratings`` (int): the number of reviews\*
-  ``overall_rating`` (int): the overall rating (out of 100)
-  ``seasonal`` (string): which season the beer is produced in. Acts as
   a catch-all for any kind of miscellanious brew information.\*
-  ``style`` (string): beer style
-  ``style_rating`` (int): rating of the beer within its style (out of
   100)
-  ``url`` (string): the beer's url
-  ``weighted_avg`` (float): the beer rating average, weighted using
   some unknown algorithm (out of 5)\*

\* may not be available for all beers

**Methods**

-  ``get_reviews`` -- Returns a generator of ``Review`` objects for all
   the reviews in the beer. Takes a ``review_order`` argument, which can
   be "most recent", "top raters", or "highest score".

``Review`` Class
~~~~~~~~~~~~~~~~

``Review`` returns a datatype that contains information about a specific
review. For efficiency reasons, it requires the soup of the individual
review. Probably best to not try to make one yourself: use
``beer.get_reviews`` instead.

**Attributes**

-  ``appearance`` (int): rating for appearance (out of 5)
-  ``aroma`` (int): aroma rating (out of 10)
-  ``date`` (datetime): review date
-  ``overall`` (int): overall rating (out of 20, for some reason)
-  ``palate`` (int): palate rating (out of 5)
-  ``rating`` (float): another overall rating provided in the review.
   Not sure how this different from ``overall``.
-  ``text`` (string): actual text of the review.
-  ``user_location`` (string): writer's location
-  ``user_name`` (string): writer's username

``Brewery`` Class
~~~~~~~~~~~~~~~~~

``Brewery`` requires the url of the brewery you want information on.

**Attributes**

-  ``city`` (string): the brewery's city
-  ``country`` (string): the brewery's country
-  ``name`` (string): the brewery's name
-  ``postal_code`` (string): the brewery's postal code
-  ``state`` (string): the brewery's state/municipality/province.
-  ``street`` (string): the street address of the brewery.
-  ``type`` (string): the type of brewery. Typically "microbrewery" or
   "macrobrewery".
-  ``url`` (string): the url of the brewery

**Methods**

-  ``get_beers`` -- Returns a generator of ``Beer`` objects for every
   beer produced by the brewery. Some brewery pages list beers that are
   produced by do not have any pages, ratings, or information besides a
   name. For now, these beers are omitted from the results.

Tests
-----

``ratebeer`` uses the standard Python unit testing library.

Changes
-------

Note that the nature of web scraping means this might break at **any**
time.

v2.2.1
~~~~~~

-  ``Beer`` and ``Brewery`` objects are now "lazy", meaning they will
   not fetch the RateBeer page unless the requested attributes are not
   available. This should help minimize unnecessary requests.
-  ``RateBeer.search()`` now returns two lists of ``Beer`` and
   ``Brewery`` objects.
-  ``RateBeer.beer_style_list()`` now returns ``Beer`` and ``Brewery``
   objects.
-  ``Beer`` and ``Brewery`` objects now allow custom attributes to be
   set.

v2.1
~~~~

-  Bugfixes and performance enhancements.
-  Python 3 compatibility.

v2.0
~~~~

Major changes.

-  New ``Beer``, ``Review``, and ``Brewery`` classes.
-  Substantial overhaul in ``ratebeer.py``, addition of new files
   including separation of responsibilities
-  New generator functions in new classes.

v1.4
~~~~

-  ``reviews`` is now a generator.

v1.3.5
~~~~~~

-  Several improvements to results, particularly for edge cases and
   situations where search results are not in the expected order.

v1.3.4
~~~~~~

-  Metadata for beers returns floats when appropriate.

v1.3.3
~~~~~~

-  Captures more meta data.
-  Plays better with foreign beers.
-  Now if information is missing from a beer entry, its key is not added
   to the ``beer`` output.

v1.3.2
~~~~~~

-  Captures aliases for beer names.

v1.3
~~~~

-  Added ``beer_style_list`` and ``beer_style``.

v1.2
~~~~

-  Everything conforms to PEP8 now. Thanks to the fine folks
   `here <http://codereview.stackexchange.com/questions/69909/ratebeer-com-scraper>`__.
-  Minor refactoring.

v1.1
~~~~

-  Added ``reviews``.
-  Better exceptions (no more ``LookupError`` for 404s)

v1.0
~~~~

-  Initial release.

License
-------

**Creator**: Andrew Lilja

**Contributors**: \* Vincent Castellano
(@`Surye <https://github.com/Surye>`__) - Python 2 and 3 compatability
\* Steven A. Cholewiak - General bug squishing

All code released under `the Unlicense <http://unlicense.org/>`__
(a.k.a. Public Domain).
