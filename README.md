# Devlo [![Build Status](https://travis-ci.org/sergoh/devlo-blog.svg?branch=master)](https://travis-ci.org/sergoh/devlo-blog)

A development blog, written by two Lopez Brothers. 

## Integrations
Static Website Generator [Pelican](http://blog.getpelican.com/)
The minimalist [Flex](https://github.com/alexandrevicenzi/Flex) theme.

## Install

Install virtualenv

`pip install virtualenv`

Create a virtualenv

`virtualenv ~/.virtualenvs/pelican`

Activate the virtualenv

`source ~/.virtualenvs/pelican/bin/activate`

cd into `~/.virtualenvs/pelican` and install pelican + dependencies using pip:

`pip install pelican Markdown typogrify`

Deactive the virtualenv

`deactivate`

## Build Locally

_Note: if it's your first time pulling down the submodule, you'll need to use this:_
`git submodule update --init --recursive`

Once installed, to build locally
`Make html`

Once built, to serve

`Make serve` or `Make devserver`

## Publish
1. Run the `Make publish` command, as it will use the `publishconf.py` config file
2. Push the commit to the `master` and [Travis-CI](https://travis-ci.org/sergoh/devlo-blog) will kick off a build to deploy the website
