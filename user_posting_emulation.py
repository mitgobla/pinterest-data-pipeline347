import requests
from time import sleep
import random
from multiprocessing import Process
import boto3
import json
import sqlalchemy
from sqlalchemy import text
import yaml

from kafka_api import KafkaAPI

random.seed(100)

class AWSDBConnector:

    def __init__(self):

        # Read Configuration
        with open("db_creds.yaml", "r") as cred_file:
            credentials = yaml.safe_load(cred_file)


        self.HOST = credentials['HOST']
        self.USER = credentials['USER']
        self.PASSWORD = credentials['PASSWORD']
        self.DATABASE = credentials['DATABASE']
        self.PORT = credentials['PORT']

    def create_db_connector(self):
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}?charset=utf8mb4")
        return engine


new_connector = AWSDBConnector()
api = KafkaAPI()

def run_infinite_post_data_loop():
    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)
        engine = new_connector.create_db_connector()

        with engine.connect() as connection:

            pin_string = text(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
            pin_selected_row = connection.execute(pin_string)

            for row in pin_selected_row:
                pin_result = dict(row._mapping)

            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)

            for row in geo_selected_row:
                geo_result = dict(row._mapping)

            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)

            for row in user_selected_row:
                user_result = dict(row._mapping)

            print(pin_result)
            print(geo_result)
            print(user_result)

            api.post_to_topic(api.topics["POSTS"], pin_result)
            api.post_to_topic(api.topics["GEO"], geo_result)
            api.post_to_topic(api.topics["USER"], user_result)


if __name__ == "__main__":
    run_infinite_post_data_loop()
