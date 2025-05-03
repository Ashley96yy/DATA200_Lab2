# Summary: This module contains the user interface and logic for a graphical user interface version of the stock manager program.

from datetime import datetime
from os import path
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog, filedialog
import csv
import stock_data
from stock_class import Stock, DailyData
from utilities import clear_screen, display_stock_chart, sortStocks, sortDailyData

class StockApp:
    def __init__(self):
        self.stock_list = []
        #check for database, create if not exists
        if path.exists("stocks.db") == False:
            stock_data.create_database()

 # This section creates the user interface

        # Create Window
        self.root = Tk()
        self.root.title("Stock Master") 
        self.root.geometry("800x600")

        # Add Menubar
        self.menubar = Menu(self.root)

        # Add File Menu
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load", command=self.load)
        self.filemenu.add_command(label="Save", command=self.save)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # Add Web Menu 
        self.webmenu = Menu(self.menubar, tearoff=0)
        self.webmenu.add_command(label="Get Data From Web", command=self.scrape_web_data)
        self.webmenu.add_command(label="Import CSV", command=self.importCSV_web_data)
        self.menubar.add_cascade(label="Web", menu=self.webmenu)

        # Add Chart Menu
        self.charmenu = Menu(self.menubar, tearoff=0)
        self.charmenu.add_command(label="Display Chart", command=self.display_chart)
        self.menubar.add_cascade(label="Chart", menu=self.charmenu)

        # Add menus to window       
        self.root.config(menu=self.menubar)

        # Create main frame
        main_frame = Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=BOTH, expand=True)

        # Create left frame for stock list
        left_frame = Frame(main_frame, padx=10, pady=200)
        left_frame.pack(side=LEFT, fill=Y)

        # Add heading information
        self.headingLabel = Label(left_frame, text="Select a Stock", font=("Arial", 16, "bold"))
        self.headingLabel.pack(pady=10)

        # Add stock list
        stock_frame = Frame(left_frame)
        stock_frame.pack(fill=BOTH, expand=True)
        stock_scroll = Scrollbar(stock_frame) 
        stock_scroll.pack(side=RIGHT, fill=Y)
        self.stockList = Listbox(stock_frame, yscrollcommand=stock_scroll.set, height=20)    
        self.stockList.bind('<<ListboxSelect>>', self.update_data)
        self.stockList.pack(fill=BOTH, expand=True)
        stock_scroll.config(command=self.stockList.yview)

        # Add tabs
        tab_control = ttk.Notebook(main_frame)

        # Set up main tab
        main_tab = Frame(tab_control)
        tab_control.add(main_tab, text='Main')

        # Add stock frame
        add_frame = LabelFrame(main_tab, text="Add Stock")
        add_frame.pack(fill=X, pady=5)

        Label(add_frame, text="Symbol").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.addSymbolEntry = Entry(add_frame)
        self.addSymbolEntry.grid(row=0, column=1, padx=5, pady=5)

        Label(add_frame, text="Name").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.addNameEntry = Entry(add_frame)
        self.addNameEntry.grid(row=1, column=1, padx=5, pady=5)

        Label(add_frame, text="Shares").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.addSharesEntry = Entry(add_frame)
        self.addSharesEntry.grid(row=2, column=1, padx=5, pady=5)

        add_button = Button(add_frame, text="Add Stock", command=self.add_stock)
        add_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Update stock frame
        update_frame = LabelFrame(main_tab, text="Update Shares")
        update_frame.pack(fill=X, pady=5)

        Label(update_frame, text="Shares:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.updateSharesEntry = Entry(update_frame)
        self.updateSharesEntry.grid(row=0, column=1, padx=5, pady=5)

        button_frame = Frame(update_frame)
        button_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        buy_button = Button(button_frame, text="Buy Shares", command=self.buy_shares)
        buy_button.pack(side=LEFT, padx=5)
        
        sell_button = Button(button_frame, text="Sell Shares", command=self.sell_shares)
        sell_button.pack(side=LEFT, padx=5)

        delete_button = Button(main_tab, text="Delete Stock", command=self.delete_stock)
        delete_button.pack(pady=10)

        # Setup history tab
        history_tab = ttk.Frame(tab_control)
        tab_control.add(history_tab, text="History")

        # Add text widget for displaying daily data
        history_frame = Frame(history_tab)
        history_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        history_scroll = Scrollbar(history_frame)
        history_scroll.pack(side=RIGHT, fill=Y)

        self.dailyDataList = Text(history_frame, width=40, height=20, yscrollcommand=history_scroll.set)
        self.dailyDataList.pack(fill=BOTH, expand=True)
        history_scroll.config(command=self.dailyDataList.yview)

        # Setup Report Tab
        report_tab = ttk.Frame(tab_control)
        tab_control.add(report_tab, text="Report")

        # Add Text widget for displaying report
        report_frame = Frame(report_tab)
        report_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        report_scroll = Scrollbar(report_frame)
        report_scroll.pack(side=RIGHT, fill=Y)

        self.stockReport = Text(report_frame, width=40, height=20, yscrollcommand=report_scroll.set)
        self.stockReport.pack(fill=BOTH, expand=True)
        report_scroll.config(command=self.stockReport.yview)

        # Pack the tab control
        tab_control.pack(fill=BOTH, expand=True)

        # Load existing data
        self.load()

        ## Call MainLoop
        self.root.mainloop()

# This section provides the functionality
       
    # Load stocks and history from database.
    def load(self):
        self.stockList.delete(0,END)
        stock_data.load_stock_data(self.stock_list)
        sortStocks(self.stock_list)
        for stock in self.stock_list:
            self.stockList.insert(END,stock.symbol)
        messagebox.showinfo("Load Data","Data Loaded")

    # Save stocks and history to database.
    def save(self):
        stock_data.save_stock_data(self.stock_list)
        messagebox.showinfo("Save Data","Data Saved")

    # Refresh history and report tabs
    def update_data(self, evt):
        if self.stockList.curselection():
            self.display_stock_data()

    # Display stock price and volume history.
    def display_stock_data(self):
        symbol = self.stockList.get(self.stockList.curselection())
        for stock in self.stock_list:
            if stock.symbol == symbol:
                self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
                self.dailyDataList.delete("1.0",END)
                self.stockReport.delete("1.0",END)
                self.dailyDataList.insert(END,"- Date -   - Price -   - Volume -\n")
                self.dailyDataList.insert(END,"=================================\n")
                
                # Sort daily data by date in descending order
                sortDailyData(stock.DataList)
                
                for daily_data in stock.DataList:
                    row = daily_data.date.strftime("%m/%d/%y") + "   " +  '${:0,.2f}'.format(daily_data.close) + "   " + str(daily_data.volume) + "\n"
                    self.dailyDataList.insert(END,row)

                # Display report
                self.stockReport.insert(END, f"Report for {stock.name} ({stock.symbol})\n")
                self.stockReport.insert(END, f"=================================\n\n")
                self.stockReport.insert(END, f"Shares Owned {stock.shares}\n")

                if len(stock.DataList) > 0:
                    latest_price = stock.DataList[0].close
                    self.stockReport.insert(END, f"Current Price: ${latest_price:.2f}\n")
                    self.stockReport.insert(END, f"Current Value: ${stock.shares * latest_price:.2f}\n\n")
                    
                    # Calculate gain/loss
                    if len(stock.DataList) > 1:
                        pre_price = stock.DataList[1].close
                        change = latest_price - pre_price
                        percent_change = (change / pre_price) * 100

                        self.stockReport.insert(END, f"Previous Close: ${pre_price:.2f}\n")
                        self.stockReport.insert(END, f"Price Change: ${change:.2f} ({percent_change:.2f}%)\n")

                        # Calculate portfolio change
                        portfolio_change = stock.shares * change
                        self.stockReport.insert(END, f"Portfolio Change: ${portfolio_change:.2f}\n")

                    # Add volume info
                    if len(stock.DataList) > 0:
                        self.stockReport.insert(END, f"\nLatest Volume: {stock.DataList[0].volume:,}\n")

                        # Calculate average volume
                        if len(stock.DataList) > 1:
                            total_volume = sum(data.volume for data in stock.DataList)
                            avg_volume = total_volume/ len(stock.DataList)
                            self.stockReport.insert(END, f"Average Volume: {avg_volume:,.0f}\n")
    
    # Add new stock to track.
    def add_stock(self):
        try:
            symbol = self.addSymbolEntry.get().strip().upper()
            name = self.addNameEntry.get().strip()
            shares = float(self.addSharesEntry.get().strip())

            if not symbol or not name:
                messagebox.showerror("Input Error", "Symbol and Name must not be empty")
                return
            
            # Check if stock already exists
            for stock in self.stock_list:
                if stock.symbol == symbol:
                    messagebox.showerror("Duplicate Stock", f"Stock {symbol} already exists!")
                    return
                
            new_stock = Stock(symbol, name, shares)
            self.stock_list.append(new_stock)
            self.stockList.insert(END,self.addSymbolEntry.get())
            self.addSymbolEntry.delete(0,END)
            self.addNameEntry.delete(0,END)
            self.addSharesEntry.delete(0,END)
            messagebox.showinfo("Stock Added", f"{symbol} added successfully!")
        except ValueError:
            messagebox.showerror("Input Error", "Shares must be a valid number!")

    # Buy shares of stock.
    def buy_shares(self):
        if not self.stockList.curselection():
            messagebox.showerror("Selecton Error", "Please select a stock first.")
            return
        
        try:
            shares = float(self.updateSharesEntry.get())
            if shares <= 0:
                messagebox.showerror("Input Error", "Shares must be greater than 0.")
                return
            
            symbol = self.stockList.get(self.stockList.curselection())
            for stock in self.stock_list:
                if stock.symbol == symbol:
                    stock.buy(float(self.updateSharesEntry.get()))
                    self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
            messagebox.showinfo("Buy Shares","Shares Purchased")
            self.updateSharesEntry.delete(0,END)
            self.display_stock_data()
        except ValueError:
            messagebox.showerror("Input Error", "Shares must be a valid number!")

    # Sell shares of stock.
    def sell_shares(self):
        if not self.stockList.curselection():
            messagebox.showerror("Selection Error", "Please select a stock first")
            return
            
        try:
            shares = float(self.updateSharesEntry.get())
            if shares <= 0:
                messagebox.showerror("Input Error", "Shares must be greater than 0")
                return
                
            symbol = self.stockList.get(self.stockList.curselection())
            for stock in self.stock_list:
                if stock.symbol == symbol:
                    if shares > stock.shares:
                        messagebox.showerror("Input Error", f"Cannot sell more than {stock.shares} shares")
                        return
                    stock.sell(shares)
                    self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
            messagebox.showinfo("Sell Shares", f"{shares} Shares Sold")
            self.updateSharesEntry.delete(0, END)
            self.display_stock_data()
        except ValueError:
            messagebox.showerror("Input Error", "Shares must be a valid number")

    # Remove stock and all history from being tracked.
    def delete_stock(self):
        if not self.stockList.curselection():
            messagebox.showerror("Selection Error", "Please select a stock to delete.")
            return
        symbol = self.stockList.get(self.stockList.curselection())
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {symbol}?")

        if confirm:
            # Remove from list
            index = 0
            for i, stock in enumerate(self.stock_list):
                if stock.symbol == symbol:
                    index = i
                    break
            self.stock_list.pop(index)

            # Update listbox
            self.stockList.delete(self.stockList.curselection())

            # Clear displays
            self.headingLabel['text'] = "Select a Stock"
            self.dailyDataList.delete("1.0", END)
            self.stockReport.delete("1.0", END)

            messagebox.showinfo("Delete Stock", f"{symbol} has been deleted")

    # Get data from web scraping.
    def scrape_web_data(self):
        if not self.stockList.curselection():
            messagebox.showerror("Selection Error", "Please select a stock first.")
            return
        
        dateFrom = simpledialog.askstring("Starting Date","Enter Starting Date (m/d/yy)")
        dateTo = simpledialog.askstring("Ending Date","Enter Ending Date (m/d/yy")

        if not dateFrom or not dateTo:
            return
        
        try:
            stock_data.retrieve_stock_web(dateFrom,dateTo,self.stock_list)
        except:
            messagebox.showerror("Cannot Get Data from Web", "Error: Check Path for Chrome Driver")
            return
        
        self.display_stock_data()
        messagebox.showinfo("Get Data From Web", "Data Retrieved")

    # Import CSV stock history file.
    def importCSV_web_data(self):
        if not self.stockList.curselection():
            messagebox.showerror("Selection Error", "Please select a stock first.")
            return
        
        symbol = self.stockList.get(self.stockList.curselection())
        filename = filedialog.askopenfilename(title="Select " + symbol + " File to Import",filetypes=[('Yahoo Finance! CSV','*.csv')])
        if filename != "":
            try:
                stock_data.import_stock_web_csv(self.stock_list,symbol,filename)
                self.display_stock_data()
                messagebox.showinfo("Import Complete",symbol + "Import Complete") 
            except Exception as e:
                messagebox.showerror("Import Error", f"Error importing data: {str(e)}")  
        
    # Display stock price chart.
    def display_chart(self):
        if not self.stockList.curselection():
            messagebox.showerror("Selection Error", "Please select a stock first.")
            return
        
        symbol = self.stockList.get(self.stockList.curselection())
        try:
            display_stock_chart(self.stock_list,symbol)
        except Exception as e:
            messagebox.showerror("Chart Error", f"Error displaying chart: {str(e)}")

def main():
        app = StockApp()
        

if __name__ == "__main__":
    # execute only if run as a script
    main()