import scrapy
import json
import re

from scrapers.items import ProductItem


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
        # for url in url_test:
        #     yield response.follow(url, callback=self.parse_follow, cb_kwargs={'url': url},
        #                           headers=self.header
        #                           )
        next_page = response.css('#loadmore::attr(href)').get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_follow(self, response, url):

        branches = {
            '3106': {
                'latitude': '43.656422',
                'longitude': '-79.435567'
            },
            '3124': {
                'latitude': '48.412997',
                'longitude': '-89.239717'
            }
        }

        data_page_json = json.loads(
            re.findall(r'(\{.*\})', response.xpath("/html/body/script[1]/text()").get())[0])
        prod_json = json.loads(response.css('.evlleax3 > script:nth-child(1)::text').get())

        sku = prod_json['sku']
        description = prod_json['description']
        name = prod_json['name']
        brand = prod_json['brand']['name']
        image_url = prod_json['image']
        store = response.xpath('/html/head/meta[10]/@content').get()
        # print(f'{sku} , {description}, {name}, {brand}, {image_url}')

        upc = data_page_json['entities']['skus'][sku]['upc']
        category = data_page_json['entities']['skus'][sku]['facets'][0]['value']
        # print(f'{upc} , {category}')

        for i in range(3):
            category = '{0} | {1}'.format(data_page_json['entities']['skus'][sku]['categories'][0][
                                              'hierarchy'][i]['displayName']['en'], category)

        package = data_page_json['entities']['skus'][sku]['description']

        item = ProductItem()
        item['barcodes'] = ', '.join(upc)
        item['store'] = store
        item['category'] = category
        item['package'] = package
        item['url'] = self.start_urls[0] + url
        item['brand'] = brand
        item['image_url'] = ', '.join(image_url)
        item['description'] = description.replace('<br>', '')
        item['sku'] = sku
        item['name'] = name

        url_store = 'https://www.walmart.ca/api/product-page/find-in-store?' \
                    'latitude={}&longitude={}&lang=en&upc={}'

        for k in branches.keys():
            yield scrapy.http.Request(
                url_store.format(branches[k]['latitude'], branches[k]['longitude'], upc[0]),
                callback=self.parse_find_store, cb_kwargs={'item': item},
                meta={'handle_httpstatus_all': True},
                dont_filter=False, headers=self.header)

    def parse_find_store(self, response, item):
        store_json = json.loads(response.body)

        branch = store_json['info'][0]['id']
        stock = store_json['info'][0]['availableToSellQty']
        price = store_json['info'][0].get('sellPrice', 0)

        item['branch'] = branch
        item['stock'] = stock
        item['price'] = price

        print(item)

        yield item
