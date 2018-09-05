# -*- coding: utf-8 -*-
import re
import json
import copy
import scrapy
from carspider.items import PhonespiderItem
from scrapy import Selector


class PhoneSpider(scrapy.Spider):
    name = 'phone'

    def start_requests(self):
        start_url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_1.html'
        yield scrapy.Request(start_url,callback=self.parse)

    def parse(self, response):
        next_href = response.xpath('.//a[@class="next"]/@href').extract_first()
        for div in response.xpath('.//div[starts-with(@class,"list-item")]'):
            item = PhonespiderItem()
            item['phone_name'] = response.xpath('.//div[@class="pro-intro"]/h3/a/text()').extract_first()
            item['parameter'] ={li.xpath('./span/text()').extract_first():li.xpath('./@title').extract_first() for li in response.xpath('.//div[starts-with(@class,"list-item")]/div[@class="pro-intro"]/ul[starts-with(@class,"param")]/li')}
            info_url = response.urljoin(response.xpath('.//div[@class="pro-intro"]/h3/a/@href').extract_first())
            # print(url)
            yield scrapy.Request(info_url,callback=self.parse_info,meta={'item':item})
        if next_href:
            next_url = 'http://detail.zol.com.cn%s'%next_href
            yield scrapy.Request(next_url,callback=self.parse)

    def parse_info(self, response):
        item = response.meta['item']
        item['phone_brand'] = response.xpath('.//a[@id="_j_breadcrumb"]/text()').extract_first()
        item['reference_price'] = response.xpath('//b[@class="price-type"]/text()').extract_first()
        comment_href = response.xpath('.//a[contains(text(), "查看全部点评")]/@href').extract_first()
        if comment_href:
            proid = re.findall(r'index(\d+)', response.url)[0]
            comment_url = 'http://detail.zol.com.cn/xhr4_Review_GetList_proId='+proid+'%5Elevel=0%5Efilter=1%5Epage=1.html'
            yield scrapy.Request(comment_url,callback=self.parse_comment,meta={'item':item})

    def parse_comment(self, response):
        pgnum = re.findall(r'page=(\d+).html', response.url)[0]
        result = json.loads(response.text)
        content = result['list']
        html = Selector(text=content)
        for comment in html.xpath('.//div[@class="comments-item"]'):
            item = response.meta['item']
            comments = {}
            comments['comment_user'] = comment.xpath('//div[@class="comments-user"]/a[@class="name"]/text()').extract_first()
            comments['buy_price'] = comment.xpath('//div[@class="comments-user"]/p[contains(text(), "价格")]/text()').extract_first().split(':')[-1] if comment.xpath('//div[@class="comments-user"]/p[contains(text(), "价格")]/text()').extract_first() else None
            comments['buy_date'] = comment.xpath('//div[@class="comments-user"]/p[contains(text(), "时间")]/text()').extract_first().split(':')[-1] if comment.xpath('//div[@class="comments-user"]/p[contains(text(), "时间")]/text()').extract_first() else None
            comments['buy_address'] = comment.xpath('//div[@class="comments-user"]/p[contains(text(), "地点")]/text()').extract_first().split(':')[-1] if comment.xpath('//div[@class="comments-user"]/p[contains(text(), "地点")]/text()').extract_first() else None
            comments['appraise'] = comment.xpath('.//div[@class="title"]/a/text()').extract_first()
            comments['score'] = comment.xpath('.//div[starts-with(@class,"score")]/span/text()').extract_first()
            comments['grade'] ={grade.xpath('./text()').extract_first().rstrip(':'):grade.xpath('./em/text()').extract_first() for grade in comment.xpath('.//div[@class="single-score"]/p/span') }
            comments['advantage'] = comment.xpath('.//strong[@class="good"]/../p/text()').extract_first()
            comments['disadvantage'] = comment.xpath('.//strong[@class="bad"]/../p/text()').extract_first()
            comments['upvote'] = int(re.findall(r'(\d+)赞',comment.xpath('.//a[@class="_j_review_vote"]').extract_first())[0]) if len(re.findall(r'(\d+)赞',comment.xpath('.//a[@class="_j_review_vote"]').extract_first()))>0 else 0
            item['comments'] = comments
            yield item
        if not result.get('isEnd'):
            next_num = int(pgnum)+1
            next_url = re.sub(r'page=\d+.html', 'page=%d.html'%next_num, response.url)
            print(next_url)
            yield scrapy.Request(next_url,callback=self.parse_comment,meta={'item':response.meta['item']})
