#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from conway.gol import __version__

PACKAGE = "gol"
NAME = "gol"
DESCRIPTION = "Curses implementation of Conway's Game Of Life with an evolutionary twist"
AUTHOR = "Chris Seymour"
AUTHOR_EMAIL = "chris.j.seymour@hotmail.com"
AUTHOR_TWITTER = "@iiSeymour"
URL = "https://github.com/iiSeymour/game-of-life"

setup(
    name=NAME,
    version=__version__,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    packages=['conway'],
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console :: Curses",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Topic :: Games/Entertainment :: Simulation",
        "Programming Language :: Python",
    ],
    entry_points={
        'console_scripts': [
            'gol=conway.gol:main',
        ]
    }
)
