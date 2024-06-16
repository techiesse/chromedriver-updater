# Chromedriver Updater

This is a very simple updater for chromedriver. The intent is to have a quick way to update the chromedriver whenever your Google Chrome browser gets updated and your Selenium scripts stop working because of mismatching versions.

# How it Works?

Selenium looks for webdrivers in certain locations to interact with the browser. In particular any location available in your `PATH` will allow Selenium to interact with the webdriver.

This tool installs the chromedriver in: `$HOME/bin` (`%HOME%\bin` on Windows) and assumes this directory is available in your PATH.

Once the chromedriver has been installed, Selenium will use it provided you don't have any other chromedriver version installed in a place with higher priority (like your current directory).

# Installation

## Environment

Python >= 3.8 is required.

Other than that the only external dependency is lib `requests`.

So make sure to `pip install requests`.

This tool was designed to be used with the system Python interpreter. That requires to install requests globally, which many people don't like. I don't mind doing it because I use requests for other puposes as well. If you don't like this approach feel free to create and use a virtual environment.

## Linux

At some point we may provide a command line installer using curl to download and install the package (like what is done in `pyenv`). But for now please follow the instructions below:

Download `chromedriver-update.py` to your machine, make it available in your path and rename it to `chromedriver-update`. A good place is `~/bin` (make sure it is in your `PATH`). Then fix the permissions and you're good to go.

```bash
$ mv chromedriver-update.py chromedriver-update
$ sudo chmod ug+x chromedriver-update
```

## Windows

Windows support is a bit rudimentary at the moment.

Simplest way to use the tool is clone this repository and then use your terminal to call Python with the script.

```cmd
> git clone git@github.com:techiesse/chromedriver-updater.git
```

Example in the usage section below.

Of course just copying `chromedriver-updater.py` to a directory and calling it from there also works.


# Usage

## Linux

```bash
$ chromedriver-update [version]
```

Note that the version is optional. If it's not provided the latest stable version will be installed.

If `version` is provided it must follow the format of chromedriver versions. It can be a partial string though.

If a partial version is provided the program will install the latest version that begins with the supplied string.

Example:
```bash
$ chromedriver-update
$ chromedriver -v
ChromeDriver 128.0.6540.0 (e2477df01e178d7f534086e37d2fcc024a1644e6-refs/branch-heads/6540@{#1})

$ chromedriver-update 126
$ chromedriver -v
ChromeDriver 126.0.6478.61 (8dc092df54ce9b93406cb7fec530eb297bc0b332-refs/branch-heads/6478_56@{#3})
```

Version 128.0.6540.0 is the latest stable at the date of writing this document.

## Windows

The behavior is the same as in Linux but in order to use the tool you call python passing the script:

```cmd
> python chromedriver-update.py [version]
```

Example:
```cmd
X:\path\to\repo> python chromedriver-update.py
X:\path\to\repo> chromedriver -v
ChromeDriver 128.0.6540.0 (e2477df01e178d7f534086e37d2fcc024a1644e6-refs/branch-heads/6540@{#1})
```