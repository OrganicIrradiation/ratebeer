#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from ratebeer import RateBeer

setup(
    name="ratebeer",
    version=RateBeer.VERSION,
    description="Python API for RateBeer.com",
    long_description=RateBeer.__doc__,
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
        "requests",
    ],
    test_suite="test.py",
)