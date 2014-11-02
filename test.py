import unittest
from bs4 import BeautifulSoup
from ratebeer import RateBeer

class TestSearch(unittest.TestCase):
    def test_results_exist(self):
        soup = RateBeer().search("summit")
        self.assertTrue(any("beers" in s for s in soup.find_all("h1")))
        self.assertTrue(any("brewers" in s for s in soup.find_all("h1")))

        soup = RateBeer().search("summit extra pale ale")
        self.assertTrue(any("beers" in s for s in soup.find_all("h1")))
        self.assertFalse(any("brewers" in s for s in soup.find_all("h1")))

        soup = RateBeer().search(";lfidsuaflihjdksfdsajfl")
        self.assertTrue(soup.find_all(text="0 beers"))

if __name__ == '__main__':
    unittest.main()