import scrapy
import json
import re


class CaWalmartBot(scrapy.Spider):
    name = 'ca_walmart'
    allowed_domains = ['walmart.ca']
    handle_httpstatus_list = [500, 503, 504, 400, 408, 403]
    start_urls = ['https://www.walmart.ca/en/grocery/fruits-vegetables/fruits/N-3852']
    # start_urls = (
    #     'https://httpbin.org/get',
    #     'https://httpbin.org/redirect-to?url=http%3A%2F%2Fexample.com%2F',
    # )
    header = {
        'Host': 'www.walmart.ca',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/text',
        'Connection': 'keep-alive',
        # 'If-None-Match': '*'
    }

    # def start_requests(self):
    #     response = scrapy.FormRequest(self.start_urls[0],
    #                        callback=self.parse,
    #                                   headers=self.header)
    #     print(response.headers)
    #     return [response]

    def parse(self, response):
        # url_test = ['/en/ip/pears-bartlett/6000187833002']
        for url in response.css('.product-link::attr(href)').getall():
            yield response.follow(url, callback=self.parse_follow,
                                  cb_kwargs={'url': url}, headers=self.header)
        # print(response.meta)
        # print(response.headers)
        # for url in url_test:
        #     yield response.follow(url, callback=self.parse_follow, cb_kwargs={'url': url},
        #                           headers=self.header
        #                           )


    def parse_follow(self, response, url):
        data_page_json = json.loads(
            re.findall(r'(\{.*\})', response.xpath("/html/body/script[1]/text()").get())[0])
        print(data_page_json)
        prod_json = json.loads(response.css('.evlleax3 > script:nth-child(1)::text').get())
        print(prod_json)
