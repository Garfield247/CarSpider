import re
import os
import json
import requests
from lxml import etree

class Phone_crawl(object):
    """docstring for Phone_crawl"""
    def __init__(self):
        super(Phone_crawl, self).__init__()
        self.start_url = 'http://（detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_2_0_1.html'
        self.headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Cache-Control':'max-age=0',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
        self.comment_headers = {
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Connection':'keep-alive',
            'Host':'detail.zol.com.cn',
            'Cookie':'gr_user_id=587d1958-9234-4bdb-9e20-d5a106675484;ip_ck=48CE5/r0j7QuNDc1MDAzLjE1MzUzNTQxMjA%3D;realLocationId=1;userFidLocationId=1;listSubcateId=57;visited_subcateId=57;visited_subcateProId=57-0;visited_serachKw=%u56FD%u7F8EU9;z_pro_city=s_provice%3Dbeijing%26s_city%3Dbeijing;userProvinceId=1;userCityId=475;userCountyId=0;userLocationId=1;lv=1535590487;vn=10;Hm_lvt_ae5edc2bc4fc71370807f6187f0a2dd0=1535427097,1535534227,1535534495,1535590488;Hm_lpvt_ae5edc2bc4fc71370807f6187f0a2dd0=1535590488;Adshow=1;gr_session_id_9b437fe8881a7e19=5725a985-3355-43b2-beb2-2b563e04895b;gr_session_id_9b437fe8881a7e19_5725a985-3355-43b2-beb2-2b563e04895b=true;questionnaire_pv=1535587204;z_day=izol102591%3D2%26izol102569%3D2%26rdetail%3D3',
            'Referer':'',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest',
        }
        self.file_path = './phone.json'

    def open_spider(self):
        print('爬虫启动')
        self.fp = open(self.file_path,'a',encoding='utf-8')
        print('初始化完成')

    def _hanlder_request(self,url,headers):

        response = requests.get(url=url,headers=headers)
        return response

    def _xpath(self,response):
        if type(response) == str:
            xpath = etree.HTML(response)
        elif type(response) == requests.models.Response:
            xpath = etree.HTML(response.text)
        else:
            pass
        return xpath

    def _save_item(self,item):
        data = json.dumps(item,ensure_ascii=False)
        self.fp.write(data+'\n')


    def crawl(self,url):
        print('获取手机列表')
        response = self._hanlder_request(url,self.headers)
        html = self._xpath(response)
        phone_list = ['http://detail.zol.com.cn%s'%url for url in html.xpath('.//ul[@id="J_PicMode"]/li/h3/a/@href')]
        self.crawl_info(phone_list)
        if len(html.xpath('.//div[@class="pagebar"]/a[@class="next"]/@href'))>0:
            next_url = 'http://detail.zol.com.cn%s'%(html.xpath('.//div[@class="pagebar"]/a[@class="next"]/@href')[0])
            print('开始下一轮采集')
            self.crawl(next_url)

    def crawl_info(self,url_list):
        print('采集手机信息')
        for url in url_list:
            response = self._hanlder_request(url,self.headers)
            html = self._xpath(response)
            item = {}
            try:
                item['phone_name'] = html.xpath('//h1[@class="product-model__name"]/text()')[0]
                item['referrncr_price'] = html.xpath('//b[@class="price-type"]/text()')[0]
                item['parameter'] = {l.xpath('./span/text()')[0]:l.xpath('./text()')[0] for l in html.xpath('//div[@class="section-content"]/ul[starts-with(@class,"product-param-item")]/li/p')}
                print(item)
                if len(html.xpath('.//a[contains(text(), "查看全部点评")]/@href'))>0:
                    comment_herf = html.xpath('.//a[contains(text(), "查看全部点评")]/@href')[0]
                    self.comment_headers['Referer'] = 'http://detail.zol.com.cn%s'%comment_herf
                    self.crawl_comment(comment_herf, item)
            except:
                continue

    def crawl_comment(self,url,item):
        print('采集评论')
        proid = re.findall(r'/\d+/(\d+)/review.shtml', url)[0]
        print(proid)
        comment_url = 'http://detail.zol.com.cn/xhr4_Review_GetList_proId='+proid+'%5Elevel=0%5Efilter=1%5Epage=1.html'
        print(comment_url)
        response = self._hanlder_request(comment_url,self.comment_headers)
        ｐ品牌品牌品　　　　　　　　　　　　　　
            print('--------=-=-=-=-=-=-=-=-=--------')
            print(json.loads(r.text).get('nextPage'))
            print('--------=-=-=-=-=-=-=-=-=-=------')

    def close_spider(self):
        self.fp.close()

if __name__ == '__main__':
    p = Phone_crawl()
    p.open_spider()
    p.crawl(p.start_url)
    p.close_spider()





