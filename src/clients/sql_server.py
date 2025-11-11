import pymysql
from pymysql.cursors import DictCursor

class MySQLClient:
    def __init__(self, host="mysql", user="my_user", password="my_password",
                 database="my_database", port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.connect()

    def connect(self):
        """Establish a connection to the MySQL database."""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                cursorclass=DictCursor,
                autocommit=True
            )
            print("✅ Connected to MySQL successfully.")
        except Exception as e:
            print("❌ Failed to connect to MySQL:", e)

    def ensure_connected(self):
        try:
            # PyMySQL attempts to reconnect if the connection is detected as closed.
            self.connection.ping(reconnect=True) 
        except Exception as e:
            print(f"❌ Connection check failed, trying full reconnect: {e}")
            # If ping failed, try establishing a brand new connection
            self.connect()

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("🔌 MySQL connection closed.")

    def execute(self, query, params=None, commit=False):
        """
        Execute an INSERT, UPDATE, or DELETE query.
        Example:
            client.execute("INSERT INTO users (name, age) VALUES (%s, %s)", ("John", 25), commit=True)
        """
        self.ensure_connected()

        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, params or ())
                if commit:
                    self.connection.commit()
                return cursor.rowcount
            except Exception as e:
                self.connection.rollback()
                print("❌ Query failed:", e)
                return None

# MAYBE ADD CONDITION FOR NOT AUTO COMMITING (for performance?)

    def fetch_one(self, query, params=None):
        """
        Execute a SELECT query and return a single record.
        Example:
            user = client.fetch_one("SELECT * FROM users WHERE id = %s", (1,))
        """
        self.ensure_connected()

        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()

    def fetch_all(self, query, params=None):
        """
        Execute a SELECT query and return all records.
        Example:
            users = client.fetch_all("SELECT * FROM users WHERE active = %s", (1,))
        """
        self.ensure_connected()

        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        
    def insert_transaction(self, ticker, share_count, share_price, transaction_date, buying):
        self.ensure_connected()

        with self.connection.cursor() as cursor:
            sql = """
                INSERT INTO transactions (ticker, share_count, share_price, transaction_date, buying)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (ticker, share_count, share_price, transaction_date, buying))
            # self.connection.commit()
            inserted_id = cursor.lastrowid
            return inserted_id

    def update_company_data(self, ticker, name, description, sector, industry):
        self.ensure_connected()
        with self.connection.cursor() as cursor:
            sql = """
                INSERT INTO tickers (ticker, name, description, sector, industry) VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=%s, description=%s, sector=%s, industry=%s
            """
            cursor.execute(sql, (ticker, name, description, sector, industry, name, description, sector, industry)) 
            # self.connection.commit()
            return 200
        
    def update_stock_price(self, ticker, price, date):
        self.ensure_connected()
        with self.connection.cursor() as cursor:
            sql = """
                INSERT INTO tickers (ticker, latest_price, latest_date) VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE latest_price=%s, latest_date=%s
            """
            cursor.execute(sql, (ticker, price, date, price, date))
            # self.connection.commit()
            return 
        
    def update_logo(self, ticker, path):
        self.ensure_connected()

        with self.connection.cursor() as cursor:
            sql = """
                INSERT INTO tickers (ticker, logo) VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE logo=%s
            """
            cursor.execute(sql, (ticker, path, path)) 
            # self.connection.commit()
            return 200