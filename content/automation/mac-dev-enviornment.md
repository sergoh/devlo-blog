Title: Install Common Developement Tools on Mac
Date: 2018-04-04
Modified: 2018-04-04
Tags: automation, mac, dev
Slug: mac-developer-enviornment
Author: Miguel Lopez
Summary: Automatically install common developer tools on macOS with this script.


Technical Stack: macOS High Sierra 
Read: 5 minutes 

## **Prerequisites** 

- Mac Laptop or Desktop (script was build with macOS High Sierra)
- Knowledge of how to run a bash script

## **Introduction**

I've built a script that uses homebrew to install a common set of development tools on a Mac. Feel free to download the script from my [github gist](https://gist.github.com/lopezm1/16e641918277a4888ee7e88722b2d7dd).

I've done my best to avoid installing any duplicates by checking if you've already installed the application in the /Applications folder of the Mac. 

## **Packages it installs**

- Homebrew
- Slack
- Docker
- iTerm2
- Google Chrome (boooo Safari)
- IntelliJ Idea (Enterprise)
- SourceTree
- Spotify (super important)
- Terraform
- git
- python
- pip3
- node
- coreutils

Feel free to verify any of these packages after installation by checking your /Applications folder or checking for the instance in terminal. 

For example:

```sh
git --version
python --version
pip3 --version
node --version
```

_If you don't need to extend the script, stop reading **here**_

## **Packages it installs**

Extending the script is easy. 

If you wish to add other homebrew formulas, just add them at the end of the script. 

```
## Install other miscellaneous tools
brew install git
brew install python
brew install node
brew install coreutils
*brew install <your formula here>*
.
.
```

If you wish to add another application, you'll need to use ```brew cask install``` and edit the script in two places.

**1) Add to the application name to the application array list. (We'll add Skype as an example)**

```
## Applications we will install with `brew cask install`
## additional applications can be added here if you wish to install them
declare -a applications=( Spotify Sourcetree Slack Docker iTerm "IntelliJ Idea" "Google Chrome" **"Skype"** )
```
Skype is capitalized because it would be saved to your /Applciations folder as Skype.app (the script will use this to make sure the application isn't already installed).

Next, search for the application on the [cask room search](https://caskroom.github.io/search).

**2) Add to the switch case statement and call brew_install with the cask-name pulled from the search**

```
 case $1 in
      Slack) brew_install slack;;
      Docker) brew_install docker;;
      iTerm) brew_install iterm2;;
      Google\ Chrome) brew_install google-chrome;;
      IntelliJ\ Idea) brew_install intellij-idea;;
      Sourcetree) brew_install sourcetree;;
      Spotify) brew_install spotify;;
      **Skype) brew_install skype;;**
      *) echo "Add $1 to check_before_install() to install additional applications." ;;
    esac
```

Again, keep the switch case key captilaized because it reflects the application name under the /Application folder. Next, we will pass the _cask-name_ to the ```brew_install`` function inside the shell script. 


## **Conclusion** 

Hope this helps, happy coding!





