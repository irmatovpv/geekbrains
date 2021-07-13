# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HhParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class VacancyItem(scrapy.Item):
    item_name = 'vacancy'
    _id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    key_skill = scrapy.Field()
    author_url = scrapy.Field()
    url = scrapy.Field()


class AuthorItem(scrapy.Item):
    item_name = 'author'
    _id = scrapy.Field()
    name = scrapy.Field()
    site_url = scrapy.Field()
    field_of_activity = scrapy.Field()
    author_description = scrapy.Field()
    url = scrapy.Field()