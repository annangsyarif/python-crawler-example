import os
import json
import scrapy
import time
from scrapy_selenium import SeleniumRequest
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from datetime import datetime
import logging

from script.FindMeasurements import find_measurements

# disable selenium logging
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class TokopediaSpider(scrapy.Spider):
    name = "spider_tokopedia"

    def __init__(self):
        self.page = 1

    def start_requests(self):
        url = f"https://www.tokopedia.com/unilever/product/page/{self.page}"
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        logging.info("Page : "+ str(self.page))
        dt = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")

        driver = response.request.meta["driver"]
        logging.info("Driver Found!")
        for i in range(0, 5):
            # scroll down by 10000 pixels
            ActionChains(driver) \
                .scroll_by_amount(0, 10000) \
                .perform()

            # waiting for products to load
            time.sleep(1)

        items = driver.find_elements(By.CSS_SELECTOR, "* > div.css-1sn1xa2")
        logging.info("Items Found!")


        # parse product
        product = []
        _id = 0
        logging.info("Processing data ...")
        for item in items:
            name = item.find_element(By.CSS_SELECTOR, "* > div.prd_link-product-name.css-3um8ox").text
            if self.check_text(name):
                logging.info(name)
                _id += 1
                price = item.find_element(By.CSS_SELECTOR, "* > div.prd_link-product-price.css-h66vau").text
                try:
                    originalprice = item.find_element(By.CSS_SELECTOR, "* > div.prd_label-product-slash-price.css-xfl72w").text
                    discountpercentage = item.find_element(By.CSS_SELECTOR, "* > div.prd_badge-product-discount.css-1xelcdh").text
                except Exception as e:
                    originalprice = None
                    discountpercentage = None
                
                platform = "www.tokopedia.com"

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
                
                product.append(data)

        
        if len(product) != 0:
            output_name = os.getcwd() + f"/datastore/tokopedia/product_page_{self.page}.json"
            self.write_data(
                product,
                output_name
            )
            logging.info(f"Data saved to: {output_name}")
        else:
            logging.info("No data found!")

        self.page += 1
        try:
            next_page_url = driver.find_element(By.CSS_SELECTOR, '* > a[data-testid="btnShopProductPageNext"]').get_attribute("href")
            yield SeleniumRequest(url=next_page_url, callback=self.parse)
        except Exception as e:
            pass

    
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
            originalprice = float(originalprice.strip().replace("Rp","").replace(".", ""))
        
        if discountpercentage is not None:
            discountpercentage = float(discountpercentage.replace("%", ""))
        
        return {
            "id": id,
            "name": name,
            "price": float(price.strip().replace("Rp","").replace(".", "")),
            "originalprice": originalprice,
            "discountpercentage": discountpercentage,
            "detail": detail,
            "platform": platform,
            "createdat": createdat
        }
    
    def check_text(self, text):
        with open("requirements/banned_words", "r") as f:
            words = f.read().split("\n")
        result = True
        for word in words:
            if word in text.lower():
                result = False
                break
        
        return result
        
    
