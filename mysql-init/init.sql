CREATE DATABASE IF NOT EXISTS my_database;
USE my_database;

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(100),
    share_count FLOAT,
    share_price FLOAT,
    transaction_date DATE,
    buying BOOLEAN
);

CREATE TABLE IF NOT EXISTS tickers(
    ticker VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255),
    description MEDIUMTEXT,
    sector VARCHAR(255),
    industry VARCHAR(255),
    logo VARCHAR(100),
    analysis MEDIUMTEXT,
    analysis_updated DATE,
    latest_price FLOAT,
    latest_date DATE,
    book_value FLOAT,
    earnings_per_share FLOAT,
    revenue_per_share FLOAT,
    dividend_per_share FLOAT,
    shares_outstanding BIGINT,
    analyst_target_price FLOAT,
    ebitda DOUBLE,
    is_etf BOOLEAN
);

CREATE TABLE IF NOT EXISTS price_history(
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(100),
    open_price FLOAT,
    close_price FLOAT,
    high FLOAT,
    low FLOAT,
    date DATE,
    FOREIGN KEY (ticker) REFERENCES tickers(ticker)
);

CREATE TABLE IF NOT EXISTS dividend_history(
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(100),
    amount FLOAT,
    declaration_date DATE,
    ex_dividend_date DATE,
    payment_date DATE,
    FOREIGN KEY (ticker) REFERENCES tickers(ticker)
);