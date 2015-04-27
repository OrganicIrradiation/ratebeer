#!/usr/local/bin/python
# coding: utf-8
import unittest

from ratebeer import RateBeer
from ratebeer import rb_exceptions


class TestSearch(unittest.TestCase):
    def test_search(self):
        ''' Test out the search function with a str search '''
        results = RateBeer().search("deschutes inversion")
        self.assertListEqual(results['breweries'], [])
        self.assertIsNotNone(results['beers'])
        self.assertDictContainsSubset({
            'url': '/beer/deschutes-inversion-ipa/55610/',
            'name': u'Deschutes Inversion IPA',
            'id': 55610
        }, results['beers'][0])

    def test_unicode_search(self):
        ''' Test out the search function with a unicode search '''
        results = RateBeer().search("to øl jule mælk")
        self.assertListEqual(results['breweries'], [])
        self.assertIsNotNone(results['beers'])
        self.assertDictContainsSubset({
            'url': '/beer/to-ol-jule-maelk/235066/',
            'name': u'To Øl Jule Mælk',
            'id': 235066
        }, results['beers'][0])


class TestBeer(unittest.TestCase):
    def test_beer(self):
        ''' Make sure the results for a beer contain the expected data '''
        results = RateBeer().beer("/beer/new-belgium-tour-de-fall/279122/")
        self.assertIsNotNone(results)
        self.assertDictContainsSubset({
            'name': u'New Belgium Tour de Fall',
            'brewery': u'New Belgium Brewing Company',
            'brewery_url': u'/brewers/new-belgium-brewing-company/77/',
            'style': u'American Pale Ale',
            'ibu': 38
        }, results)

    def test_beer_404(self):
        ''' Checks to make sure that we appropriately raise a page not found '''
        rb = RateBeer()
        self.assertRaises(rb_exceptions.PageNotFound, rb.beer, "/beer/sdfasdf")

    def test_beer_country(self):
        results = RateBeer().beer("/beer/rochefort-trappistes-10/2360/")
        self.assertIsNotNone(results)
        self.assertDictContainsSubset({
            'name': u'Rochefort Trappistes 10',
            'brewery': u'Brasserie Rochefort',
            'brewery_url': u'/brewers/brasserie-rochefort/406/',
            'style': u'Abt/Quadrupel',
            'abv': 11.3
        }, results)

    def test_beer_unicode(self):
        results = RateBeer().beer("/beer/steoji-oktoberbjor/292390/")
        self.assertIsNotNone(results)
        self.assertDictContainsSubset({
            'name': u'Steðji Októberbjór',
            'brewery': u'Brugghús Steðja',
            'brewery_url': u'/brewers/brugghus-steoja/15310/',
            'style': u'Spice/Herb/Vegetable'
        }, results)

    def test_reviews(self):
        ''' Check to make multi-page review searches work properly '''
        reviews = RateBeer().get_beer("/beer/deschutes-inversion-ipa/55610/").get_reviews()
        for i in range(3):
            self.assertIsNotNone(reviews.next())


class TestBrewery(unittest.TestCase):
    def test_brewery(self):
        ''' Make sure the results for a brewery contain the expected data '''
        results = RateBeer().brewery("/brewers/deschutes-brewery/233/")
        self.assertIsNotNone(results)
        self.assertDictContainsSubset({
            'name': u'Deschutes Brewery',
            'type': u'Microbrewery',
            'city': u'Bend',
        }, results)

    def test_brewery_404(self):
        ''' Make sure the results for a brewery contain the expected data '''
        rb = RateBeer()
        self.assertRaises(rb_exceptions.PageNotFound, rb.beer, "/brewers/qwerty/1234567890")

    def test_brewery_unicode(self):
        ''' Check unicode brewery URLs '''
        results = RateBeer().brewery("/brewers/brauhaus-18•80/12750/")
        self.assertIsNotNone(results)
        self.assertDictContainsSubset({
            'name': u'Brauhaus 18\x9580',
            'type': u'Brew Pub',
            'country': u'Germany',
        }, results)

    def test_beers(self):
        ''' Check to make multi-page review searches work properly '''
        beers = RateBeer().get_brewery("/brewers/deschutes-brewery/233/").get_beers()
        for i in range(3):
            self.assertIsNotNone(beers.next())


if __name__ == '__main__':
    unittest.main()
