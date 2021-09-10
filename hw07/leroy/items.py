# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst  # Подключаемые обработчики


def process_price(value):  # Функция для обработки цен
    value_clear = value.replace(' ', '')
    try:
        return int(value_clear)
    except:
        return value


def specification_definition(value):  # Функция для обработки характеристик
    value_clear = value.replace('\n                ', '').replace('\n            ', '')
    return value_clear


class LeroyItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())  # Теперь у поля есть обработчики
    price = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())
    currency = scrapy.Field(output_processor=TakeFirst())
    unit = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    specification = scrapy.Field()
    specification_term = scrapy.Field()
    specification_definition = scrapy.Field(input_processor=MapCompose(specification_definition))
    url = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field()
