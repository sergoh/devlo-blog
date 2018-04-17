Title: Setting up a Pelican Blog on Github Pages with Travis-CI using MacOS High Sierra
Date: 2018-03-22
Modified: 2018-04-04
Author: Sergio Lopez
Summary: The step-by-step instructions to get this blog up and running.
Tags: pelican, mac, python, blog, setup, travis-ci, github pages

## **Intro**

Setting up this blog was not a difficult task, but it did some digging around the internet to get everything up and 
running the way my brother and I visioned our blog. I'm going to document the steps I followed from start to finish, combined from all those resources, 
so that anyone wanting to setup something similar can do so!

## **Configure Mac High Sierra 10.13**

#### Bash profile setup
First thing is to make sure that we update the PATH to ensure that any Homebrew installations take precedence over stock macOS binaries.

Open your `.bash_profile` using:

```bash
$ vim ~/.bash_profile
```
then add:

```bash
# Ensure user-installed binaries take precedence
export PATH=/usr/local/share/python:$PATH
# Load .bashrc if it exists
test -f ~/.bashrc && source ~/.bashrc
```

Type `:wq` to write and save the `.bash_profile`

To have the directives take effect in the current session, without a restart needed. Type the following

```bash
$ source ~/.bash_profile
```

#### Homebrew Install

Homebrew allows you to install stuff you need, quick and easy, that Apple didn't.

To install paste the following in the terminal: 

```bash
$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Run the following:

```bash
$ brew doctor
```

To ensure that it installed correctly and see if anything needs to be addressed

#### Python Install

Now that Homebrew is installed, we can use it to install Python 2.7

```bash
$ brew install python@2
```

Now, check what pythons are found on your OSX by typing:

```bash
$ which -a python
```
There should be one python found at `/usr/bin/` (the Apple python) and one at `/usr/local/bin/` which is the Homebrew python.

```bash
$ which python
```
will show you, which python is found first in your `$PATH` and will be executed when you invoke python.

#### Virtualenv Install

When you're working on python projects, you might run into the scenario where one project requires a specific version of a package
and another project could require a newer version of that package. Now this could cause an issue if they were all installed 
globally, in order to get around that I recommend we install Virtualenv

```bash
$ pip2 install virtualenv
```

Once that is installed, we should create a directory to store our virtual environments. 

```bash
$ mkdir -p ~/Virtualenvs
```

#### Restricting Pip to Virtual Environments 

To ensure that pip will not install a package in global but only if a virtual environment is active, we need to create/update
the pip configuration file.

```bash
$ mkdir -p ~/Library/Application\ Support/pip
```

We’ll then open Pip’s configuration file 

```bash
$ vim ~/Library/Application\ Support/pip/pip.conf
```

add the following lines: 

```bash
[install]
require-virtualenv = true

[uninstall]
require-virtualenv = true
```

## **Create Pelican Virtual Environment **

With our MacOS configured we can now install pelican. First we create the virtual environment:

```bash
$ cd ~/Virtualenvs
$ virtualenv pelican
``` 

and activate it via:

```bash
$ cd pelican
$ source bin/activate
```

Install pelican using pip2:

```bash
$ pip2 install pelican markdown typogrify
```

## **Setting up GitHub Pages**
To create a Github user page, make sure you're logged into github and create and initialize two new repositories:

_yourusername.github.blog_ and _yourusername.github.io_

The _yourusername.github.blog_ repository will hold the source code of the blog and the  _yourusername.github.io_ repository
will hold the output HTML files that pelican generates.

Next, you'll clone your _yourusername.github.blog_ branch into your projects folder, if you don't have one. Go ahead and create one.

```bash
$ mkdir -p ~/Projects/
$ cd ~/Projects/
$ git clone https://github.com/yourusername/yourusername.github.blog.git
```

## **Setting up Pelican**

Once Pelican has been installed, and your repositories are set up,  you can create a skeleton project via the pelican-quickstart command. First
we need to switch to the directory of our project.

```bash
$ cd ~/Projects/yourusername.github.blog
```

initiate pelican using the command: 

```bash
$ pelican-quickstart
```

It should ask you a series of questions:

```bash
$ Where do you want to create your new web site? [.] ./
$ What will be the title of this web site? blog
$ Who will be the author of this web site? Your Name
$ What will be the default language of this web site? [pt] en
$ Do you want to specify a URL prefix? e.g., http://example.com   (Y/n) n
$ Do you want to enable article pagination? (Y/n) y
$ How many articles per page do you want? [10] 10
$ What is your time zone? 
$ Do you want to generate a Fabfile/Makefile to automate generation and publishing? (Y/n) Y 
$ Do you want an auto-reload & simpleHTTP script to assist with theme and site development? (Y/n) n
$ Do you want to upload your website using FTP? (y/N) n
$ Do you want to upload your website using SSH? (y/N) n
$ Do you want to upload your website using Dropbox? (y/N) n
$ Do you want to upload your website using S3? (y/N) n
$ Do you want to upload your website using Rackspace Cloud Files? (y/N) n
$ Do you want to upload your website using GitHub Pages? (y/N) y
$ Is this your personal page (yourusername.github.io)? (y/N) y
Done. Your new project is available at /home/yourusername/yourusername.github.io
```

#### Picking a theme

The next step is to pick a theme for the blog, we can use this site [Pelican Themes](http://www.pelicanthemes.com/) to see
live examples of themes.

Once a theme is picked you need create a submodule of the theme you want.
Clone the pelican-themes repository into a submodule of _yourusername.github.blog_. For this example, I'm using the Flexi :

```bash
$ git submodule add git@github.com:alexandrevicenzi/Flex.git Flex
$ git submodule init
$ git submodule update
```

Now you should have your pelican-themes repository stored at _~/Projects/yourusername.github.blog/Flex_.
To use one of the themes, edit your Pelican settings file `pelicanconf.py` to include this line:

```javascript
THEME = "./Flex"
```

Save the changes and regenerate your site by using the make command 

```bash
$ make devserver
```

Which will simultaneously run Pelican in regeneration mode as well as serve the output at `http://localhost:8000`. 
Once you are done viewing your changes, you should stop the development server via:

```bash
$ make stopserver
```

#### Add Custom Domain to Blog

To use a custom domain with GitHub Pages, you need to put the domain of your site (e.g., blog.example.com)
inside a CNAME file at the root of your site. To do this, create the content/extra/ directory and add a CNAME file to it.
Then use the STATIC_PATHS setting to tell Pelican to copy this file to your output directory. For example:

```python
STATIC_PATHS = ['images', 'extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}
```

#### Setting up Apex domain  DNS

You can set up an apex domain through your DNS provider and GitHub Pages' servers will automatically
 create redirects between them. For example, your site can be found at `www.example.com` or `example.com.`

1. Contact your DNS provider for detailed instructions on how to set up A records.

2. Follow your DNS provider's instructions to create two A records that point your custom domain to the following IP addresses:

    `192.30.252.153`

    `192.30.252.154`

3. To confirm that your DNS record is set up correctly, use the dig command with your custom domain. Using a custom domain as an example:
 
```bash
$ dig +noall +answer example.com
 example.com.   73  IN  A 192.30.252.153
 example.com.   73  IN  A 192.30.252.154
```

## **Setting up Travis CI**

Now we're going to setup Travis CI, which will allow us to deploy a new version of the blog everytime there is a commit to master.

First, create a `requirements.txt` in the blog project folder:

```
pelican
Markdown
typogrify
fabric
```

Then create a `.travis.yml` file in the same folder:

```yaml
branches:
  only:
  - master
language: python
python:
- 2.7
install:
- pip install -r requirements.txt
script:
- make html
notifications:
  email:
    on_success: always
    on_failure: always
env:
  global:
before_install:
  - git submodule update --init --recursive
after_success: bash deploy.sh
```
Then add also the `deploy.sh` script and update the global variable with yours:

```bash
#!/usr/bin/env bash
BRANCH=master
TARGET_REPO=yourusername/yourusername.github.io.git
PELICAN_OUTPUT_FOLDER=output

echo -e "Testing travis-encrypt"
echo -e "$VARNAME"

if [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
    echo -e "Starting to deploy to Github Pages\n"
    if [ "$TRAVIS" == "true" ]; then
        git config --global user.email "travis@travis-ci.org"
        git config --global user.name "Travis"
    fi
    #using token clone gh-pages branch
    git clone --quiet --branch=$BRANCH https://${GH_TOKEN}@github.com/$TARGET_REPO built_website > /dev/null
    #go into directory and copy data we're interested in to that directory
    cd built_website
    rsync -rv --exclude=.git  ../$PELICAN_OUTPUT_FOLDER/* .
    #add, commit and push files
    git add -f .
    git commit -m "Travis build $TRAVIS_BUILD_NUMBER pushed to Github Pages"
    git push -fq origin $BRANCH > /dev/null
    echo -e "Deploy completed\n"
fi
```

Now we need to create the encrypted token under env global in order to let Travis CI intract withtthe repository.
Login to the Github web interface to get an [Authentication Token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/), and then install the travis command line tool with:

```bash
$ sudo apt-get install ruby1.9.1-dev
$ sudo gem install travis
```


and run from inside the repository:

```bash
$ travis encrypt GH_TOKEN=AUTHENTICATIONTOKENFROMGITHUB --add env.global
```

From now on, every time you commit a change to master, it should kick off a build in travis ci and push the code to your _yourusername.github.io_

Now go grab a drink, its well deserved! Cheers!


##### References

Below are a list of links or other guides that have helped me get to this point.

_https://hackercodex.com/guide/mac-development-configuration/_

_https://hackercodex.com/guide/python-development-environment-on-mac-osx/_

_https://superuser.com/questions/915810/pip-not-working-on-hombrew-python-2-7-install_

_http://docs.getpelican.com/en/3.6.3/install.html_

_https://github.com/getpelican/pelican-themes_

_https://git-scm.com/docs/gitmodules_

_https://github.com/getpelican/pelican/blob/master/docs/tips.rst_

_https://help.github.com/articles/using-a-custom-domain-with-github-pages/_

_https://zonca.github.io/2013/09/automatically-build-pelican-and-publish-to-github-pages.html_

_https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/_

_https://docs.travis-ci.com/user/github-oauth-scopes_






