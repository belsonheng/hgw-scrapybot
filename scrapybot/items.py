# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Restaurant(scrapy.Item):
    town = scrapy.Field()
    url = scrapy.Field()
    business_id = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    postal = scrapy.Field()
    type = scrapy.Field()
    price_range = scrapy.Field()
    cuisine = scrapy.Field()

class Review(scrapy.Item):
    business_id = scrapy.Field()
    review_user = scrapy.Field()
    review_date = scrapy.Field()
    review_title = scrapy.Field()
    review_text = scrapy.Field()
    review_url = scrapy.Field()
