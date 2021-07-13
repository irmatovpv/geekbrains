from urllib.parse import urljoin

from scrapy.loader import ItemLoader
from .items import AutoYoulaItem
from itemloaders.processors import TakeFirst, MapCompose
from urllib.parse import unquote
import json
import base64
from scrapy import Selector

import json

def get_specifications(item):
    tag = Selector(text=item)
    return {tag.xpath('//div[contains(@class, "label")]/text()').get(): tag.xpath('//div[contains(@class, "data")]//text()').get()}

def get_specifications_out(data):
    result = {}
    for item in data:
        result.update(item)
    return result

def js_decoder_author(text):
    data = json.loads(unquote(unquote(text.split('"')[1])))
    data = data[1]
    data = dict(zip(data[::2], data[1::2]))
    data = data['advertCard'][1]
    data = dict(zip(data[::2], data[1::2]))
    seller_url = "https://youla.ru/user/{}".format(data['youlaId'])

    return seller_url

class AutoyoulaLoader(ItemLoader):
    default_item_class = AutoYoulaItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    description_out = TakeFirst()
    autor_in = MapCompose(js_decoder_author)
    autor_out = TakeFirst()
    specifications_in = MapCompose(get_specifications)
    specifications_out = get_specifications_out