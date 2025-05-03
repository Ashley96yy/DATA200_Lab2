# Summary: This module contains the user interface and logic for a console-based version of the stock manager program.

from datetime import datetime, timezone
from stock_class import Stock, DailyData
from utilities import clear_screen, display_stock_chart
from os import path
import stock_data
import yfinance as yf
import sqlite3
import holidays
import pytz

# Main Menu
def main_menu(stock_list):
    option = ""
    while option != "0":
        clear_screen()
        print("Stock Analyzer ---")
        print("1 - Manage Stocks (Add, Update, Delete, List)")
        print("2 - Add Daily Stock Data (Date, Price, Volume)")
        print("3 - Show Report")
        print("4 - Show Chart")
        print("5 - Manage Data (Save, Load, Retrieve)")
        print("0 - Exit Program")
        option = input("Enter Menu Option: ")
        while option not in ["1","2","3","4","5","0"]:
            clear_screen()
            print("*** Invalid Option - Try again ***")
            print("Stock Analyzer ---")
            print("1 - Manage Stocks (Add, Update, Delete, List)")
            print("2 - Add Daily Stock Data (Date, Price, Volume)")
            print("3 - Show Report")
            print("4 - Show Chart")
            print("5 - Manage Data (Save, Load, Retrieve)")
            print("0 - Exit Program")
            option = input("Enter Menu Option: ")
        if option == "1":
            manage_stocks(stock_list)
        elif option == "2":
            add_stock_data(stock_list)
        elif option == "3":
            display_report(stock_list)
        elif option == "4":
            display_chart(stock_list)
        elif option == "5":
            manage_data(stock_list)
        else:
            clear_screen()
            print("Goodbye")

# Manage Stocks
def manage_stocks(stock_list):
    option = ""
    while option != "0":
        clear_screen()
        print("Manage Stocks ---")
        print("1 - Add Stock")
        print("2 - Update Shares")
        print("3 - Delete Stock")
        print("4 - List Stocks")
        print("0 - Exit Manage Stocks")
        option = input("Enter Menu Option: ")
        while option not in ["1","2","3","4","0"]:
            clear_screen()
            print("*** Invalid Option - Try again ***")
            print("1 - Add Stock")
            print("2 - Update Shares")
            print("3 - Delete Stock")
            print("4 - List Stocks")
            print("0 - Exit Manage Stocks")
            option = input("Enter Menu Option: ")
        if option == "1":
            add_stock(stock_list)
        elif option == "2":
            update_shares(stock_list)
        elif option == "3":
            delete_stock(stock_list)
        elif option == "4":
            list_stocks(stock_list)
        else:
            print("Returning to Main Menu")

# Add new stock to track
def add_stock(stock_list):
    option = ""
    while option != "0":
        clear_screen()
        print("Add Stock ---")
        symbol = input("Enter Stock Symbol: ").upper()

        # Check if stock already exists
        for stock in stock_list: 
            if stock.symbol == symbol:
                print(f"Error: Stock symbol {symbol} already exists in list.")
                _ = input("Press Enter to continue...")
                return
        
        # Auto-fetch company name using yfinance
        try:
            stock_info = yf.Ticker(symbol)
            name = stock_info.info['longName']
        except:
            name = None
        if not name:
            print(f"Error: Unable to fetch company name for {symbol}.")
            _ = input("Press Enter to continue...")
            return
        print(f"Company Name Found: {name}")

        try:
            shares = float(input("Enter Number of Shares: "))
        except ValueError:
            print("Error: Invalid number of shares. Please enter a numeric value.")
            _ = input("Press Enter to continue...")
            return
        
        new_stock = Stock(symbol, name, shares)
        stock_list.append(new_stock)

        print(f"Stock {symbol} ({name}) with {shares} added to list.")
        option = input("Press Enter to add another stock or 0 to exit: ")

##### In real-world stock markets:
"""Market Open (Weekday + Not Holiday + 9:30–16:00): Use real-time price
   Otherwise: 	Use latest close price"""
# Get latest close price
def get_latest_close_price(stock):
    if not stock.DataList:
        return None
    latest_data = sorted(stock.DataList, key=lambda x: x.date, reverse=True)[0]
    return latest_data.close

# Get real-time price
def get_real_time_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        return stock.fast_info['last_price']
    except:
        return None

# Check if the day is holidy
def is_us_holiday(date=None):
    us_holidays = holidays.US()
    if date is None:
        date = datetime.now().date()
    return date in us_holidays
    
# Check if the market is open right now
def is_market_open_now():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(tz=eastern)
    weekday = now.weekday()

    # Check for weekend
    if weekday >= 5:
        return False
    
    # Check for US holiday
    if is_us_holiday(now.date()):
        return False
    
    # Check for market hours (9:30 AM - 4:00 PM EST)
    hour = now.hour
    minute = now.minute
    current_minutes = hour * 60 + minute
    return 570 <= current_minutes <= 960 # Between 9:30 AM and 4:00 PM EST

# Insert transaction into database
def log_transaction(symbol, transaction_type, shares, price, date):
    conn = sqlite3.connect("stocks.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions (symbol, type, shares, price, date)
        VALUES (?, ?, ?, ?, ?);
    """, (symbol, transaction_type, shares, price, date.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
        
# Buy or Sell Shares Menu
def update_shares(stock_list):
    option = ""
    while option != "0":
        clear_screen()
        print("Update Shares ---")
        print("1 - Buy Shares")
        print("2 - Sell Shares")
        print("0 - Exit Update Shares")
        option = input("Enter Menu Option: ")

        while option not in ["1","2","0"]:
            clear_screen()
            print("*** Invalid Option - Try again ***")
            print("1 - Buy Shares")
            print("2 - Sell Shares")
            print("0 - Exit Update Shares")
            option = input("Enter Menu Option: ")
        
        if option == "1":
            buy_stock(stock_list)
        elif option == "2":
            sell_stock(stock_list)
        else:
            print("Returning to Manage Stocks Menu")

# Buy Stocks (add to shares)
def buy_stock(stock_list):
    clear_screen()
    print("Buy Shares ---")
    print("Stock List: [",end="")
    for i, stock in enumerate(stock_list):
        if i < len(stock_list) - 1:
            print(f"{stock.symbol}", end=", ")
        else:
            print(f"{stock.symbol}]")
    
    symbol = input("Enter Stock Symbol: ").upper()

    # Find the stock in the list
    for stock in stock_list:
        if stock.symbol == symbol:
            try:
                shares = float(input(f"Enter number of shares to buy for {symbol}: "))
                if shares <= 0:
                    print("Error: Number of shares must be positive.")
                    _ = input("Press Enter to continue...")
                    return
                
                # Ask for transaction date
                date_str = input("Enter transaction date (MM/DD/YYYY [Leave Blank for today]: ")
                if date_str == "":
                    transaction_date = datetime.now()
                    if is_market_open_now():
                        price = get_real_time_price(symbol)
                        if price is None:
                            price = get_latest_close_price(stock)
                            print("Market open, but failed to get real-time price. Using last close price instead.")
                    else:
                        price = get_latest_close_price(stock)
                        print("Market closed. Using last close price.")
                else:
                    transaction_date = datetime.strptime(date_str, "%m/%d/%Y")
                    price = None
                    for daily in stock.DataList:
                        if daily.date.strftime("%m/%d/%Y") == date_str:
                            price = daily.close
                            break
                    if price is None:
                        print("Error: No market data for that date.")
                        return
                    
                stock.buy(shares)
                log_transaction(symbol, "BUY", shares, price, transaction_date)

                print(f"Bought {shares} shares of {symbol} at ${price} on {transaction_date.strftime('%m/%d/%Y')}.")
                print(f"Total shares of {symbol}: {stock.shares}")
            except ValueError:
                print("Error: Invalid number of shares. Please enter a numeric value.")
            return
    print(f"Error: Stock symbol {symbol} not found in list.")
    _ = input("Press Enter to continue...")

# Sell Stocks (subtract from shares)
def sell_stock(stock_list):
    clear_screen()
    print("Sell Shares ---")
    print("Stock List: [",end="")
    for i, stock in enumerate(stock_list):
        if i < len(stock_list) - 1:
            print(f"{stock.symbol}", end=", ")
        else:
            print(f"{stock.symbol}]")

    symbol = input("Enter Stock Symbol: ").upper()

    # Find the stock in the list
    for stock in stock_list:
        if stock.symbol == symbol:
            try:
                shares = float(input(f"Enter number of shares to sell for {symbol}: "))
                if shares <= 0:
                    print("Error: Number of shares must be positive.")
                    _ = input("Press Enter to continue...")
                    return
                # Check if we have enough shares to sell
                if shares > stock.shares:
                    print(f"Error: Not enough shares of {symbol} to sell.")
                    _ = input("Press Enter to continue...")
                    return
                
                date_str = input("Enter transaction date (MM/DD/YYYY [Leave Blank for today]: ")
                if date_str == "":
                    transaction_date = datetime.now()
                    if is_market_open_now():
                        price = get_real_time_price(symbol)
                        if price is None:
                            price = get_latest_close_price(stock)
                            print("Market open, but failed to get real-time price. Using last close price instead.")
                    else:
                        price = get_latest_close_price(stock)
                        print("Market closed. Using last close price.")
                else:
                    transaction_date = datetime.strptime(date_str, "%m/%d/%Y")
                    price = None
                    for daily in stock.DataList:
                        if daily.date.strftime("%m/%d/%Y") == date_str:
                            price = daily.close
                            break
                    if price is None:
                        print("Error: No market data for that date.")
                        return
                    
                    stock.sell(shares)
                    log_transaction(symbol, "SELL", shares, price, transaction_date)

                    print(f"Sold {shares} shares of {symbol} at ${price} on {transaction_date.strftime('%m/%d/%Y')}.")
                    print(f"Total shares of {symbol}: {stock.shares}")
            except ValueError:
                print("Error: Invalid number of shares. Please enter a numeric value.")
            return
    print(f"Error: Stock symbol {symbol} not found in list.")
    _ = input("Press Enter to continue...")

# Remove stock and all daily data
def delete_stock(stock_list):
    clear_screen()
    print("Delete Stock ---")
    print("Stock List: [",end="")
    for i, stock in enumerate(stock_list):
        if i < len(stock_list) - 1:
            print(f"{stock.symbol}", end=", ")
        else:
            print(f"{stock.symbol}]")
    
    symbol = input("Enter Stock Symbol to delete: ").upper()

    # Find the stock in the list
    for i, stock in enumerate(stock_list):
        if stock.symbol == symbol:
            confirm = input(f"Are you sure you want to delete {stock.name} ({symbol})? (y/n): ").lower()
            if confirm == "y":
                stock_list.pop(i)
                print(f"Deleted {stock.name} ({symbol}) from list.")
            else:
                print(f"Deletion of {stock.name} ({symbol}) cancelled.")
            break
    
    else:
        print(f"Error: Stock symbol {symbol} not found in list.")
    _ = input("Press Enter to continue...")

# List stocks being tracked
def list_stocks(stock_list):
    clear_screen()
    print("List Stocks ---")

    for stock in stock_list:
        print(f"{stock.symbol}\t{stock.name}\t{stock.shares}shares")
    _ = input("Press Enter to continue...")

# Add Daily Stock Data
def add_stock_data(stock_list):
    clear_screen()
    print("Add Daily Stock Data ---")

    if len(stock_list) == 0:
        print("No stocks in list. Please add stocks first.")
        _ = input("Press Enter to continue...")
        return
    
    print("1 - Fetch from Web (Recommended)")
    print("2 - Manual Enter Daily Data")
    print("0 - Back to Main Menu")
    option = input("Enter Menu Option: ")

    while option not in ["1","2","0"]:
        clear_screen()
        print("*** Invalid Option - Try again ***")
        print("1 - Fetch from Web (Recommended)")
        print("2 - Manual Enter Daily Data")
        print("0 - Back to Main Menu")
        option = input("Enter Menu Option: ")
    if option == "1":
        retrieve_from_web(stock_list)
    elif option == "2":
        manual_add_data(stock_list)
    else:
        print("Returning to Main Menu")

def manual_add_data(stock_list):
    clear_screen()
    print("Manual Add Daily Stock Data ---")

    print("Stock List: [",end="")
    for i, stock in enumerate(stock_list):
        if i < len(stock_list) - 1:
            print(f"{stock.symbol}", end=", ")
        else:
            print(f"{stock.symbol}]")
    
    symbol = input("Enter Stock Symbol: ").upper()

    # Find the stock in the list
    for stock in stock_list:
        if stock.symbol == symbol:
            date_str = input("Enter Date (MM/DD/YYYY): ")

            try:
                data_obj = datetime.strptime(date_str, "%m/%d/%Y")

                # Check if date already exists
                for daily_data in stock.DataList:
                    if daily_data.date.strftime("%m/%d/%Y") == date_str:
                        print(f"Error: Data for {symbol} on {date_str} already exists.")
                        _ = input("Press Enter to continue...")
                        return
                
                price = float(input("Enter Closing Price: "))
                volume = float(input("Enter Trading Volume: "))

                daily_data = DailyData(data_obj, price, volume)
                stock.add_data(daily_data)
                print(f"Data added for {symbol} on {date_str}.")
            except ValueError:
                print("Error: Invalid data format or numeric value")
            _ = input("Press Enter to continue...")
            return
            
        print(f"Error: Stock symbol {symbol} not found in list.")
        _ = input("Press Enter to continue...")

# Display Report for All Stocks
def display_report(stock_data):
    clear_screen()
    print("Stock Report ---")
    print("SYMBOL\tNAME\t\tSHARES\tCURRENT\tMKT VALUE")
    print("=" * 60)

    for stock in stock_data:
        # Calculate current price and market value
        current_price = 0
        if len(stock.DataList) > 0:
            stock.DataList.sort(key=lambda x: x.date, reverse=True)
            current_price = stock.DataList[0].close
        
        market_value = current_price * stock.shares
        print(f"{stock.symbol}\t{stock.name}\t{stock.shares}\t{current_price:.2f}\t{market_value:.2f}")

        # If there's price history, show change
        if len(stock.DataList) > 1:
            prev_price = stock.DataList[1].close
            change = current_price - prev_price
            percent = (change / prev_price) * 100
            print(f"\tPrevious Close: ${prev_price:.2f}")
            print(f"\tChange: ${change:.2f} ({percent:.2f}%)")
        
        print("-" * 60)
    
    _= input("Press Enter to continue...")

# Display Chart
def display_chart(stock_list):
    print("Display Chart ---")
    print("Stock List: [",end="")
    for i, stock in enumerate(stock_list):
        if i < len(stock_list) - 1:
            print(f"{stock.symbol}", end=", ")
        else:
            print(f"{stock.symbol}]")
    
    symbol = input("Enter Stock Symbol: ").upper()

    display_stock_chart(stock_list, symbol)
    
    _ = input("Press Enter to continue...")

# Manage Data Menu
def manage_data(stock_list):
    option = ""
    while option != "0":
        clear_screen()
        print("Manage Data ---")
        print("1 - Save Data to Database")
        print("2 - Load Data from Database")
        print("3 - Retrieve Data from Web")
        print("4 - Import Data from CSV")
        print("0 - Exit Manage Data")
        option = input("Enter Menu Option: ")

        while option not in ["1","2","3","4","0"]:
            clear_screen()
            print("*** Invalid Option - Try again ***")
            print("1 - Save Data to Database")
            print("2 - Load Data from Database")
            print("3 - Retrieve Data from Web")
            print("4 - Import Data from CSV")
            print("0 - Exit Manage Data")
            option = input("Enter Menu Option: ")
        
        if option == "1":
            stock_data.save_stock_data(stock_list)
            print("Data saved to database.")
            _ = input("Press Enter to continue...")
        elif option == "2":
            stock_data.load_stock_data(stock_list)
            print("Data loaded from database.")
            _ = input("Press Enter to continue...")
        elif option == "3":
            retrieve_from_web(stock_list)
        elif option == "4":
            import_csv(stock_list)

# Get stock price and volume history from Yahoo! Finance using Web Scraping
def retrieve_from_web(stock_list):
    clear_screen()
    print("Retrieve Data from Web ---")

    # Check if there are any stocks to retrieve data for
    if len(stock_list) == 0:
        print("No stocks in the list. Please add stocks first.")
        _ = input("Press Enter to continue...")
        return
    
    # Display available stocks
    print("Stock List: [", end="")
    for i, stock in enumerate(stock_list):
        if i < len(stock_list) - 1:
            print(f"{stock.symbol}", end=", ")
        else:
            print(f"{stock.symbol}]")

    # Get the stock symbol
    symbol = input("Enter stock symbol to retrieve data for (or 'ALL' for all stocks): ").upper()
    
    if symbol != "ALL" and not any(stock.symbol == symbol for stock in stock_list):
        print(f"Symbol {symbol} not found in your stock list.")
        _ = input("Press Enter to continue...")
        return

     # Get date range
    print("\nEnter date range for stock data:")
    start_date = input("Enter start date (mm/dd/yy): ")
    end_date = input("Enter end date (mm/dd/yy): ")

    # Validate date format
    try:
        datetime.strptime(start_date, "%m/%d/%y")
        datetime.strptime(end_date, "%m/%d/%y")
    except ValueError:
        print("Invalid date format. Please use mm/dd/yy format.")
        _ = input("Press Enter to continue...")
        return
    
    # Create a filtered list of stocks based on user selection
    selected_stocks = []
    if symbol == "ALL":
        selected_stocks = stock_list.copy()
    else:
        for stock in stock_list:
            if stock.symbol == symbol:
                selected_stocks.append(stock)
                break
    
    print("\nRetrieving data from Yahoo Finance...")
    print("This may take a few moments...")
    
    try:
        # Use the function from stock_data module
        record_count = stock_data.retrieve_stock_web(start_date, end_date, selected_stocks)
        print(f"\nSuccessfully retrieved {record_count} records.")
    except Exception as e:
        print(f"\nError retrieving data: {str(e)}")
        print("Make sure Chrome and Chrome WebDriver are properly installed.")
    
    _ = input("\nPress Enter to continue...")

# Import stock price and volume history from Yahoo! Finance using CSV Import
def import_csv(stock_list):
    clear_screen()
    print("Import Data from CSV ---")

    # Check if there are any stocks to import data for
    if len(stock_list) == 0:
        print("No stocks in the list. Please add stocks first.")
        _ = input("Press Enter to continue...")
        return
    
    # Display available stocks
    print("Stock List: [", end="")
    for i, stock in enumerate(stock_list):
        if i < len(stock_list) - 1:
            print(f"{stock.symbol}", end=", ")
        else:
            print(f"{stock.symbol}]")
    
    # Get the stock symbol
    symbol = input("Enter stock symbol to import data for: ").upper()
    
    # Check if symbol exists in list
    found = False
    for stock in stock_list:
        if stock.symbol == symbol:
            found = True
            break
    
    if not found:
        print(f"Symbol {symbol} not found in your stock list.")
        _ = input("Press Enter to continue...")
        return
    
    # Get filename
    print("\nPlease select the CSV file to import.")
    print("Note: The file should be in Yahoo Finance CSV format.")
    filename = input("Enter the full path to the CSV file: ")
    
    if not path.exists(filename):
        print(f"File not found: {filename}")
        _ = input("Press Enter to continue...")
        return
    
    try:
        # Use the function from stock_data module
        stock_data.import_stock_web_csv(stock_list, symbol, filename)
        print(f"\nSuccessfully imported data for {symbol}.")
    except Exception as e:
        print(f"\nError importing CSV: {str(e)}")
    
    _ = input("\nPress Enter to continue...")

# Begin program
def main():
    #check for database, create if not exists
    if path.exists("stocks.db") == False:
        stock_data.create_database()
    stock_list = []

    # Load existing data
    stock_data.load_stock_data(stock_list)
    
    main_menu(stock_list)

# Program Starts Here
if __name__ == "__main__":
    # execute only if run as a stand-alone script
    main()