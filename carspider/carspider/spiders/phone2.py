# -*- coding: utf-8 -*-
import scrapy


class Phone2Spider(scrapy.Spider):
    name = 'phone2'
    allowed_domains = ['http://product.pconline.com.cn']
    start_urls = ['http://http://product.pconline.com.cn/']

    def parse(self, response):
        pass
