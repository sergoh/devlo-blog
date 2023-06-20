#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'https://www.devlo.io'
RELATIVE_URLS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'

DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
GOOGLE_ANALYTICS = "UA-116740360-1"
GOOGLE_TAG_MANAGER = "GTM-T32GC6Q"

GOOGLE_ADSENSE = {
    'ca_id': 'ca-pub-2119138261035978',    # Your AdSense ID
    'page_level_ads': True,          # Allow Page Level Ads (mobile)
    'ads': {
        'aside': '7180191250',          # Side bar banner (all pages)
        'main_menu': '7180191250',      # Banner before main menu (all pages)
        'index_top': '',      # Banner after main menu (index only)
        'index_bottom': '5952522457',   # Banner before footer (index only)
        'article_top': '5952522457',    # Banner after article title (article only)
        'article_bottom': '5952522457', # Banner after article content (article only)
    }
}
