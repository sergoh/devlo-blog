#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Lopez Brothers'
FAVICON = '/favicon.ico'
SITELOGO = '/images/Devlo-Logo.png'
SITENAME = u'DevLo Software Blog'
#SITETITLE = u'DevLo'
SITEURL = 'http://localhost:8000'
SITESUBTITLE = 'Lopez Brothers Blog'
SITEDESCRIPTION = 'DevLo - Software Blog.'
THEME = "./Flex"
HOME_HIDE_TAGS = True
PYGMENTS_STYLE = "arduino"
DISABLE_URL_HASH = True

ROBOTS = 'index, follow'

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
#LINKS = (('', ''),('Contact', 'http://python.org/'))

# Social widget
MIGUEL_SOCIAL = (('linkedin', 'https://www.linkedin.com/in/lopezm1/'),
          ('github', 'https://github.com/lopezm1'))

SERGIO_SOCIAL = (('linkedin', 'https://www.linkedin.com/in/sergiolopezjr/'),
          ('github', 'https://github.com/sergoh'))

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

STATIC_PATHS = ['images', 'extra']
EXTRA_PATH_METADATA = {
    'extra/CNAME': {'path': 'CNAME'},
    'extra/favicon.ico': {'path': 'favicon.ico'},
    'extra/ads.txt': {'path': 'ads.txt'},
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/google201f3609f5b46efa.html': {'path': 'google201f3609f5b46efa.html'},
}

CUSTOM_CSS = 'extra/static/custom.css'

SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.8,
        "indexes": 0.5,
        "pages": 0.5
    },
    "changefreqs": {
        "articles": "daily",
        "indexes": "monthly",
        "pages": "monthly"
    }
}

# Menu
MAIN_MENU = True
MENUITEMS = (('Archives', '/archives.html'),
             ('Categories', '/categories.html'),
             ('Tags', '/tags.html'),)
