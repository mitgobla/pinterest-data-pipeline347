import yaml
import sqlalchemy

class AWSDBConnector:
    """A connector to an AWS RDS database.
    Provides functions for fetching specific rows of data.
    """

    def __init__(self, conf_file = "db_creds.yaml"):

        # Read Configuration
        with open(conf_file, "r") as cred_file:
            credentials = yaml.safe_load(cred_file)


        self.HOST = credentials['HOST']
        self.USER = credentials['USER']
        self.PASSWORD = credentials['PASSWORD']
        self.DATABASE = credentials['DATABASE']
        self.PORT = credentials['PORT']

    def create_db_connector(self):
        """Create an engine to the RDS instance.

        Returns:
            sqlalchemy.engine.base.Engine: SQLAlchemy Engine
        """
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}?charset=utf8mb4")
        return engine

    def get_pin_row(self, connection, row: int):
        """Get a row from the Pin table in the RDS database.

        Args:
            connection (sqlalchemy.engine.base.Connection): SQLAlchemy Engine Connection
            row (int): Row to select from table

        Returns:
            dict: Dictionary of row mapping.
        """
        pin_string = sqlalchemy.text(f"SELECT * FROM pinterest_data LIMIT {row}, 1")
        pin_selected_row = connection.execute(pin_string)

        for _row in pin_selected_row:
            pin_result = dict(_row._mapping)
        return pin_result

    def get_geo_row(self, connection, row: int):
        """Get a row from the Geolocation table in the RDS database.

        Args:
            connection (sqlalchemy.engine.base.Connection): SQLAlchemy Engine Connection
            row (int): Row to select from table

        Returns:
            dict: Dictionary of row mapping.
        """
        geo_string = sqlalchemy.text(f"SELECT * FROM geolocation_data LIMIT {row}, 1")
        geo_selected_row = connection.execute(geo_string)

        for _row in geo_selected_row:
            geo_result = dict(_row._mapping)
        return geo_result

    def get_user_row(self, connection, row: int):
        """Get a row from the User table in the RDS database.

        Args:
            connection (sqlalchemy.engine.base.Connection): SQLAlchemy Engine Connection
            row (int): Row to select from table

        Returns:
            dict: Dictionary of row mapping.
        """
        user_string = sqlalchemy.text(f"SELECT * FROM user_data LIMIT {row}, 1")
        user_selected_row = connection.execute(user_string)

        for _row in user_selected_row:
            user_result = dict(_row._mapping)
        return user_result