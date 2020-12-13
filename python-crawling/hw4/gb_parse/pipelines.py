# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_11']

    def process_item(self, item, spider):
        colleciton = self.db[spider.name]
        colleciton.insert_one(item)
        return item


class GbImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        images = item.get('images')
        for image in images:
            yield Request(image)

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results]
        return item