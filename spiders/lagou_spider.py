# -*- coding: utf-8 -*-
import datetime
import os
import time
import scrapy
import requests
from urllib.parse import urlencode
import json
from bloom_filter import BloomFilter
from jobscrawler_lagou.items import JobscrawlerLagouItem

class LagouSpiderSpider(scrapy.Spider):
    name = 'lagou_spider'
    allowed_domains = ['lagou.com']
    fake_url = 'http://quotes.toscrape.com/'
    start_url_tags = ['大数据'] #['数据分析', '数据挖掘', '算法', '机器学习', '深度学习', '人工智能']
    url_start = 'https://m.lagou.com/search.html'
    json_ajax_url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
    headers = {
        "Host": "www.lagou.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Anit-Forge-Token": "None",
        "X-Anit-Forge-Code": "0",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Length": "93",
        "Origin": "https://www.lagou.com",
        "Connection": "keep-alive",
        "Referer": "https://www.lagou.com/jobs/list_%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90?labelWords=&fromSearch=true&suginput=",
        #"Cookie": "user_trace_token=20200328191626-2ae022e3-31c1-433f-a949-fb8be37b71fe; LGUID=20200328191630-9f221e7e-cd53-4856-82cc-37b08a608a5d; _ga=GA1.2.1166673721.1585394191; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2217120db89a7e-01a9c595c1732e-4c302f7e-1327104-17120db89a84b%22%2C%22%24device_id%22%3A%2217120db89a7e-01a9c595c1732e-4c302f7e-1327104-17120db89a84b%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fcn.bing.com%2F%22%2C%22%24latest_referrer_host%22%3A%22cn.bing.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%7D; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1587484931,1587485032,1587532326,1587564214; index_location_city=%E5%85%A8%E5%9B%BD; lagou_utm_source=A; _gid=GA1.2.2028747476.1587484932; SEARCH_ID=9a145f14826c46f6a1700754e270d106; JSESSIONID=ABAAAECAAEBABII11522BFF599DD45200A1FF164A2FF69C; WEBTJ-ID=20200422220331-171a2336f8746-0557211c09d0418-4c302e7f-1327104-171a2336f9656; LGSID=20200422220334-5faa31e2-5b0c-4e11-976f-5cd550f61b7a; PRE_UTM=; PRE_HOST=cn.bing.com; PRE_SITE=https%3A%2F%2Fcn.bing.com%2F; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; LGRID=20200422221931-0345a555-3377-48fd-b50d-379b361eca0b; X_HTTP_TOKEN=447c6a537b80ff4a5315657851e77d395354012cf8; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1587565136; TG-TRACK-CODE=index_search; _gat=1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers"
    }

    def __init__(self):
        self.record_date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.url_filter = None
        self.url_filter_file = None

    def start_requests(self):
        yield scrapy.Request(self.fake_url, callback=self.parse)

    def parse(self, sid='2a30d68ddfd041caa20b04fba52d4a77'):
        data = {
            'first': 'false',
            'pn': '',
            'kd': '',
            'sid': sid
        }
        for tag in self.start_url_tags:
            print("currentTag", tag)
            data['kd'] = tag
            for page in range(1, 31):
                print("currentPage:", page)
                data['pn'] = str(page)

                i = 0
                while i < 5:
                    cookie = self.init_cookies()  # 为此次获取的cookies
                    response = self.postData(urlencode(data), cookie)
                    if response:
                        next_sid = self.get_next_sid(response.text)
                        time.sleep(5)
                        if next_sid:
                            data['sid'] = next_sid
                            for item in self.parse_json(response.text, tag):  #此处产生Item
                                yield item
                            break
                        else:
                            print("Error occured,retrying")

    def get_next_sid(self, json_str):
        result = json.loads(json_str)
        try:
            sid = result['content']['showId']
            return sid
        except:
            return None

    def init_cookies(self):
        """
        return the cookies after your first visit
        """
        headers = {
            'Upgrade-Insecure-Requests': '1',
            'Host': 'm.lagou.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'DNT': '1',
            'Cache-Control': 'max-age=0',
            'Referrer Policy': 'no-referrer-when-downgrade',
        }
        url = 'https://m.lagou.com/search.html'
        response = requests.get(url, headers=headers, timeout=10)

        return response.cookies

    def parse_json(self, json_response_str, tag):
        json_obj = json.loads(json_response_str)
        job_list = json_obj['content']['positionResult']['result']
        for job in job_list:
            job_dict = JobscrawlerLagouItem()
            id = str(job['positionId'])
            # 获得job_id,判断是否存在
            if not self.is_url_in_bloomfilter(tag + id):
                self.save_tag_url_to_file(tag + id)
                job_dict['job_id'] = id
                job_dict['record_date'] = self.record_date
                job_dict['job_tag'] = tag
                job_dict['job_name'] = job['positionName']
                if tag == '算法' and not ('算法' in job['positionName']):
                    continue
                job_dict['company_name'] = job['companyShortName']
                job_dict['company_people'] = job['companySize']
                job_dict['company_industry'] = job['industryField']
                job_dict['company_financing_stage'] = job['financeStage']
                job_dict['job_salary'] = job['salary']
                job_dict['job_welfare'] = job['positionAdvantage']
                job_dict['job_exp_require'] = job['workYear']
                job_dict['job_edu_require'] = job['education']
                yield job_dict

    def get_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/").json()

    def delete_proxy(self, proxy):
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

    def postData(self, data, cookie):
        # ....
        retry_count = 5
        proxy = self.get_proxy().get("proxy")
        while retry_count > 0:
            try:
                response = requests.post(self.json_ajax_url, data=data, headers=self.headers, cookies=cookie,
                                         proxies={"http": "http://{}".format(proxy)})
                # 使用代理访问
                return response
            except Exception:
                retry_count -= 1
        # 出错5次, 删除代理池中代理
        self.delete_proxy(proxy)
        return None

    # 全局单例过滤器
    def get_filter(self):
        if self.url_filter is None:
            self.url_filter = BloomFilter(max_elements=100000, error_rate=0.001)
            # url_filter.txt
            if os.path.exists('./url_filter.txt'):
                self.url_filter_file = open('./url_filter.txt', 'a+')
                self.url_filter_file.seek(0)
                for url in self.url_filter_file.readlines():
                    self.url_filter.add(url.strip('\n'))
            else:
                self.url_filter_file = open('./url_filter.txt', 'a+')
        return self.url_filter

    def is_url_in_bloomfilter(self, tag_id):
        filter = self.get_filter()
        if tag_id in filter:
            return True
        else:
            filter.add(tag_id)
            return False

    def save_tag_url_to_file(self, tag_id):
        self.url_filter_file.write(tag_id + '\n')
        self.url_filter_file.flush()

    def closed(self):
        self.url_filter_file.close()
        del self.url_filter