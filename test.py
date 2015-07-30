#!/usr/bin/env python
# coding: utf-8
import unittest

from ratebeer import RateBeer
from ratebeer import rb_exceptions


class TestBeer(unittest.TestCase):
    def test_beer(self):
        ''' Make sure the results for a beer contain the expected data '''
        results = RateBeer().beer("/beer/new-belgium-tour-de-fall/279122/")
        self.assertIsNotNone(results)
        superset = results
        subset = {'name': u'New Belgium Tour de Fall',
                  'brewery': u'New Belgium Brewing Company',
                  'brewery_url': u'/brewers/new-belgium-brewing-company/77/',
                  'style': u'American Pale Ale',
                  'ibu': 38}
        self.assertTrue(all(item in superset.items() for item in subset.items()))

    def test_beer_404(self):
        ''' Checks to make sure that we appropriately raise a page not found '''
        rb = RateBeer()
        self.assertRaises(rb_exceptions.PageNotFound, rb.beer, "/beer/asdfasdf")

    def test_beer_closed_brewery(self):
        ''' Handling beers from closed brewers '''
        results = RateBeer().beer('/beer/hantens-hildener-landbrau/140207/')
        superset = results
        subset = {'brewery': '1. Hildener Landbierbrauerei',
                  'brewery_url': '/brewers/1-hildener-landbierbrauerei/12618/'}
        self.assertTrue(all(item in superset.items() for item in subset.items()))

    def test_beer_contract_brewed(self):
        ''' Handling contract brewed beers '''
        results = RateBeer().beer('/beer/benediktiner-weissbier/157144/')
        superset = results
        subset = {'brewed_at': 'Licher Privatbrauerei (Bitburger)',
                  'brewed_at_url': '/brewers/licher-privatbrauerei-bitburger/1677/',
                  'brewery': 'Klosterbrauerei Ettal',
                  'brewery_url': '/brewers/klosterbrauerei-ettal/1943/'}
        self.assertTrue(all(item in superset.items() for item in subset.items()))

    def test_beer_get_reviews(self):
        ''' Check to make multi-page review searches work properly '''
        reviews = RateBeer().get_beer("/beer/deschutes-inversion-ipa/55610/").get_reviews()
        for i in range(3):
            self.assertIsNotNone(next(reviews))

    def test_beer_get_reviews_404(self):
        ''' Check lazy get_reviews 404 exception '''
        beer = RateBeer().get_beer("/beer/asdfasdf")
        with self.assertRaises(rb_exceptions.PageNotFound):
            next(beer.get_reviews())

    def test_beer_unicode(self):
        results = RateBeer().beer("/beer/steoji-oktoberbjor/292390/")
        self.assertIsNotNone(results)
        superset = results
        subset = {'name': u'Steðji Októberbjór',
                  'brewery': u'Brugghús Steðja',
                  'brewery_url': u'/brewers/brugghus-steoja/15310/',
                  'style': u'Spice/Herb/Vegetable'}
        self.assertTrue(all(item in superset.items() for item in subset.items()))


class TestBrewery(unittest.TestCase):
    def test_brewery(self):
        ''' Make sure the results for a brewery contain the expected data '''
        results = RateBeer().brewery("/brewers/deschutes-brewery/233/")
        self.assertIsNotNone(results)
        superset = results
        subset = {'name': u'Deschutes Brewery',
                  'type': u'Microbrewery',
                  'city': u'Bend'}
        self.assertTrue(all(item in superset.items() for item in subset.items()))

    def test_brewery_404(self):
        ''' Make sure the results for a brewery contain the expected data '''
        rb = RateBeer()
        self.assertRaises(rb_exceptions.PageNotFound, rb.brewery, "/brewers/qwerty/1234567890")

    def test_brewery_get_beers(self):
        ''' Check to make multi-page review searches work properly '''
        beers = RateBeer().get_brewery("/brewers/deschutes-brewery/233/").get_beers()
        for i in range(3):
            self.assertIsNotNone(next(beers))

    def test_brewery_get_beers_404(self):
        ''' Check lazy get_beer 404 exception '''
        brewery = RateBeer().get_brewery("/brewers/qwerty/1234567890")
        with self.assertRaises(rb_exceptions.PageNotFound):
            next(brewery.get_beers())

    def test_brewery_unicode(self):
        ''' Check unicode brewery URLs '''
        results = RateBeer().brewery("/brewers/brauhaus-18•80/12750/")
        self.assertIsNotNone(results)
        superset = results
        subset = {'name': u'Brauhaus 18\x9580',
                  'type': u'Brew Pub',
                  'country': u'Germany'}
        self.assertTrue(all(item in superset.items() for item in subset.items()))


class TestSearch(unittest.TestCase):
    def test_str_ascii_search(self):
        ''' Test out the search function with an ASCII only str search '''
        results = RateBeer().search("deschutes inversion")
        self.assertListEqual(results['breweries'], [])
        self.assertIsNotNone(results['beers'])
        superset = results['beers'][0].__dict__
        subset = {'url': '/beer/deschutes-inversion-ipa/55610/',
                  'name': u'Deschutes Inversion IPA'}
        self.assertTrue(all(item in superset.items() for item in subset.items()))

    def test_str_nonascii_search(self):
        ''' Test out the search function with a str with more than ASCII characters '''
        results = RateBeer().search("to øl jule mælk")
        self.assertListEqual(results['breweries'], [])
        self.assertIsNotNone(results['beers'])
        superset = results['beers'][0].__dict__
        subset = {'url': '/beer/to-ol-jule-maelk/235066/',
                  'name': u'To Øl Jule Mælk'}
        self.assertTrue(all(item in superset.items() for item in subset.items()))

    def test_unicode_ascii_search(self):
        ''' Test out the search function with an ASCII only unicode search '''
        results = RateBeer().search(u"deschutes inversion")
        self.assertListEqual(results['breweries'], [])
        self.assertIsNotNone(results['beers'])
        superset = results['beers'][0].__dict__
        subset = {'url': '/beer/deschutes-inversion-ipa/55610/',
                  'name': u'Deschutes Inversion IPA'}
        self.assertTrue(all(item in superset.items() for item in subset.items()))

    def test_unicode_nonascii_search(self):
        ''' Test out the search function with a unicode string with more than ASCII characters '''
        results = RateBeer().search(u"to øl jule mælk")
        self.assertListEqual(results['breweries'], [])
        self.assertIsNotNone(results['beers'])
        superset = results['beers'][0].__dict__
        subset = {'url': '/beer/to-ol-jule-maelk/235066/',
                  'name': u'To Øl Jule Mælk'}
        self.assertTrue(all(item in superset.items() for item in subset.items()))


if __name__ == '__main__':
    unittest.main()
