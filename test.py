import unittest
from bs4 import BeautifulSoup
from ratebeer import RateBeer

class TestSearch(unittest.TestCase):
    def test_search_results(self):
        soup = RateBeer()._search("summit")
        self.assertTrue(any("beers" in s for s in soup.find_all("h1")))
        self.assertTrue(any("brewers" in s for s in soup.find_all("h1")))

        soup = RateBeer()._search("summit extra pale ale")
        self.assertTrue(any("beers" in s for s in soup.find_all("h1")))
        self.assertFalse(any("brewers" in s for s in soup.find_all("h1")))

        soup = RateBeer()._search(";lfidsuaflihjdksfdsajfl")
        self.assertTrue(soup.find_all(text="0 beers"))

    def test_search(self):
    	results = RateBeer().search("deschutes inversion")
    	self.assertListEqual(results['breweries'],[])
    	self.assertIsNotNone(results['beers'])
    	self.assertEqual(results['beers'][0],{
    		'url': u'/beer/deschutes-inversion-ipa/55610/', 
    		'rating': u'94', 
    		'name': u'Deschutes Inversion IPA', 
    		'num_ratings': u'1151', 
    		'id': u'55610'})

    def test_beer_404(self):
    	results = RateBeer().beer("/beer/sdfasdf")
    	self.assertIsNone(results)

    def test_beer(self):
    	results = RateBeer().beer("/beer/deschutes-inversion-ipa/55610/")
    	self.assertIsNotNone(results)
    	self.assertListEqual(results,[])

if __name__ == '__main__':
    unittest.main()