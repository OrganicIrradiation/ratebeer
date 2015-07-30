#!/usr/bin/env python

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readfile(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

exec(readfile('ratebeer/_version.py'))

setup(
    name="ratebeer",
    version=__version__,
    description="Python API for RateBeer.com",
    long_description=readfile('README.rst'),
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
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        "beautifulsoup4",
        "lxml",
        "requests[security]",
    ],
    test_suite="test.py",
)