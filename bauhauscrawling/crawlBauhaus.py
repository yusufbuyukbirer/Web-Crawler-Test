from scrapy.crawler import CrawlerProcess
from datetime import datetime
import scrapy
import json
import re


class bauhaus(scrapy.Spider):
    name = 'Bauhaus'
    today = datetime.now().strftime("%Y-%m-%d")
    output = []
    start_url = "https://www.bauhaus.com.tr/bauhaus-hirdavat"
    headers = {
        'cookie': 'showgrid=4; frontend=956s091u26eniog50ff882ch66; frontend=956s091u26eniog50ff882ch66',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    def start_requests(self):
        req = scrapy.Request(url=self.start_url, callback=self.pagination, headers=self.headers)
        yield req

    def pagination(self, response):
        ppp = 24
        url_format = "https://www.bauhaus.com.tr/service/list/category?pg={p}&id=3"
        pagination_text = response.css(".resultTxt::text").get()
        product_count = int(re.findall("\d+", pagination_text)[0])
        page_count = product_count // ppp + 1

        for i in range(0, page_count):
            url = url_format.format(p=i)
            req = scrapy.Request(url=url, callback=self.parse)
            yield req

    def parse(self, response):
        data = json.loads(response.body)
        products = data['products']

        for product in products:
            sku = product['sku']
            pname = product['title']
            purl = "https://www.bauhaus.com.tr/%s" % product['url_key']
            pimage = "https://bau-cdn.veesk.net%s" % product['listimages_array'][0]
            product_price = float(product['price'])
            product_discount_price = float(product['special_price'])

            prices_arr = [product_price, product_discount_price]
            prices_arr = [x for x in prices_arr if x > 0]
            prices_arr = sorted(list(set(prices_arr)))

            if len(prices_arr) > 0:
                pprice = max(prices_arr)
                dprice = min(prices_arr)
                is_promoted = (pprice > dprice)
            else:
                pprice = dprice = 0
                is_promoted = False

            if pprice == dprice:
                dprice = 0

            item = {
                "product_sku_id": sku,
                "product_name": pname,
                "product_sales_channel": self.name,
                "product_url": purl,
                "product_image": pimage,
                "product_price": pprice,
                "product_discount_price": dprice,
                "product_is_promoted": is_promoted,
            }

            self.output.append(item)

    def close(self, spider, reason):
        with open(f"{self.name}_{self.today}.json", "w", encoding="utf-8") as f:
            json.dump(self.output, f, ensure_ascii=False)


process = CrawlerProcess()
process.crawl(bauhaus)
process.start()
