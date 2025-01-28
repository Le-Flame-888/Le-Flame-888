import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from calendar import monthrange

class ReportsTab(ttk.Frame):
    def __init__(self, parent, db_connection):
        super().__init__(parent)
        self.db = db_connection
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frames
        self.controls_frame = self.create_controls_frame()
        self.report_frame = self.create_report_frame()
        
        # Layout frames
        self.controls_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.report_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
    def create_controls_frame(self):
        frame = ttk.LabelFrame(self, text="Report Controls")
        
        # Report Type Selection
        ttk.Label(frame, text="Report Type:").grid(row=0, column=0, padx=5, pady=5)
        self.report_type = ttk.Combobox(frame, values=[
            "Occupancy Rate",
            "Revenue Analysis",
            "Reservation Status",
            "Room Type Distribution",
            "Guest Statistics"
        ])
        self.report_type.grid(row=0, column=1, padx=5, pady=5)
        self.report_type.bind('<<ComboboxSelected>>', self.on_report_type_change)
        
        # Date Range
        date_frame = ttk.Frame(frame)
        date_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Label(date_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.date_from = DateEntry(date_frame, width=12)
        self.date_from.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.date_to = DateEntry(date_frame, width=12)
        self.date_to.pack(side=tk.LEFT, padx=5)
        
        # Quick Date Selections
        quick_date_frame = ttk.Frame(frame)
        quick_date_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(quick_date_frame, text="Last 7 Days", 
                  command=lambda: self.set_date_range(7)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_date_frame, text="Last 30 Days", 
                  command=lambda: self.set_date_range(30)).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_date_frame, text="This Month", 
                  command=self.set_this_month).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_date_frame, text="This Year", 
                  command=self.set_this_year).pack(side=tk.LEFT, padx=5)
        
        # Generate Report Button
        ttk.Button(frame, text="Generate Report", 
                  command=self.generate_report).grid(row=3, column=0, columnspan=2, pady=10)
        
        return frame
        
    def create_report_frame(self):
        frame = ttk.LabelFrame(self, text="Report View")
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs for different views
        self.chart_frame = ttk.Frame(self.notebook)
        self.table_frame = ttk.Frame(self.notebook)
        self.summary_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.chart_frame, text="Chart View")
        self.notebook.add(self.table_frame, text="Table View")
        self.notebook.add(self.summary_frame, text="Summary")
        
        return frame
    
    def set_date_range(self, days):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        self.date_from.set_date(start_date)
        self.date_to.set_date(end_date)
    
    def set_this_month(self):
        today = datetime.now()
        first_day = today.replace(day=1)
        last_day = today.replace(day=monthrange(today.year, today.month)[1])
        self.date_from.set_date(first_day)
        self.date_to.set_date(last_day)
    
    def set_this_year(self):
        today = datetime.now()
        first_day = today.replace(month=1, day=1)
        last_day = today.replace(month=12, day=31)
        self.date_from.set_date(first_day)
        self.date_to.set_date(last_day)
    
    def generate_report(self):
        report_type = self.report_type.get()
        date_from = self.date_from.get_date()
        date_to = self.date_to.get_date()
        
        if not report_type:
            tk.messagebox.showerror("Error", "Please select a report type")
            return
            
        try:
            if report_type == "Occupancy Rate":
                self.generate_occupancy_report(date_from, date_to)
            elif report_type == "Revenue Analysis":
                self.generate_revenue_report(date_from, date_to)
            elif report_type == "Reservation Status":
                self.generate_status_report(date_from, date_to)
            elif report_type == "Room Type Distribution":
                self.generate_room_type_report(date_from, date_to)
            elif report_type == "Guest Statistics":
                self.generate_guest_statistics(date_from, date_to)
                
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_occupancy_report(self, date_from, date_to):
        # Fetch occupancy data
        query = """
        SELECT date(check_in_date) as date,
               COUNT(*) as occupied_rooms,
               (SELECT COUNT(*) FROM rooms) as total_rooms
        FROM reservations
        WHERE check_in_date BETWEEN ? AND ?
        AND status != 'Cancelled'
        GROUP BY date
        ORDER BY date
        """
        df = pd.read_sql_query(query, self.db, params=(date_from, date_to))
        
        # Calculate occupancy rate
        df['occupancy_rate'] = (df['occupied_rooms'] / df['total_rooms']) * 100
        
        # Create chart
        self.clear_chart_frame()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df['date'], df['occupancy_rate'], marker='o')
        ax.set_title('Daily Occupancy Rate')
        ax.set_xlabel('Date')
        ax.set_ylabel('Occupancy Rate (%)')
        ax.grid(True)
        plt.xticks(rotation=45)
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create table view
        self.show_table_view(df[['date', 'occupied_rooms', 'total_rooms', 'occupancy_rate']])
        
        # Create summary
        summary = f"""
        Average Occupancy Rate: {df['occupancy_rate'].mean():.2f}%
        Maximum Occupancy Rate: {df['occupancy_rate'].max():.2f}%
        Minimum Occupancy Rate: {df['occupancy_rate'].min():.2f}%
        """
        self.show_summary(summary)
    
    def generate_revenue_report(self, date_from, date_to):
        query = """
        SELECT date(check_in_date) as date,
               COUNT(*) as bookings,
               SUM(r.rate) as daily_revenue
        FROM reservations res
        JOIN rooms r ON res.room_number = r.room_number
        WHERE check_in_date BETWEEN ? AND ?
        AND status != 'Cancelled'
        GROUP BY date
        ORDER BY date
        """
        df = pd.read_sql_query(query, self.db, params=(date_from, date_to))
        
        # Create chart
        self.clear_chart_frame()
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Revenue chart
        ax1.bar(df['date'], df['daily_revenue'])
        ax1.set_title('Daily Revenue')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Revenue ($)')
        ax1.grid(True)
        plt.xticks(rotation=45)
        
        # Bookings chart
        ax2.bar(df['date'], df['bookings'], color='green')
        ax2.set_title('Daily Bookings')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Number of Bookings')
        ax2.grid(True)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create table view
        self.show_table_view(df)
        
        # Create summary
        summary = f"""
        Total Revenue: ${df['daily_revenue'].sum():.2f}
        Average Daily Revenue: ${df['daily_revenue'].mean():.2f}
        Total Bookings: {df['bookings'].sum()}
        Average Daily Bookings: {df['bookings'].mean():.2f}
        """
        self.show_summary(summary)
    
    def clear_chart_frame(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
    
    def show_table_view(self, df):
        # Clear existing table
        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
        # Create Treeview
        tree = ttk.Treeview(self.table_frame, columns=list(df.columns), show='headings')
        
        # Add scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Set column headings
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add data
        for idx, row in df.iterrows():
            tree.insert('', 'end', values=list(row))
        
        # Layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
    
    def show_summary(self, summary_text):
        # Clear existing summary
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
            
        # Create text widget
        text_widget = tk.Text(self.summary_frame, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert('1.0', summary_text)
        text_widget.configure(state='disabled')
        text_widget.pack(fill=tk.BOTH, expand=True)
    
    def on_report_type_change(self, event=None):
        # Clear existing report views
        self.clear_chart_frame()
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        for widget in self.summary_frame.winfo_children():
            widget.destroy()