import psycopg2
from sqlalchemy import create_engine
import pandas as pd

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PostgreSQLHandler:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.engine = None

    def create_connection(self):
        try:
            connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logging.info("Connected to PostgreSQL")
            self.connection = connection

            self.engine = create_engine(f'postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}')
        except Exception as e:
            logging.error(f"Error: {e}")

    def close_connection(self):
        if self.connection:
            self.connection.close()
            logging.info("Connection to PostgreSQL closed")

    def execute_query(self, query):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            logging.info("Query executed successfully")
        except Exception as e:
            logging.error(f"Error executing query: {e}")

    def insert_data(self, table_name, data_frame, write_mode="append"):
        try:
            data_frame.to_sql(
                table_name,
                self.engine,
                if_exists=write_mode,
                index=False
            )
            logging.info("Data inserted successfully")
        except Exception as e:
            logging.error(f"Error inserting data: {e}")

    def read_data(self, query):
        try:
            result = pd.read_sql_query(query, self.connection)
            logging.info("Data read successfully")
            return result
        except Exception as e:
            logging.error(f"Error reading data: {e}")
            return None