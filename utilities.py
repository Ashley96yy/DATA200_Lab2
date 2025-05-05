#Helper Functions

import matplotlib.pyplot as plt

from os import system, name

# Function to Clear the Screen
def clear_screen():
    if name == "nt": 
        system('cls')
    else: 
        system('clear')

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
    selected_stock = None
    for stock in stock_list:
        if stock.symbol == symbol:
            selected_stock = stock
            break
    
    if not selected_stock or not selected_stock.DataList:
        print(f"No data available for {symbol}")
        return
    
    # Sort data from oldest to newest
    chart_data = sorted(selected_stock.DataList, key=lambda x: x.date)
    
    dates = [data.date for data in chart_data]
    prices = [data.close for data in chart_data]
    volumes = [data.volume for data in chart_data]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # Plot price data
    ax1.plot(dates, prices, color='#1f77b4', linewidth=2, marker='o', markersize=4)
    ax1.fill_between(dates, prices, color='#1f77b4', alpha=0.1)
    ax1.set_title(f'{selected_stock.name} ({symbol}) - Price History', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Plot volume data
    ax2.bar(dates, volumes, color='#2ca02c', alpha=0.6)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    
    if len(dates) > 10:
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    plt.show()