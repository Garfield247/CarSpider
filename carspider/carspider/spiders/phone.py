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
        for i in range(1,38):
            start_url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_%d.html'%i
            yield scrapy.Request(start_url,callback=self.parse)

    def parse(self, response):
        # next_href = response.xpath('.//a[@class="next"]/@href').extract_first()
        # print(next_href)
        for div in response.xpath('.//div[starts-with(@class,"list-item")]'):
            item = PhonespiderItem()
            item['phone_name'] = response.xpath('.//div[@class="pro-intro"]/h3/a/text()').extract_first()
            item['parameter'] ={li.xpath('./span/text()').extract_first():li.xpath('./@title').extract_first() for li in response.xpath('.//div[starts-with(@class,"list-item")]/div[@class="pro-intro"]/ul[starts-with(@class,"param")]/li')}
            info_url = response.urljoin(response.xpath('.//div[@class="pro-intro"]/h3/a/@href').extract_first())
            # print(url)
            yield scrapy.Request(info_url,callback=self.parse_info,meta={'item':item})
        # if next_href:
        #     next_url = response.urljoin(next_href)
        #     yield scrapy.Request(next_url,callback=self.parse)

    def parse_info(self, response):
        item = response.meta['item']
        item['phone_brand'] = response.xpath('.//a[@id="_j_breadcrumb"]/text()').extract_first().rstrip('手机')
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
        for div in html.xpath('.//div[@class="comments-item"]'):
            item = response.meta['item']
            comments = {}
            comments['comment_user'] = div.xpath('//div[@class="comments-user"]/a[@class="name"]/text()').extract_first()
            comments['buy_price'] = div.xpath('//div[@class="comments-user"]/p[contains(text(), "价格")]/text()').extract_first().split(':')[-1] if div.xpath('//div[@class="comments-user"]/p[contains(text(), "价格")]/text()').extract_first() else None
            comments['buy_date'] = div.xpath('//div[@class="comments-user"]/p[contains(text(), "时间")]/text()').extract_first().split(':')[-1] if div.xpath('//div[@class="comments-user"]/p[contains(text(), "时间")]/text()').extract_first() else None
            comments['buy_address'] = div.xpath('//div[@class="comments-user"]/p[contains(text(), "地点")]/text()').extract_first().split(':')[-1] if div.xpath('//div[@class="comments-user"]/p[contains(text(), "地点")]/text()').extract_first() else None
            comments['appraise'] = div.xpath('.//div[@class="title"]/a/text()').extract_first()
            comments['score'] = div.xpath('.//div[starts-with(@class,"score")]/span/text()').extract_first()
            comments['grade'] ={grade.xpath('./text()').extract_first().rstrip(':'):grade.xpath('./em/text()').extract_first() for grade in div.xpath('.//div[@class="single-score"]/p/span') }
            comment = { d.xpath('./strong/text()').extract_first().rstrip('：'):d.xpath('./p/text()').extract_first() for d in div.xpath('.//div[@class="content-inner"]/div[@class="words"]')}
            comments['comment'] = div.xpath('.//div[@class="words-article"]/p/text()').extract_first() if not comment else comment
            comments['upvote'] = int(re.findall(r'(\d+)赞',div.xpath('.//a[@class="_j_review_vote"]').extract_first())[0]) if len(re.findall(r'(\d+)赞',div.xpath('.//a[@class="_j_review_vote"]').extract_first()))>0 else 0
            item['comments'] = comments
            yield item
        if not result.get('isEnd'):
            next_num = int(pgnum)+1
            next_url = re.sub(r'page=\d+.html', 'page=%d.html'%next_num, response.url)
            print(next_url)
            yield scrapy.Request(next_url,callback=self.parse_comment,meta={'item':response.meta['item']})

