from time import sleep
import random

from connector import AWSDBConnector
from kafka_api import KafkaAPI

random.seed(100)

db_connector = AWSDBConnector()
api = KafkaAPI()

def run_infinite_post_data_loop():
    """
    Fetch data from RDS database, that acts as mock data that in a real scenario, would be coming from millions of devices.
    This data is then sent as a POST request to the Kafka API Gateway.
    """
    engine = db_connector.create_db_connector()

    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)

        with engine.connect() as connection:

            pin_result = db_connector.get_pin_row(connection, random_row)
            geo_result = db_connector.get_geo_row(connection, random_row)
            user_result = db_connector.get_user_row(connection, random_row)

            print("pin response:", api.post_to_topic(api.topics["POSTS"], pin_result))
            print("geo response:", api.post_to_topic(api.topics["GEO"], geo_result))
            print("user response:", api.post_to_topic(api.topics["USER"], user_result))


if __name__ == "__main__":
    run_infinite_post_data_loop()
