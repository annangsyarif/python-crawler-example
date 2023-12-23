import os
import json
import scrapy
from datetime import datetime
from script.FindMeasurements import find_measurements

import logging


class KlikIndomaretSpider(scrapy.Spider):
    name = "spider_klikindomaret"

    def __init__(self):
        self.page = 1

    def start_requests(self):
        url = "https://www.klikindomaret.com/page/unilever-officialstore"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        logging.info("Page : "+ str(self.page))

        # get timnow
        dt = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")

        # parse html
        div_content = response.css('* > div.product-collection.list-product.clearfix')
        
        items = div_content.css('.item')  
        logging.info("Items Found!")      

        # parse productitems
        productitems = []
        for item in items:
            _id = item.css(".item::attr(data-plu)").get()
            name = item.css(".title::text").get()
            price = item.css("* > span.normal.price-value::text").get()
            originalprice = item.css("* > span.strikeout.disc-price").get()
            discountpercentage = item.css("* > span.discount::text").get()
            platform = "www.klikindomaret.com"
            data = self.result_formatter(
                _id,
                name.strip(),
                price,
                originalprice,
                discountpercentage,
                find_measurements(name.lower()),
                platform,
                dt
            )
            productitems.append(data)
    
        # save as json
        output_name = os.getcwd() + f"/datastore/klikindomaret/product_page_{self.page}.json"
        self.write_data(
            productitems,
            output_name
        )
        logging.info(f"Data saved to: {output_name}")

        # go to next page
        next_page_url = response.css("* > div.pagination").xpath('//a[span[@class="next"]]').css("a::attr(href)").get()
        if next_page_url:
            self.page += 1
            yield scrapy.Request(url=next_page_url, callback=self.parse)
    
    def write_data(self, data, path):
        with open(path, "w") as outfile:
            json.dump(data, outfile, indent=2)
    
    def result_formatter(
            self,
            id,
            name,
            price,
            originalprice,
            discountpercentage,
            detail,
            platform,
            createdat
        ):
        if originalprice is not None:
            originalprice = float(originalprice.split("\n")[2].split(" ")[1].replace(".", ""))
        
        if discountpercentage is not None:
            discountpercentage = float(discountpercentage.replace("%", ""))
        
        return {
            "id": id,
            "name": name,
            "price": float(price.split(" ")[1].replace(".", "")),
            "originalprice": originalprice,
            "discountpercentage": discountpercentage,
            "detail": detail,
            "platform": platform,
            "createdat": createdat
        }
