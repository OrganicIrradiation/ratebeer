#!/usr/bin/env python
# coding: utf-8
import unittest

from ratebeer import RateBeer
from ratebeer import rb_exceptions


class TestBeer(unittest.TestCase):
    def is_float(self, s):
        ''' Checks whether a string represents a float '''
        try:
            float(s)
            return True
        except ValueError:
            return False

    def test_beer(self):
        ''' Make sure the results for a beer contain the expected data '''
        results = RateBeer().beer('/beer/new-belgium-tour-de-fall/279122/')
        self.assertIsNotNone(results)
        self.assertTrue(results['name'] == u'New Belgium Tour de Fall')
        self.assertTrue(results['style'] == u'American Pale Ale')
        self.assertTrue(results['ibu'] == 38)
        self.assertTrue(results['brewery'].url == u'/brewers/new-belgium-brewing-company/77/')
        self.assertTrue(results['overall_rating'] <= 100)
        self.assertTrue(results['style_rating'] <= 100)
        self.assertTrue(results['num_ratings'] > 0)
        self.assertTrue(results['mean_rating'] is None)
        self.assertTrue(self.is_float(results['weighted_avg']))
        self.assertTrue(results['weighted_avg'] <= 5.0)
        self.assertTrue(results['retired'] == False)
        self.assertTrue(results['description'] == u'New Belgium’s love for beer, bikes and benefits is best described by being at Tour de Fat. Our love for Cascade and Amarillo hops is best tasted in our Tour de Fall Pale Ale. We’re cruising both across the country during our favorite time of year. Hop on and find Tour de Fall Pale Ale in fall 2014.')

    def test_beer_404(self):
        ''' Checks to make sure that we appropriately raise a page not found '''
        rb = RateBeer()
        self.assertRaises(rb_exceptions.PageNotFound, rb.beer, "/beer/asdfasdf")

    def test_beer_closed_brewery(self):
        ''' Handling beers from closed brewers '''
        results = RateBeer().beer('/beer/hantens-hildener-landbrau/140207/')
        self.assertTrue(results['brewery'].url == u'/brewers/hildener-landbierbrauerei/12618/')

    def test_beer_closed_contract_brewery(self):
        ''' Handling beers from closed contract brewers '''
        results = RateBeer().beer('/beer/crew-republic-x-11-wet-hop/298026/')
        self.assertTrue(results['brewery'].url == u'/brewers/crew-republic-brewery/13816/')
        self.assertTrue(results['brewed_at'].url == u'/brewers/hohenthanner-schlossbrauerei/5557/')

    def test_beer_contract_brewed(self):
        ''' Handling contract brewed beers '''
        results = RateBeer().beer('/beer/benediktiner-weissbier/157144/')
        self.assertTrue(results['brewery'].url == u'/brewers/klosterbrauerei-ettal/1943/')
        self.assertTrue(results['brewed_at'].url == u'/brewers/licher-privatbrauerei-bitburger/1677/')

    def test_beer_get_reviews(self):
        ''' Check to make multi-page review searches work properly '''
        reviews = RateBeer().get_beer('/beer/deschutes-inversion-ipa/55610/').get_reviews()
        for i in range(20):
            self.assertIsNotNone(next(reviews))

    def test_beer_get_reviews_404(self):
        ''' Check lazy get_reviews 404 exception '''
        beer = RateBeer().get_beer('/beer/asdfasdf')
        with self.assertRaises(rb_exceptions.PageNotFound):
            next(beer.get_reviews())

    def test_beer_no_abv(self):
        results = RateBeer().beer('/beer/deschutes-altitude-amber/92102/')
        self.assertIsNotNone(results)
        self.assertTrue(results['name'] == u'Deschutes Altitude Amber')
        self.assertTrue(results['style'] == u'Amber Ale')
        self.assertTrue(results['abv'] is None)
        self.assertTrue(results['overall_rating'] is None)
        self.assertTrue(results['style_rating'] is None)
        self.assertTrue(results['num_ratings'] > 0)
        self.assertTrue(results['mean_rating'] > 0)
        self.assertTrue(self.is_float(results['weighted_avg']))
        self.assertTrue(results['weighted_avg'] > 0)
        self.assertTrue(results['retired'] == False)

    def test_beer_no_ratings(self):
        results = RateBeer().beer('/beer/deschutes-abyssident/194792/')
        self.assertIsNotNone(results)
        self.assertTrue(results['name'] == u'Deschutes Abyssident')
        self.assertTrue(results['style'] == u'Sour/Wild Ale')
        self.assertTrue(results['abv'] == 11)
        self.assertTrue(results['overall_rating'] is None)
        self.assertTrue(results['style_rating'] is None)
        self.assertTrue(results['num_ratings'] == 0)
        self.assertTrue(results['mean_rating'] is None)
        self.assertTrue(results['weighted_avg'] is None)
        self.assertTrue(results['retired'] == False)

    def test_beer_unicode(self):
        results = RateBeer().beer('/beer/stedji-oktoberbjor/292390/')
        self.assertIsNotNone(results)
        self.assertTrue(results['name'] == u'Steðji Októberbjór')
        self.assertTrue(results['brewery'].name == u'Brugghús Steðja')
        self.assertTrue(results['brewery'].url == u'/brewers/brugghus-steoja/15310/')

    def test_beer_retired_beer(self):
        ''' Attributes for retired beers display properly '''
        results = RateBeer().beer('/beer/shorts-funkin-punkin/79468/')
        self.assertTrue(results['retired'] == True)

    def test_beer_aliased(self):
        ''' Check that AliasedBeer exception is raised properly'''
        rb = RateBeer()
        self.assertRaises(rb_exceptions.AliasedBeer, rb.beer, "/beer/new-belgium-biere-de-mars/113241/")


class TestBrewery(unittest.TestCase):
    def test_brewery(self):
        ''' Make sure the results for a brewery contain the expected data '''
        results = RateBeer().brewery("/brewers/deschutes-brewery/233/")
        self.assertIsNotNone(results)
        self.assertTrue(results['name'] == u'Deschutes Brewery')
        self.assertTrue(results['type'] == u'Microbrewery')
        self.assertTrue(results['city'] == u'Bend')

    def test_brewery_404(self):
        ''' Make sure the results for a brewery contain the expected data '''
        rb = RateBeer()
        self.assertRaises(rb_exceptions.PageNotFound, rb.brewery, "/brewers/qwerty/1234567890")

    def test_brewery_get_beers(self):
        ''' Check to make multi-page review searches work properly '''
        beers = RateBeer().get_brewery("/brewers/deschutes-brewery/233/").get_beers()
        for beer in beers:
            self.assertIsNotNone(beer)

    def test_brewery_get_beers_404(self):
        ''' Check lazy get_beer 404 exception '''
        brewery = RateBeer().get_brewery("/brewers/qwerty/1234567890")
        with self.assertRaises(rb_exceptions.PageNotFound):
            next(brewery.get_beers())

    def test_brewery_unicode(self):
        ''' Check unicode brewery URLs '''
        results = RateBeer().brewery("/brewers/brauhaus-18•80/12750/")
        self.assertIsNotNone(results)
        self.assertTrue(results['name'] == u'Brauhaus 18•80')
        self.assertTrue(results['type'] == u'Brew Pub')
        self.assertTrue(results['country'] == u'Germany')


class TestMisc(unittest.TestCase):
    def test_beer_styles(self):
        ''' Make sure the results for a brewery list contain the expected data '''
        results = RateBeer().beer_style_list()
        self.assertIsNotNone(results, [])
        gen = RateBeer().beer_style(results['Abt/Quadrupel'], sort_type='score', sort_order='descending')
        beers = [b for b in gen]
        self.assertIsNotNone(beers)
        self.assertTrue(beers[0].name == u'Westvleteren 12 (XII)')
        gen = RateBeer().beer_style(results['Low Alcohol'], sort_type='score', sort_order='ascending')
        beers = [b for b in gen]
        self.assertIsNotNone(beers)
        self.assertTrue(beers[0].name == u'Busch NA')

    def test_whitespace_in_url(self):
        ''' The rare situation where a URL might have whitespace '''
        results = RateBeer().search("13 Virtues Cleanliness Helles")
        beer = results['beers'][0]
        self.assertTrue(beer._has_fetched == False)
        self.assertTrue(beer.url == u'/beer/13-virtues-cleanliness-helles/231944/')
        self.assertTrue(beer.name == u'13 Virtues Cleanliness Helles')


class TestSearch(unittest.TestCase):
    def test_str_ascii_search(self):
        ''' Test out the search function with an ASCII only str search '''
        results = RateBeer().search("deschutes inversion")
        self.assertListEqual(results['breweries'], [])
        self.assertIsNotNone(results['beers'])
        beer = results['beers'][0]
        self.assertTrue(beer.url == u'/beer/deschutes-inversion-ipa/55610/')
        self.assertTrue(beer.name == u'Deschutes Inversion IPA')

    def test_str_nonascii_search(self):
        ''' Test out the search function with a str with more than ASCII characters '''
        results = RateBeer().search("to øl jule mælk")
        self.assertListEqual(results['breweries'], [])
        self.assertIsNotNone(results['beers'])
        beer = results['beers'][0]
        self.assertTrue(beer.url == u'/beer/to-øl-jule-mælk/235066/')
        self.assertTrue(beer.name == u'To Øl Jule Mælk')

    def test_unicode_ascii_search(self):
        ''' Test out the search function with an ASCII only unicode search '''
        results = RateBeer().search(u"deschutes inversion")
        self.assertListEqual(results['breweries'], [])
        self.assertIsNotNone(results['beers'])
        beer = results['beers'][0]
        self.assertTrue(beer.url == u'/beer/deschutes-inversion-ipa/55610/')
        self.assertTrue(beer.name == u'Deschutes Inversion IPA')

    def test_unicode_nonascii_search(self):
        ''' Test out the search function with a unicode string with more than ASCII characters '''
        results = RateBeer().search(u"to øl jule mælk")
        self.assertListEqual(results['breweries'], [])
        self.assertIsNotNone(results['beers'])
        beer = results['beers'][0]
        self.assertTrue(beer.url == u'/beer/to-øl-jule-mælk/235066/')
        self.assertTrue(beer.name == u'To Øl Jule Mælk')


class TestAlpha(unittest.TestCase):
    def test_fetch_by_letter(self):
        ''' Make sure the results for a brewery list by index contain the expected data '''
        results = RateBeer().brewers_by_alpha("A")
        self.assertIsNotNone(results, [])
        beer = results[0]
        self.assertTrue(beer.url == u'/brewers/a-duus-and-co/1668/')
        self.assertTrue(beer.name == u'A. Duus & Co.')


if __name__ == '__main__':
    unittest.main()
