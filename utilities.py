#Helper Functions

import matplotlib.pyplot as plt

from os import system, name

# Function to Clear the Screen
def clear_screen():
    if name == "nt": # User is running Windows
        _ = system('cls')
    else: # User is running Linux or Mac
        _ = system('clear')

# Function to sort the stock list (alphabetical)
def sortStocks(stock_list):
    ## Sort the stock list
    stock_list.sort(key=lambda x: x.symbol)


# Function to sort the daily stock data (oldest to newest) for all stocks
def sortDailyData(stock_list):
    for stock in stock_list:
        stock.DataList.sort(key=lambda x: x.date)

# Function to create stock chart
def display_stock_chart(stock_list,symbol):
    # Find the stock in the list
    selected_stock = None
    for stock in stock_list:
        if stock.symbol == symbol:
            selected_stock = stock
            break
    
    if not selected_stock or not selected_stock.DataList:
        print(f"No data available for {symbol}")
        return
    
    # Sort data chronologically (oldest to newest) for the chart
    chart_data = sorted(selected_stock.DataList, key=lambda x: x.date)
    
    # Extract dates and prices
    dates = [data.date for data in chart_data]
    prices = [data.close for data in chart_data]
    volumes = [data.volume for data in chart_data]
    
    # Create a figure with 2 subplots (price and volume)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # Plot price data
    ax1.plot(dates, prices, 'b-', linewidth=2)
    ax1.set_title(f'{selected_stock.name} ({symbol}) - Price History')
    ax1.set_ylabel('Price ($)')
    ax1.grid(True)
    
    # Plot volume data as a bar chart
    ax2.bar(dates, volumes, color='g', alpha=0.5)
    ax2.set_ylabel('Volume')
    ax2.set_xlabel('Date')
    ax2.grid(True)
    
    # Format the figure
    plt.tight_layout()
    
    # Rotate date labels if there are many data points
    if len(dates) > 10:
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    # Show the chart
    plt.show()