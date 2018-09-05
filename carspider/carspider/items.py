# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CarspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    brand = scrapy.Field()
    version = scrapy.Field()
    price = scrapy.Field()
    car_score = scrapy.Field()
    parameter = scrapy.Field()
    comments = scrapy.Field()

class PhonespiderItem(scrapy.Item):
    """docstring for PhonespiderItem"""
    phone_brand = scrapy.Field()
    phone_name = scrapy.Field()
    reference_price = scrapy.Field()
    parameter = scrapy.Field()
    comments = scrapy.Field()
