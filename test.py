# stock_data.py

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import csv
import time
from datetime import datetime, timedelta
from stock_class import Stock, DailyData
from utilities import clear_screen, sortDailyData

# Create the SQLite database
def create_database():
    stockDB = "stocks.db"
    conn = sqlite3.connect(stockDB)
    cur = conn.cursor()
    createStockTableCmd = """CREATE TABLE IF NOT EXISTS stocks (
                            symbol TEXT NOT NULL PRIMARY KEY,
                            name TEXT,
                            shares REAL
                        );"""
    createDailyDataTableCmd = """CREATE TABLE IF NOT EXISTS dailyData (
                            symbol TEXT NOT NULL,
                            date TEXT NOT NULL,
                            price REAL NOT NULL,
                            volume REAL NOT NULL,
                            PRIMARY KEY (symbol, date)
                        );"""   
    createTransactionTableCmd = """CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            symbol TEXT NOT NULL,
                            type TEXT NOT NULL,
                            shares REAL NOT NULL,
                            price REAL NOT NULL,
                            date TEXT NOT NULL
                        );"""
    cur.execute(createStockTableCmd)
    cur.execute(createDailyDataTableCmd)
    cur.execute(createTransactionTableCmd)

# Save stocks and daily data into database
def save_stock_data(stock_list):
    stockDB = "stocks.db"
    conn = sqlite3.connect(stockDB)
    cur = conn.cursor()
    insertStockCmd = """INSERT OR REPLACE INTO stocks (symbol, name, shares) VALUES (?, ?, ?);"""
    insertDailyDataCmd = """INSERT OR IGNORE INTO dailyData (symbol, date, price, volume) VALUES (?, ?, ?, ?);"""
    for stock in stock_list:
        insertValues = (stock.symbol, stock.name, stock.shares)
        cur.execute(insertStockCmd, insertValues)
        for daily_data in stock.DataList:
            insertValues = (stock.symbol, daily_data.date.strftime("%m/%d/%y"), daily_data.close, daily_data.volume)
            cur.execute(insertDailyDataCmd, insertValues)
    conn.commit()
    conn.close()

# Load stocks and daily data from database
def load_stock_data(stock_list):
    stock_list.clear()
    conn = sqlite3.connect("stocks.db")
    stockCur = conn.cursor()
    stockCur.execute("SELECT symbol, name, shares FROM stocks;")
    stockRows = stockCur.fetchall()
    for row in stockRows:
        new_stock = Stock(row[0], row[1], row[2])
        dailyDataCur = conn.cursor()
        dailyDataCur.execute("SELECT date, price, volume FROM dailyData WHERE symbol=?;", (new_stock.symbol,))
        dailyDataRows = dailyDataCur.fetchall()
        for dailyRow in dailyDataRows:
            daily_data = DailyData(datetime.strptime(dailyRow[0], "%m/%d/%y"), float(dailyRow[1]), float(dailyRow[2]))
            new_stock.add_data(daily_data)
        stock_list.append(new_stock)
    conn.close()
    sortDailyData(stock_list)

# Record a transaction
def log_transaction(symbol, transaction_type, shares, price, date):
    conn = sqlite3.connect("stocks.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions (symbol, type, shares, price, date)
        VALUES (?, ?, ?, ?, ?);
    """, (symbol, transaction_type, shares, price, date.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# Calculate average cost price from BUY transactions
def get_average_cost(symbol):
    conn = sqlite3.connect("stocks.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT shares, price FROM transactions
        WHERE symbol = ? AND type = 'BUY'
    """, (symbol,))
    rows = cur.fetchall()
    conn.close()

    total_shares = 0
    total_cost = 0
    for shares, price in rows:
        total_shares += shares
        total_cost += shares * price

    if total_shares == 0:
        return 0
    return total_cost / total_shares

# Fill missing daily data (e.g., past 30 days)
def fill_missing_daily_data(stock_list, days=30):
    print("[Info] Checking for missing daily data...")
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    total_fetched = 0

    for stock in stock_list:
        print(f"\nChecking {stock.symbol}...")
        try:
            data_list = stock.DataList
        except AttributeError:
            data_list = stock.data_list

        existing_dates = set(d.date.date() for d in data_list)
        expected_dates = set(
            (start_date + timedelta(days=i))
            for i in range(days + 1)
            if (start_date + timedelta(days=i)).weekday() < 5
        )
        missing_dates = sorted(expected_dates - existing_dates)

        if missing_dates:
            print(f"[{stock.symbol}] Missing {len(missing_dates)} trading days.")
            fetch_start = min(missing_dates).strftime("%m/%d/%y")
            fetch_end = max(missing_dates).strftime("%m/%d/%y")
            print(f"[{stock.symbol}] Fetching from {fetch_start} to {fetch_end}...")
            fetched = retrieve_stock_web(fetch_start, fetch_end, [stock])
            print(f"[{stock.symbol}] {fetched} records fetched.")
            total_fetched += fetched
        else:
            print(f"[{stock.symbol}] OK — All recent data present.")

    print("\n" + "=" * 50)
    print(f"[Done] Total records fetched across all stocks: {total_fetched}")
    input("Press Enter to continue...")

# Retrieve data from Yahoo Finance via Web scraping
def retrieve_stock_web(dateStart, dateEnd, stock_list):
    dateFrom = str(int(time.mktime(time.strptime(dateStart, "%m/%d/%y"))))
    dateTo = str(int(time.mktime(time.strptime(dateEnd, "%m/%d/%y"))))
    recordCount = 0
    for stock in stock_list:
        stockSymbol = stock.symbol
        url = f"https://finance.yahoo.com/quote/{stockSymbol}/history?period1={dateFrom}&period2={dateTo}&interval=1d&filter=history&frequency=1d"

        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})

        try:
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(60)
            driver.get(url)
        except:
            raise RuntimeWarning("Chrome Driver Not Found")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        dataRows = soup.find_all('tr')
        for row in dataRows:
            td = row.find_all('td')
            rowList = [i.text for i in td]
            if len(rowList) == 7:
                try:
                    daily_data = DailyData(
                        datetime.strptime(rowList[0], "%b %d, %Y"),
                        float(rowList[5].replace(',', '')),
                        float(rowList[6].replace(',', ''))
                    )
                    stock.add_data(daily_data)
                    recordCount += 1
                except:
                    continue
        driver.quit()
    return recordCount

# Import CSV file
def import_stock_web_csv(stock_list, symbol, filename):
    for stock in stock_list:
        if stock.symbol == symbol:
            with open(filename, newline='') as stockdata:
                datareader = csv.reader(stockdata, delimiter=',')
                next(datareader)
                for row in datareader:
                    daily_data = DailyData(datetime.strptime(row[0], "%Y-%m-%d"), float(row[4]), float(row[6]))
                    stock.add_data(daily_data)
