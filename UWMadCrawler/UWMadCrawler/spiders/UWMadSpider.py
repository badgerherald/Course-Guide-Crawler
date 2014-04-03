# !/usr/bin/env python


# Program: UW-Madison Course Crawler
# __author__ = "Joseph Kelley"
# __copyright__ = "Copyright 2014"
# __license__ = "MIT"
# __version__ = "0.7"
# __maintainer__ = "Joseph Kelley"
# __email__ = "jckelley2@wisc.edu"
# __status__ = "Beta"


# This program will crawl the UW-Madison public facing course register. It will provide a live update
# of what classes are closed, waitlisted, or how many spots are still available. Note that this program is
# not hooked up to any database whatsoever, so if you wish to save the information crawled and not just print it
# to the screen, you will have to do so on your own.

from bs4 import BeautifulSoup
from datetime import datetime
import html5lib
import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy.http.request.form import FormRequest
from scrapy.utils.response import get_base_url
from urlparse import urljoin

from UWMadCrawler.items import CourseItem, SectionItem


class CourseSpider(BaseSpider):
    name = "UWMad"
    curTerm = '1152'  # (Fall 2014 is 1152)
    classes = []

    start_urls = [
        'http://public.my.wisc.edu/portal/f/u124l1s4/normal/render.uP',
    ]

    def parse(self, response):
        yield FormRequest.from_response(response, formnumber=1, formdata={'termChoice': self.curTerm, 'resultsPerPage': '200'},
                                        callback=self.parse_result_page)

    def parse_result_page(self, response):
        body = response.body
        body = re.sub('&nbsp;', " ", body)
        body = re.sub(r'\bcollapsed""><strong>Starts\b', 'collapsed"><strong>Starts', body)
        body = re.sub('(?s)<script(.*?)</script>', "", body)
        soup = BeautifulSoup(body, "html5lib")

        last_updated_text = soup.find("span", {"class": "dataRefreshTimestamp"}).get_text().strip()
        last_updated_unix = datetime.strptime(last_updated_text, "%I:%M%p %b %d, %Y").strftime("%s")

        # All courseResultULs are results, but not all CourseResults are. Use the courseResultsUL to get the
        # parent courseResult, which is guaranteed to be a real result
        for td_course in soup.findAll("td", {"class": "courseResultUL", "align": "center"}):
            course = td_course.parent
            tdata = course.find_all("td")
            # Skip the first 2, they hold nothing
            department = tdata[2].a["title"]
            course_num = tdata[3].get_text().strip()
            course_title = tdata[4].get_text().strip()
            num_credits = tdata[5].get_text().strip()
            desc = tdata[6].get_text().strip()
            last_taught = tdata[7].get_text().strip()

            # Now load sibling table, which contains course description and prerequisites
            nextSibling = course.next_sibling.next_sibling
            description = nextSibling.contents[3].contents[1].get_text().strip()
            pReq = nextSibling.contents[3].contents[3].get_text().strip()
            pReq = re.sub('Pre-Reqs:', "", pReq).decode('utf-8', 'ignore')

            base_url = get_base_url(response)

            current_class = CourseItem(
                department=department,
                course_num=course_num,
                course_title=course_title,
                credits=num_credits,
                desc=desc,
                last_taught=last_taught,
                description=description,
                pReq=pReq,
            )
            yield current_class

            # Scrape class pages to get sections for current class
            section_url = tdata[4].find("a")["href"]
            section = Request(url=urljoin(base_url, section_url), callback=self.parse_section)
            section.meta['department'] = department
            section.meta['course_num'] = course_num
            section.meta['course_title'] = course_title
            section.meta['last_updated'] = last_updated_unix
            yield section

        # Advance to next page
        next_page_url = soup.find("a", {"title": "go to next page"})["href"]
        if next_page_url:
            yield Request(url=urljoin(get_base_url(response), next_page_url), callback=self.parse_result_page)

    def parse_section(self, response):
        soup = BeautifulSoup(response.body)
        for tr in soup.find_all("tr", {"class": "detailsClassSection"}):
            tdata = tr.find_all("td")
            class_no = tdata[0].get_text().strip()
            sec_no = tdata[1].strong.get_text().strip()
            session = tdata[2].get_text().strip()
            time = tdata[3].get_text().strip()
            place = tdata[4].get_text().strip()
            teacher = tdata[5].get_text().strip()
            num_credits = tdata[6].get_text().strip()
            # TODO: Parse honors information in tdata[7]?
            openSeats = tdata[8].get_text().strip()
            seat_status = tdata[9].get("data-enrollmentstatus")

            current_section = SectionItem(
                department=response.meta['department'],
                course_num=response.meta['course_num'],
                course_title=response.meta['course_title'],
                last_updated=response.meta['last_updated'],
                class_no=class_no,
                sec_no=sec_no,
                session=session,
                time=time,
                place=place,
                teacher=teacher,
                credits=num_credits,
                openSeats=openSeats,
                seat_status=seat_status
            )

            yield current_section