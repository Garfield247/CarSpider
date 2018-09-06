# -*- coding: utf-8 -*-
import re
import json
import copy
import scrapy
from carspider.items import PhonespiderItem
from scrapy import Selector

class Phone2Spider(scrapy.Spider):
    name = 'phone2'
    def start_requests(self):
        for i in range(125):
            url = 'http://product.pconline.com.cn/mobile/list_%ds1.shtml'%int(i*25)
            yield scrapy.Request(url,callback=self.parse)

    def parse(self, response):
        for li in response.xpath('.//ul[@id="JlistItems"]/li'):
            item = PhonespiderItem()
            item['phone_name'] = li.xpath('//div[@class="item-title"]/h3/a[@class="item-title-name"]/text()').extract_first()
            item['parameter'] = { l.xpath('./span/text()').extract_first().rstrip('：'):l.xpath('./em/text()').extract_first() for l in li.xpath('//ul[@class="item-specs"]/li') if l.xpath('./span') }
            item['reference_price'] = li.xpath('.//div[starts-with(@class,"price")]/a/text()').extract_first()
            info_url = response.urljoin(li.xpath('//div[@class="item-title"]/h3/a[@class="item-title-name"]/@href').extract_first())
            yield scrapy.Request(info_url,callback=self.parse_info,meta={'item':item})


    def parse_info(self, response):
        item = response.meta['item']
        item['phone_brand'] = response.xpath('.//div[@class="crumb"]/a[4]/@title').extract_first().rstrip('手机大全')
        pid = re.findall(r'/(\d+).html', response.url)[0]
        comments_url = 'http://pdcmt.pconline.com.cn/front/2015/mtp-list.jsp?productId=%s&filterBy=-1&itemCfgId=-1&order=2&pageNo=1'%str(pid)
        yield scrapy.Request(comments_url,callback=self.parse_comments,meta={'item':item})

    def process_rnt(self, string):
        if type(string) == str:
            return re.sub(r'[\r|\n|\t]','', string).split('：')[-1]
        else:
            return None


    def parse_comments(self, response):
        # print(response.text)
        pgnum = re.findall(r'pageNo=(\d+)', response.url)[0]
        # print(next_url)
        for li in response.xpath('/html/body/ul/li'):
            item = response.meta['item']
            comments = {}
            comments['comment_user'] = li.xpath('.//i[@class="tit"]/text()').extract_first()
            comments['buy_price'] = self.process_rnt(li.xpath('.//dd[contains(text(),"价格")]/text()').extract_first())#.lstrip('价格：')
            comments['buy_date'] = self.process_rnt(li.xpath('.//dd[contains(text(),"时间")]/text()').extract_first())#.lstrip('时间：')
            comments['buy_address'] = self.process_rnt(li.xpath('.//dd[contains(text(),"渠道")]/text()').extract_first())#.lstrip('渠道：')
            comments['appraise'] = li.xpath('.//dt/strong[@class="title"]/a/text()').extract_first()
            comments['score'] = li.xpath('.//strong[@class="goal"]/text()').extract_first()
            comments['grade'] = dict(s.split('：') for s in li.xpath('.//ul[@class="goal-detail"]/li/text()').extract())
            comment = { l.xpath('./span/text()').extract_first():l.xpath('./text()').extract_first() for l in li.xpath('.//div[@class="cmt-text"]/ul[@class="clearfix"]/li')}
            comments['comment'] = li.xpath('string(.//div[@class="cmt-text"]/p[@class="text"])').extract_first() if not comment else comment
            comments['upvote'] = li.xpath('.//a[@class="good"]/span/text()').extract_first()
            item['comments'] = comments
            yield item
        if len(response.xpath('/html/body/ul/li'))>0:
            next_num = int(pgnum)+1
            next_url = re.sub(r'pageNo=\d+', 'pageNo=%d'%next_num, response.url)
            yield scrapy.Request(next_url,callback=self.parse_comments,meta={'item':response.meta['item']})




