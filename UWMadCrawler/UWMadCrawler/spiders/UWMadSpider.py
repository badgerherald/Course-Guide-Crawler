#!/usr/bin/env python


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








from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from bs4 import BeautifulSoup
#When we run into UTF-8 characters
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy.http.request.form import FormRequest
from w3lib.url import urljoin_rfc
from scrapy.utils.response import get_base_url
import html5lib
import re #Use regex to clean up the soup


 
class CourseSpider(BaseSpider):
    name = "UWMad"
    curTerm = '1144' #Insert the term you wish to search for here! (Spring 2014 is 1144)

    start_urls = [
        'http://public.my.wisc.edu/portal/f/u124l1s4/normal/render.uP',
    ]
    def parse(self, response):
        yield FormRequest.from_response(response, formnumber=1, formdata={'termChoice': curTerm}, callback=self.parse_result_page)
    def parse_result_page(self, response):
      #Write to File
      filename = "Madison_Lectures.html"
      body = response.body
      body = re.sub('&nbsp;'," ",body)
      body = re.sub(r'\bcollapsed""><strong>Starts\b', 'collapsed"><strong>Starts',body)
      body = re.sub('(?s)<script(.*?)</script>', "",body)
      soup = BeautifulSoup(body, "html5lib") #doesn't work with BSoup
      pretty = soup.encode('ascii','ignore')
      file = open(filename,'w')
      file.write(str(pretty))

      for td_course in soup.findAll("td", { "class":"courseResultUL","align":"center"})[:5]: #got rid of [:5]
        course = td_course.parent
        tdata = course.find_all("td")
        #Skip the first 3, they hold nothing and are only there for bad website design
        department  = tdata[2].a["title"]
        course_num = tdata[3].get_text().strip()
        course_title = tdata[4].get_text().strip()
        credits = tdata[5].get_text().strip()
        desc = tdata[6].get_text().strip()
        last_taught = tdata[7].get_text().strip()
        # Now load sibling table, which contains descrip
        nextSibling = course.next_sibling.next_sibling #CourseResult tag

        description = nextSibling.contents[3].contents[1].get_text().strip()
        pReq = nextSibling.contents[3].contents[3].get_text().strip()
        
    # #Go up and  get the <tr> tha tholds our course
    


        print '>>>>>>>department>>>>>>>>>',department
        print '>>>>>>>>course num>>>>>>>>',course_num
        print '>>>>>>>>course title>>>>>>',course_title
        print '>>>>>>>>credits>>>>>>>>>>>',credits
        print '>>>>>>>>>desc>>>>>>>>>>>>>',desc
        print '>>>>>>last taught>>>>>>>>>',last_taught
        print '>>>>>>>>>crip>>>>>>>>>>>>>',description
        pReq = re.sub('Pre-Reqs:', "",pReq).decode('utf-8', 'ignore')
        print '>>>>>>Pre-Reqs   >>>>>>>>>',pReq
        print '=========================='

        


        #   #GRAB THE SECTION LINK 
        base_url = get_base_url(response)
        hxs = HtmlXPathSelector(response)
  
        # #Grab all the Section Links
        sections = hxs.select('//td[contains(@class, "sectionExpandColumn")]/a/@href').extract()
        for section_url in sections:
            yield Request(url = urljoin_rfc(base_url, section_url), callback=self.parse_section) 


      hxs = HtmlXPathSelector(response)
      pages = hxs.select('//div[contains(@class, "searchPagination")]/a[contains(text(), ">")]/@href').extract()
      print 'PAGES COUNT=',len(pages)
      counter = 0
      for page in pages:
          counter += 1
          hxs = HtmlXPathSelector(response)
          courses = hxs.select('//tr[contains(@class, "courseResult")]/td[5]/@text').extract()
          for course in courses:
            print '>>>>>>>>>>>>>>>>>>>>>>>>>>>',course
          yield Request(url=urljoin_rfc(get_base_url(response),page),callback=self.parse_result_page)
    def parse_section(self,response):

            

        #Throw it in beautifulSoup
        soup = BeautifulSoup(response.body)
        #Print it out in a text document for reference
        pretty = soup.prettify()
        filename = "practiceLecture"
        file = open(filename,'wb')
        file.write('>>>>>>>>>> SOUP <<<<<<<<<<<')
        pretty = soup.encode('ascii','ignore')
        file.write(str(pretty))
        #END PRINTING PROCESS ------------
        for tr in soup.find_all("tr", { "class":"detailsClassSection" }):
          print ':::::::::::::::::SECTION::::::::::::::::::::::'
          #Grab a list of all the td 's'
          tdata = tr.find_all("td")
          #GRAB THE FIRST td, otherwise known as the class_no
          class_no = tdata[0].get_text().strip()
          sec_no = tdata[1].strong.get_text().strip()
          session = tdata[2].get_text().strip()
          time = tdata[3].get_text().strip()
          place = tdata[4].get_text().strip()
          teacher =tdata[5].get_text().strip()
          credits = tdata[6].get_text().strip()
          #NUMBER 7 is ALL THE HONORS/INFO/NOTES. MUST BE PARSED SEPERATELY
          ########################################################
          openSeats = tdata[8].get_text().strip()
          #Find out if the section is open or not
          seat_status = tdata[9].get("data-enrollmentstatus")
          print '>>>>>>>class_no>>>>>>>>',class_no
          print '>>>>>>>sec_no>>>>>>>>>>',sec_no
          print '>>>>>>>session>>>>>>>>>',session
          print '>>>>>>>time>>>>>>>>>>>>',time
          print '>>>>>>>place>>>>>>>>>>>',place
          print '>>>>>>>teacher>>>>>>>>>',teacher
          print '>>>>>>>>credits>>>>>>>>',credits
          print '>>>>>>>>openSeats>>>>>>',openSeats
          print '>>>>>>>>Open?>>>>>>>>>>',seat_status
              
            

