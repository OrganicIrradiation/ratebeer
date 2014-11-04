#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import ratebeer

setup(name="ratebeer",
      version="1.0",
      description="RateBeer.com data scraper.",
      long_description=ratebeer.RateBeer.__doc__,
      keywords="ratebeer rate beer ratings",
      author="Andrew Lilja",
      author_email="andrewlilja@gmail.com",
      url="https://github.com/alilja/ratebeer",
      license="Unlicense (a.k.a. Public Domain)",
      packages=["ratebeer"],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Topic :: Internet',
                   'Topic :: Internet :: WWW/HTTP',
                  ],
      test_suite="test.py",)