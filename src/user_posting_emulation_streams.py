from time import sleep
import logging
import random

from connector import AWSDBConnector
from kinesis_api import KinesisAPI

logger = logging.getLogger(__name__)
logging.basicConfig(filename="emulator_kinesis.log", filemode="w", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(module)s - %(funcName)s: %(message)s")

random.seed(100)

db_connector = AWSDBConnector()
api = KinesisAPI()

def run_infinite_post_data_loop():
    """
    Fetch data from RDS database, that acts as mock data that in a real scenario, would be coming from millions of devices.
    This data is then sent as a POST request to the Kinesis API Gateway.
    """
    engine = db_connector.create_db_connector()

    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)

        with engine.connect() as connection:
            row_pin = db_connector.get_row(connection, "pinterest_data", random_row)
            row_geo = db_connector.get_row(connection, "geolocation_data", random_row)
            row_user = db_connector.get_row(connection, "user_data", random_row)
            response_pin = api.record_to_stream(api.streams["POSTS"], row_pin)
            response_geo = api.record_to_stream(api.streams["GEO"], row_geo)
            response_user = api.record_to_stream(api.streams["USER"], row_user)

            logging.info("Pin response: %s", response_pin)
            logging.info("Geo response: %s", response_geo)
            logging.info("User response: %s", response_user)


if __name__ == "__main__":
    run_infinite_post_data_loop()
