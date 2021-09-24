# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import hashlib
from scrapy.utils.python import to_bytes


class LeroyPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroy

    def process_item(self, item, spider):  # В этот item попадаем после, потому что более низкий приоритет в settings
        # photos = scrapy.Field()
        item['specification'] = dict(zip(item['specification_term'], item['specification_definition']))
        item['_id'] = hashlib.sha256(item['url'].encode()).hexdigest()
        collection = self.mongo_base[spider.name]
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        return item


class LeroyPhotosPipeline(ImagesPipeline):  # В этот item попадаем сначала,потому что более высокий приоритет в settings
    def get_media_requests(self, item, info):  # Точка входа в класс
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)  # Скачиваем здесь фото и результат можно увидеть в методе item completed
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if
                          itm[0]]  # Здесь проверяем результат скачивания и сохраняем внутри item
        return item

    def file_path(self, request, response=None, info=None, *, item=None): # Метод для изменения места скачивания файлов
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        addition_path = item.get('url').replace('https://leroymerlin.ru/product/', '')
        return f'full/{addition_path}{image_guid}.jpg'
