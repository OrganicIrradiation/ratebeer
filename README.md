ratebeer.py
===========

Changes
-------

### v0.1

* This guy right here.


What is this?
-------------

RateBeer.com is a database of user-created reviews about beers and breweries. However, their API has been down for some time, making it difficult to get that information programmatically. This simplifies that process, allow you to access it in the most painless way possible. Data is returned to you in a friendly, Pythonic way:

    {'beers': [{'name': [u'21st Amendment Summit IPA'],
                'num_ratings': <td align="right">4</td>,
                'rating': <td align="right"></td>,
                'url': u'/beer/21st-amendment-summit-ipa/61118/'},
                ...
               {'name': [u'4T\x92s Summit Hoppy'],
                'num_ratings': <td align="right">1</td>,
                'rating': <td align="right"></td>,
                'url': u'/beer/4ts-summit-hoppy/258783/'},
               ]
     'breweries': [{'location': u'St. Paul, Minnesota',
                    'name': [u'Summit Brewing Company'],
                    'url': u'/brewers/summit-brewing-company/1233/'},
                   ...
                   {'location': u'Gaithersburg, Maryland',
                    'name': [u'Summit Station Restaurant & Brewery'],
                    'url': u'/brewers/summit-station-restaurant-brewery/346/'}
                   ]
    }


Why not BeerAdvocate.com?
-------------------------

Because they're evil, and they issue takedown notices left and right.


Requirements
------------

Requires [Requests](http://docs.python-requests.org/en/latest/) and [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/). See `requirements.txt`.


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

* `brewery` -- Returns information about the brewery. Also takes a `url`.


Tests
-----
`ratebeer` uses the standard Python unit testing library.


License
-------

**Author**: Andrew Lilja

All code released under [the Unlicense](http://unlicense.org/) (a.k.a. Public
Domain).