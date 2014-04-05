UW-Madison Course Guide Crawler
===============================

A web scraper that reads the information from the [public UW-Madison course guide](http://public.my.wisc.edu/portal/f/u124l1s4/normal/render.uP)
and saves it in a SQLite database. It uses [Scrapy](http://scrapy.org/), an open source web scraping library designed using Python.
To learn more about it, check out its [documentation](http://doc.scrapy.org/en/latest/intro/overview.html)


## Installation

Before you start, you'll need to install a few system libraries:

- Python 2.7
- libxml2 / libxslt
- libffi
- OpenSSL
- SQLite 3

You'll also need a C compiler. The [Scrapy installation notes](http://doc.scrapy.org/en/latest/intro/install.html) will
help you get started.

Then, clone the repo and install the project's dependencies with pip:

    pip install -r requirements.txt

## Getting started

Currently the only way to run the crawler is with the `scrapy` command-line tool. This must be run inside the `UWMadCrawler`
directory, as so:

    cd UWMadCrawler
    scrapy crawl UWMad

This will crawl the website and print out the courses on the register.

It will create a SQLite database inside this directory, named `classes.db`. Courses and their sections are saved into
different tables, along with (almost) all of the information available about them in the course guide. Sections are
related to courses by sharing the same department, course number, and course title.

Courses are not expected to change very often, so the scraper will avoid re-adding them if they are already
in the database. However, sections are saved along with the time of last modification found on the course guide itself.
This means that you can scrape multiple times and (hopefully!) have the right thing happen.

## Notes

This program is released under the MIT license. Copyright (c) 2014 The Badger Herald, Inc.

This program is a fork of the [UWMadCrawler](https://github.com/jckelley/UWMadCrawler) by [Joe Kelley](https://github.com/jckelley),
originally released under the MIT license (see NOTICE).







