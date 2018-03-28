# Devlo [![Build Status](https://travis-ci.org/sergoh/devlo-blog.svg?branch=master)](https://travis-ci.org/sergoh/devlo-blog)

A development blog, written by two Lopez Brothers. 

## Integrations
Static Website Generator [Pelican](http://blog.getpelican.com/)
The minimalist [Flex](https://github.com/alexandrevicenzi/Flex) theme.

## Install

Install pelican and dependencies using pip:

`pip install pelican Markdown typogrify`

## Build Locally

Once installed, to build locally
`Make html`

Once built, to serve

`Make serve` or `Make devserver`

## Publish
Push the commit to the `master` and [Travis-CI](https://travis-ci.org/sergoh/devlo-blog) will kick off a build to deploy the website
