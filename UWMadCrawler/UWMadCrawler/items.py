# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


class CourseItem(Item):
    item_type = "course"
    department = Field()
    course_num = Field()
    course_title = Field()
    credits = Field()
    desc = Field()
    last_taught = Field()
    description = Field()
    pReq = Field()


class SectionItem(Item):
    item_type = "section"
    department = Field()
    course_num = Field()
    course_title = Field()
    last_updated = Field()
    class_no = Field()
    sec_no = Field()
    session = Field()
    time = Field()
    place = Field()
    teacher = Field()
    credits = Field()
    openSeats = Field()
    seat_status = Field()
