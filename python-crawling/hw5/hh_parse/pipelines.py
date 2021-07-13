# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


from pymongo import MongoClient

class HHParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_12']

    def process_item(self, item, spider):
        colleciton = self.db[item.item_name]
        colleciton.insert_one(item)
        return item