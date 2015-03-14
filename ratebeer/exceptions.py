from exceptions import Exception


class PageNotFound(Exception):
    """Returns the URL of the page not found."""
    pass


class AliasedBeer(Exception):
    """Returns the old and new urls for an aliased beer."""
    def __init__(self, oldurl, newurl):
        self.oldurl = oldurl
        self.newurl = newurl
