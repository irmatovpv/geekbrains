import pymongo
import scrapy
from urllib.parse import unquote
import json
import base64
from ..loaders import AutoyoulaLoader

class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']

    xpath_query = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'brand_page_pagination': '//div[contains(@class, "Paginator_block")]//a[contains(@class, "Paginator_button")]/@href',
        'ads': '//article//a[contains(@class, "SerpSnippet_name")]/@href'
    }
    item_template = {
        'title': '//div[@data-target="advert-title"]/text()',
        'images': '//figure[contains(@class, "PhotoGallery_photo")]//img/@src',
        'description': '//div[contains(@class, "AdvertCard_descriptionInner")]/text()',
        'autor': '//script[contains(text(), "transitState")]/text()',
        'specifications': '//div[contains(@class, "AdvertCard_specs")]/div/div[contains(@class, "AdvertSpecs_row")]'
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        for link in response.xpath(self.xpath_query['brands']):
            yield response.follow(link, callback=self.brande_page_parse)

    def brande_page_parse(self, response, **kwargs):
        for page in response.xpath(self.xpath_query['brand_page_pagination']):
            yield response.follow(page, callback=self.brande_page_parse)

        for item_link in response.xpath(self.xpath_query['ads']):
            yield response.follow(item_link, callback=self.ads_parse)

    def ads_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value('url', response.url)

        for name, selector in self.item_template.items():
            loader.add_xpath(name, selector)

        yield  loader.load_item()

        # title = response.css('.AdvertCard_advertTitle__1S1Ak::text').get()
        # images = [image.attrib['src'] for image in response.css('.PhotoGallery_photo__36e_r img')]
        # description = response.css('.AdvertCard_descriptionInner__KnuRi::text').get()
        # specs = {spec.css('.AdvertSpecs_label__2JHnS::text').get(): spec.css(
        #     '.AdvertSpecs_data__xK2Qx::text, .AdvertSpecs_data__xK2Qx a::text').get()
        #          for spec in response.css('.AdvertSpecs_row__ljPcX')}
        # data = json.loads(unquote(unquote(
        #     list(filter(lambda x: 'transitState' in x, [spec.get() for spec in response.css('script::text')]))[0].split(
        #         '"')[1])))
        # data = data[1]
        # data = dict(zip(data[::2], data[1::2]))
        # data = data['advertCard'][1]
        # data = dict(zip(data[::2], data[1::2]))
        # seller_url = "https://youla.ru/user/{}".format(data['youlaId'])
        #
        # data = data['contacts'][1]
        # data = dict(zip(data[::2], data[1::2]))
        # data = data['phones'][1][0][1]
        # data = dict(zip(data[::2], data[1::2]))
        # phone = base64.b64decode(base64.b64decode(data['phone'])).decode("utf-8")
        #
        # yield {
        #     'title': title,
        #     'images': images,
        #     'description': description,
        #     'url': response.url,
        #     'specs': specs,
        #     'seller_url': seller_url,
        #     'phone': phone
        # }
