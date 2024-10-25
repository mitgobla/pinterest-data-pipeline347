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

    def get_row(self, connection, table:str, row: int):
        """Get a row from a table in the RDS database.

        Args:
            connection (sqlalchemy.engine.base.Connection): SQLAlchemy Engine Connection
            table (str): Table to select from.
            row (int): Row to select from table.

        Returns:
            dict: Dictionary of row mapping.
        """
        statement = sqlalchemy.text(f"SELECT * FROM {table} LIMIT {row}, 1")
        selected_row = connection.execute(statement)

        for _row in selected_row:
            result = dict(_row._mapping)
        return result
