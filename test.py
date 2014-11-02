import unittest
from ratebeer import RateBeer

class TestSearch(unittest.TestCase):
    def test_result_types(self):
        soup = RateBeer().search("summit")
        self.assertTrue(any("beers" in s for s in soup.find_all("h1")))
        self.assertTrue(any("brewers" in s for s in soup.find_all("h1")))

        soup = RateBeer().search("summit extra pale ale")
        self.assertTrue(any("beers" in s for s in soup.find_all("h1")))
        self.assertFalse(any("brewers" in s for s in soup.find_all("h1")))

if __name__ == '__main__':
    unittest.main()