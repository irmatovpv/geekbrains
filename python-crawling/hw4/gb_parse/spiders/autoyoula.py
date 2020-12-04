import pymongo
import scrapy
from urllib.parse import unquote
import json
import base64


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']
    css_query = {
        'brands': '.TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink',
        'brand_page_pagination': '.Paginator_block__2XAPy a.Paginator_button__u1e7D'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = pymongo.MongoClient()['parse_11'][self.name]

    def parse(self, response, **kwargs):
        for link in  response.css(self.css_query['brands']):
            yield response.follow(link.attrib['href'], callback=self.brande_page_parse)

    def brande_page_parse(self, response, **kwargs):
        for page in response.css(self.css_query['brand_page_pagination']):
            yield response.follow(page.attrib['href'], callback=self.brande_page_parse)

        for item_link in response.css('article a.SerpSnippet_name__3F7Yu'):
            yield response.follow(item_link.attrib['href'], callback=self.ads_parse)

    def ads_parse(self, response):
        title = response.css('.AdvertCard_advertTitle__1S1Ak::text').get()
        images = [image.attrib['src'] for image in response.css('.PhotoGallery_photo__36e_r img')]
        description = response.css('.AdvertCard_descriptionInner__KnuRi::text').get()
        specs = {spec.css('.AdvertSpecs_label__2JHnS::text').get():spec.css('.AdvertSpecs_data__xK2Qx::text, .AdvertSpecs_data__xK2Qx a::text').get()
                 for spec in response.css('.AdvertSpecs_row__ljPcX')}
        data = json.loads(unquote(unquote(
            list(filter(lambda x: 'transitState' in x, [spec.get() for spec in response.css('script::text')]))[0].split(
                '"')[1])))
        data = data[1]
        data = dict(zip(data[::2], data[1::2]))
        data = data['advertCard'][1]
        data = dict(zip(data[::2], data[1::2]))
        seller_url = "https://youla.ru/user/{}".format(data['youlaId'])

        data = data['contacts'][1]
        data = dict(zip(data[::2], data[1::2]))
        data = data['phones'][1][0][1]
        data = dict(zip(data[::2], data[1::2]))
        phone = base64.b64decode(base64.b64decode(data['phone'])).decode("utf-8")

        self.db.insert_one(
            {
                'title': title,
                'images': images,
                'description': description,
                'url': response.url,
                'specs': specs,
                'seller_url': seller_url,
                'phone': phone
            }
        )