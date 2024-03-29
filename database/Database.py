import psycopg2
# from psycopg2 import Error
import logging

logger = logging.getLogger(__name__)


class Database(object):
    conn = None
    curr = None

    def __init__(self, username: str, password: str, host: str, port: int, database: str):
        self.username: str = username
        self.password: str = password
        self.host: str = host
        self.port: int = port
        self.database: str = database
        self.connection_string = self.__str__()

    def __str__(self):
        """
        Postgress connection string
        """
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def __enter__(self):
        self.connect()
        self.curr = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        if exc_type is not None:
            logger.warn(exc_type, exc_val)
            return False
        logger.debug("Database connection closed")
        return True

    def connect(self):
        """
        Connect to the database
        """
        try:
            conn = psycopg2.connect(
                dbname=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logger.debug("Successfully connected to the database")
            self.conn = conn
            return conn
        except Exception as e:
            logger.error("Failed to connect to the database", e)

    def disconnect(self) -> None:
        """
        Disconnect from the database
        """
        self.conn.close()
        logger.debug("Disconnected from the database")

    def execute(self, query: str, *args) -> None:
        """
        Execute a query
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, *args)
            self.conn.commit()
            logger.debug("Query executed successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error("Failed to execute the query, rolling back", e)

    def execute_many(self, query: str, args) -> None:
        """
        Execute a query with multiple arguments
        """
        try:
            cursor = self.conn.cursor()
            cursor.executemany(query, args)
            self.conn.commit()
            logger.debug("Query executed successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error("Failed to execute the query, rolling back", e)

    def fetch(self, query: str, args) -> list[tuple]:
        """
        Fetch the results of a query
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, args)
            rows: list[tuple] = cursor.fetchall()
            return rows
        except Exception as e:
            logger.error("Failed to fetch the results", e)

    def start_transaction(self) -> None:
        """
        Start a transaction
        """
        self.conn.cursor().execute("BEGIN TRANSACTION")

    def commit_transaction(self) -> None:
        """
        Commit a transaction
        """
        self.conn.cursor().execute("COMMIT;")
