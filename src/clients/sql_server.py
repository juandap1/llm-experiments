import pymysql
from pymysql.cursors import DictCursor
from datetime import datetime

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
            # print("✅ Connected to MySQL successfully.")
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
            # print("🔌 MySQL connection closed.")

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

    def update_company_data(self, ticker, name, description, sector, industry, book_value, earnings_per_share, revenue_per_share, dividend_per_share, shares_outstanding, analyst_target_price, ebitda):
        self.ensure_connected()
        with self.connection.cursor() as cursor:
            sql = """
                INSERT INTO tickers (ticker, name, description, sector, industry, book_value, earnings_per_share, revenue_per_share, dividend_per_share, shares_outstanding, analyst_target_price, ebitda) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=%s, description=%s, sector=%s, industry=%s, book_value=%s, earnings_per_share=%s, revenue_per_share=%s, dividend_per_share=%s, shares_outstanding=%s, analyst_target_price=%s, ebitda=%s
            """
            cursor.execute(sql, (ticker, name, description, sector, industry, book_value, earnings_per_share, revenue_per_share, dividend_per_share, shares_outstanding, analyst_target_price, ebitda, name, description, sector, industry, book_value, earnings_per_share, revenue_per_share, dividend_per_share, shares_outstanding, analyst_target_price, ebitda)) 
            # self.connection.commit()
            return 200
        
    def update_stock_price(self, ticker, price):
        self.ensure_connected()
        with self.connection.cursor() as cursor:
            sql = """
                INSERT INTO tickers (ticker, latest_price) VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE latest_price=%s
            """
            cursor.execute(sql, (ticker, price, price))
            # self.connection.commit()
            return

    def update_etf_info(self, ticker, dividend_per_share):
        self.ensure_connected()
        with self.connection.cursor() as cursor:
            sql = """
                INSERT INTO tickers (ticker, dividend_per_share) VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE dividend_per_share=%s
            """
            cursor.execute(sql, (ticker, dividend_per_share, dividend_per_share))
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
        
    def update_analysis(self, ticker, analysis):
        self.ensure_connected()

        with self.connection.cursor() as cursor:
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')
            sql = """
                INSERT INTO tickers (ticker, analysis, analysis_updated) VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE analysis=%s, analysis_updated=%s
            """
            cursor.execute(sql, (ticker, analysis, formatted_date, analysis, formatted_date))
            return 200
        
    def insert_many_prices(self, ticker, price_data_list):
        """
        Inserts a list of price records using executemany for efficiency.
        price_data_list should be a list of tuples: 
        [(open_price, close_price, low, high, date), ...]
        """
        MAX_RETRIES = 2
        
        # Base SQL statement for the price_history table
        sql = """
            INSERT INTO price_history 
            (ticker, open_price, close_price, low, high, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        for attempt in range(MAX_RETRIES):
            self.ensure_connected() 
            with self.connection.cursor() as cursor:
                try:
                    # Use executemany for batch insertion
                    cursor.executemany(sql, price_data_list)
                    return cursor.rowcount 
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        print(f"⚠️ Batch insert failed on attempt {attempt + 1}. Retrying...")
                        continue
                    else:
                        print(f"❌ Batch insert failed after {MAX_RETRIES} attempts. Final Error: {e}")
                        raise

    def insert_many_splits(self, ticker, split_data_list):
        """
        Inserts a list of split records using executemany for efficiency.
        split_data_list should be a list of tuples: 
        [(split_from, split_to, date), ...]
        """
        MAX_RETRIES = 2
        
        # Base SQL statement for the price_history table
        sql = """
            INSERT INTO split_history 
            (ticker, split_from, split_to, execution_date)
            VALUES (%s, %s, %s, %s)
        """
        for attempt in range(MAX_RETRIES):
            self.ensure_connected() 
            with self.connection.cursor() as cursor:
                try:
                    # Use executemany for batch insertion
                    cursor.executemany(sql, split_data_list)
                    cursor.execute("UPDATE tickers SET checked_split = %s WHERE ticker = %s", (datetime.now(), ticker))
                    return cursor.rowcount 
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        print(f"⚠️ Batch insert failed on attempt {attempt + 1}. Retrying...")
                        continue
                    else:
                        print(f"❌ Batch insert failed after {MAX_RETRIES} attempts. Final Error: {e}")
                        raise

    def insert_dividend_history(self, ticker, dividend_data_list):
        """
        Inserts a list of dividend records using executemany for efficiency.
        dividend_data_list should be a list of tuples: 
        [(amount, declaration_date, ex_dividend_date, payment_date), ...]
        """
        MAX_RETRIES = 2
        
        # Base SQL statement for the price_history table
        sql = """
            INSERT INTO dividend_history 
            (ticker, amount, declaration_date, ex_dividend_date, payment_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        for attempt in range(MAX_RETRIES):
            self.ensure_connected() 
            with self.connection.cursor() as cursor:
                try:
                    # Use executemany for batch insertion
                    cursor.executemany(sql, dividend_data_list)
                    cursor.execute("UPDATE tickers SET checked_dividend = %s WHERE ticker = %s", (datetime.now(), ticker))
                    return cursor.rowcount 
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        print(f"⚠️ Batch insert failed on attempt {attempt + 1}. Retrying...")
                        continue
                    else:
                        print(f"❌ Batch insert failed after {MAX_RETRIES} attempts. Final Error: {e}")
                        raise

    def insert_income_reports(self, table, ticker, income_reports):
        MAX_RETRIES = 2
        
        # Base SQL statement for the price_history table
        sql = f"""
            INSERT INTO {table} 
            (ticker, fiscalDateEnding, reportedCurrency, grossProfit, totalRevenue, costOfRevenue, costofGoodsAndServicesSold, operatingIncome, sellingGeneralAndAdministrative, researchAndDevelopment, operatingExpenses, investmentIncomeNet, netInterestIncome, interestIncome, interestExpense, nonInterestIncome, otherNonOperatingIncome, depreciation, depreciationAndAmortization, incomeBeforeTax, incomeTaxExpense, interestAndDebtExpense, netIncomeFromContinuingOperations, comprehensiveIncomeNetOfTax, ebit, ebitda, netIncome)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for attempt in range(MAX_RETRIES):
            self.ensure_connected() 
            with self.connection.cursor() as cursor:
                try:
                    # Use executemany for batch insertion
                    cursor.executemany(sql, income_reports)
                    return cursor.rowcount
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        print(f"⚠️ Batch insert failed on attempt {attempt + 1}. Retrying...")
                        continue
                    else:
                        print(f"❌ Batch insert failed after {MAX_RETRIES} attempts. Final Error: {e}")
                        raise