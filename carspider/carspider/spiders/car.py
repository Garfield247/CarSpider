# -*- coding: utf-8 -*-
import re
import scrapy
from carspider.items import CarspiderItem


class CarSpider(scrapy.Spider):
    name = 'car'
    # allowed_domains = ['price.pcauto.com.cn']
    # start_urls = ['http://price.pcauto.com.cn/']
    def start_requests(self):
        start_url = 'http://price.pcauto.com.cn/cars/'
        yield scrapy.Request(start_url,callback=self.parse)

    def parse(self, response):
        car_ids = list(set(re.findall(r'/(sg\d+)/',response.text)))
        for cid in car_ids:
            car_url = 'http://price.pcauto.com.cn/%s/'%cid
            yield scrapy.Request(car_url,callback=self.parse_info,meta={'cid':cid})

    def parse_info(self, response):
        item = CarspiderItem()
        car_name = response.xpath('.//div[@class="title"]/h1/text()').extract_first()
        item['brand'] = car_name.split('-')[0]
        # print(car_name.split('-'))
        item['version'] =  car_name.split('-')[-1]
        item['price'] = response.xpath('.//div[@class="price"]/p[@class="p1"]/em[@id="dfCtrId"]/text()').extract_first()
        item['car_score'] = response.xpath('.//p[@class="score"]/text()').extract_first()
        item['parameter'] = {''.join(p.xpath('./span/text()').extract()).rstrip(':'):'、'.join(p.xpath('.//a/text()').extract()) for p in response.xpath('.//div[@class="price"]/ul[@class="des"]/li/p')}
        comment_url = 'http://price.pcauto.com.cn/comment/%s/'%response.meta['cid']
        yield scrapy.Request(comment_url,callback=self.parse_comment,meta={'item':item})

    def process_rnt(self,string):
        if type(string) == str:
            return re.sub(r'[\r|\n|\t]','',string)

    def parse_comment(self, response):
        next_url = response.xpath('//a[@title="下一页"]/@href').extract_first()
        for comment in response.xpath('.//div[@class="scollbody"]/div[starts-with(@class,"litDy")]'):
            comments = {}
            comments['user_name'] = comment.xpath('.//div[@class="txBox"]/div[@class="txline"]/p/a/text()').extract_first()
            comments['comment_date'] = comment.xpath('.//div[@class="txBox"]/div[@class="txline"]/span/a/text()').extract_first().rstrip('发表')
            comments['car_type'] = comment.xpath('.//div[@class="txBox"]/div[@class="line"]/em[contains(text(),"购买车型")]/../a/text()').extract_first()
            comments['buy_date'] = comment.xpath('.//div[@class="txBox"]/div[@class="line"]/em[contains(text(),"购买时间")]/../text()').extract_first()
            comments['buy_location'] = comment.xpath('.//div[@class="txBox"]/div[@class="line"]/em[contains(text(),"购买地点")]/../text()').extract_first()
            comments['buy_merchant'] = self.process_rnt(comment.xpath('.//div[@class="txBox"]/div[@class="line"]/em[contains(text(),"购买商家")]/../text()').extract_first())
            comments['buy_price'] = comment.xpath('.//div[@class="txBox"]/div[@class="line"]/em[contains(text(),"裸车价格")]/../i/text()').extract_first()
            comments['qtrip'] = comment.xpath('.//div[@class="txBox"]/div[@class="line"]/em[contains(text(),"平均油耗")]/../i/text()').extract_first()
            comments['distance'] = comment.xpath('.//div[@class="txBox"]/div[@class="line"]/em[contains(text(),"行驶里程")]/../text()').extract_first()
            comments['grade'] = {li.xpath('./span/text()').extract_first():li.xpath('./b/text()').extract_first() for li in comment.xpath('.//div[@class="fzbox"]/ul/li')}
            comments['impression'] = comment.xpath('.//div[@class="rightBm"]/div[starts-with(@class,"toptit")]/a/text()').extract()
            # comments['advantage'] = comment.xpath('.//div[starts-with(@class,"conLit")]/b[contains(text(),"优点")]/../span/text()').extract_first()
            # comments['disadvantage'] = comment.xpath('.//div[starts-with(@class,"conLit")]/b[contains(text(),"缺点")]/../span/text()').extract_first()
            comments['appraise'] = {div.xpath('./b/text()').extract_first().rstrip(':'):div.xpath('./span/text()').extract_first() for div in comment.xpath('.//div[starts-with(@class,"conLit")]')}
            comments['upvote'] = comment.xpath('.//div[@class="lastLine"]/div[@class="rmaxd"]/a[starts-with(@id,"corners_good")]/em/text()').extract_first().lstrip('(').rstrip(')')
            item = response.meta['item']
            item['comments'] = comments
            yield item

        if next_url:
            yield scrapy.Request(url = 'http:'+next_url,callback=self.parse_comment,meta={'item':response.meta['item']})
