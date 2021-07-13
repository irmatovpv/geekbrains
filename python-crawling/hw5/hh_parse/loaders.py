from scrapy.loader import ItemLoader
from .items import VacancyItem, AuthorItem
from itemloaders.processors import TakeFirst, MapCompose, Join
from urllib.parse import urljoin
import json
import base64
from scrapy import Selector

import json

def js_decoder_salary(text):
    data = json.loads(text)
    data = data['vacancyView']['compensation']
    if data['from'] and data['to']:
        salary = "от {} до {} {}".format(data['from'], data['to'], data['currencyCode'])
    else:
        salary = "{} {}".format(data['to'], data['currencyCode'])
    return salary

def js_decoder_key_skill(text):
    data = json.loads(text)
    data = data['vacancyView']['keySkills']
    return data['keySkill']

def js_decoder_description(text):
    data = json.loads(text)
    description = data['vacancyView']['description']
    return description

def author_decode(text):
    return urljoin('https://hh.ru/', text)

class VacancyLoader(ItemLoader):
    default_item_class = VacancyItem
    title_out = TakeFirst()
    salary_in = MapCompose(js_decoder_salary)
    salary_out = TakeFirst()
    key_skill_in = MapCompose(js_decoder_key_skill)
    # key_skill_out = TakeFirst()
    description_in = MapCompose(js_decoder_description)
    description_out = TakeFirst()
    author_url_in = MapCompose(author_decode)
    author_url_out = TakeFirst()
    url_out = TakeFirst()

def parse_field_of_activity(field_of_activity):
    return field_of_activity.split(',')

class AuthorLoader(ItemLoader):
    default_item_class = AuthorItem
    name_out = Join()
    site_url_out = TakeFirst()
    field_of_activity_in = MapCompose(parse_field_of_activity)
    author_description_out = TakeFirst()
    url_out = TakeFirst()
