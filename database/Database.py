import psycopg2
from psycopg2 import Error


class Database(object):
    conn = None
    curr = None

    def __init__(self, username, password, host, port, database):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.connection_string = self.__str__()

    def __str__(self):
        """
        Postgress connection string
        """
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def __enter__(self):
        self.connect()
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        if exc_type is not None:
            print(exc_type, exc_val)
            return False
        print("Database connection closed")
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
            print("Successfully connected to the database")
            self.conn = conn
            return conn
        except Exception as e:
            print("Failed to connect to the database")
            print(e)

    def disconnect(self):
        """
        Disconnect from the database
        """
        self.conn.close()
        print("Disconnected from the database")

    def execute(self, query, *args):
        """
        Execute a query
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, *args)
            self.conn.commit()
            print("Query executed successfully")
        except Exception as e:
            self.conn.rollback()
            print("Failed to execute the query, rolling back")
            print(e)

    def execute_many(self, query, args):
        """
        Execute a query with multiple arguments
        """
        try:
            cursor = self.conn.cursor()
            cursor.executemany(query, args)
            self.conn.commit()
            print("Query executed successfully")
        except Exception as e:
            self.conn.rollback()
            print("Failed to execute the query, rolling back")
            print(e)

    def fetch(self, query):
        """
        Fetch the results of a query
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print("Failed to fetch the results")
            print(e)

    def start_transaction(self):
        """
        Start a transaction
        """
        self.conn.cursor().execute("BEGIN TRANSACTION")

    def commit_transaction(self):
        """
        Commit a transaction
        """
        self.conn.cursor().execute("COMMIT;")
        