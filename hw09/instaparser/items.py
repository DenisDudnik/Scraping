# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    profile_pic_url = scrapy.Field()
    follower_id = scrapy.Field()
    follower_name = scrapy.Field()
    following_to_id = scrapy.Field()
    following_to_name = scrapy.Field()
    _id = scrapy.Field()
