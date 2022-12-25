import scrapy

class BauhaushirdavatSpider(scrapy.Spider):
    name = 'bauhausHirdavat'
    allowed_domains = ['www.bauhaus.com.tr']
    start_urls = ["https://www.bauhaus.com.tr/bauhaus-hirdavat?pg=%d" % i for i in range(1,226)]

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }

    def parse(self, response):
        product_sku=response.css("::attr(data-sku)").extract()
        product_name=response.css('.prodName::text').extract()
        product_price=response.css('.price::text').extract()
        
        row_data=zip(product_sku, product_name, product_price)

        for item in row_data:
            crawled_info = {
                'productID': item[0],
                'productName': item[1],
                'price': item[2],
            }

            yield crawled_info