import subprocess
import os
import json
import pandas
import json

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from script.UniqueProductIdentifier import UniqueProductIdentifier
from script.PostgreSql import PostgreSQLHandler
from script.ProductPriceGenerator import format_product_price_results

nltk.download('punkt')
nltk.download('stopwords')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CrawlingPipeline:
    def __init__(self):
        self.spider_list = [
            "spider_klikindomaret",
            "spider_tokopedia"
        ]

        with open("requirements/config.json") as f:
            self.config = json.load(f)

        self.postgres = PostgreSQLHandler(
            self.config["postgres"]["host"],
            self.config["postgres"]["port"],
            self.config["postgres"]["database"],
            self.config["postgres"]["user"],
            self.config["postgres"]["password"]
        )
        self.postgres.create_connection()

        self.productmaster = self.postgres.read_data(
            "select * from productmaster"
        )
    def run(self):
        logging.info("Running Python Crawlers")
        # running python crawler
        for spider_name in self.spider_list:
            subprocess.run(f"scrapy crawl {spider_name}", shell=True)

        logging.info("Process All Data")
        all_files = self.list_files_in_directory("datastore")
        data = []
        for file_ in all_files:
            with open(file_, "r") as f:
                data += json.load(f)
        
        df = pandas.DataFrame(data)

        df = df.drop(columns=["id"])

        logging.info("Creating productmaster ...")
        # create productmaster
        identifier = UniqueProductIdentifier()
        productmaster_dict = identifier.identify_unique_products_dataframe(df, self.productmaster)
        self.productmaster = pandas.DataFrame(productmaster_dict)

        self.postgres.insert_data(
            "productmaster",
            self.productmaster
        )

        logging.info("Creating productprice ..")
        # create productprice
        productprice_dict = format_product_price_results(df, self.productmaster)
        productprice = pandas.DataFrame(productprice_dict)
        self.postgres.insert_data(
            "productprice",
            productprice
        )

        logging.info("Creating pricerecommendation")
        self.postgres.execute_query(
            """
                drop table if exists pricerecommendation;

                create table pricerecommendation as
                    select
                        productmaster_id
                        , round(avg(price)::numeric,2)::float as pricerecommendation
                        , current_timestamp as date from productprice
                    group by productmaster_id;
            """
        )

        self.postgres.close_connection()
        logging.info("Done!")

    def list_files_in_directory(self, directory):
        file_list = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    file_list.append(file_path)

        return file_list

if __name__ == "__main__":
    pipeline = CrawlingPipeline()
    pipeline.run()