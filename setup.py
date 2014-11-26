#!/usr/bin/env python

try:
from setuptools import setup
except ImportError:
from distutils.core import setup


setup(
    name="ratebeer",
    version="1.3",
    description="""RateBeer.com data scraper. Makes getting information from RateBeer.com as easy as:

    >>> rb = RateBeer()
    >>> rb.search("summit extra pale ale")
    {'beers': [{'name': [u'Summit Extra Pale Ale'],
        'num_ratings': 678,
        'rating': 73  ,
        'url': u'/beer/summit-extra-pale-ale/7344/'}],
    'breweries': []}

    See the full README at https://github.com/alilja/ratebeer
    """,
    keywords="ratebeer rate beer ratings",
    author="Andrew Lilja",
    author_email="andrewlilja@gmail.com",
    url="https://github.com/alilja/ratebeer",
    license="Unlicense (a.k.a. Public Domain)",
    packages=["ratebeer"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        "beautifulsoup4",
        "lxml",
        "requests",
    ],
    test_suite="test.py",
)