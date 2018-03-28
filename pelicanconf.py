#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Lopez Brothers'
SITENAME = u'DevLo'
SITEURL = 'https://sergoh.github.io'
#SITEURL = 'http://localhost:8000'
THEME = "./Flex"

PATH = 'content'

TIMEZONE = 'MST'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('About', 'http://getpelican.com/'),
         ('Contact', 'http://python.org/'))

# Social widget
MIGUEL_SOCIAL = (('linkedin', 'https://www.linkedin.com/in/lopezm1/'),
          ('github', 'https://github.com/lopezm1'),
          ('twitter', 'https://twitter.com/BrogrammerMiggy'))

SERGIO_SOCIAL = (('linkedin', 'https://www.linkedin.com/in/sergiolopezjr/'),
          ('github', 'https://github.com/sergoh'),
          ('twitter', 'https://twitter.com/mrsergoh'))

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

STATIC_PATHS = ['extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}

# Menu
MAIN_MENU = True
MENUITEMS = (('Archives', '/archives.html'),
             ('Categories', '/categories.html'),
             ('Tags', '/tags.html'),)
