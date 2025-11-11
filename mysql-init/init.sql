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
    logo VARCHAR(100),
    latest_price FLOAT
);
