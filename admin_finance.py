import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector
from datetime import datetime
import certifi
import csv
import os

DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "convenient_shop"
DB_USER = "root"
DB_PASS = "SECRET"

def get_db_connection():
    # Use buffered=True to fetch all results immediately, preventing conn timeout issues
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME, ssl_ca=certifi.where()
    )

def safe_query(query, params=()):
    """Executes a SELECT query and returns all results as a list of dictionaries."""
    try:
        conn = get_db_connection()
    except mysql.connector.Error as e:
        # Re-raise as a standard Python error for easier handling
        raise ConnectionError(f"DB connection failed: {e}")
    
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

# Fetchers (updated to use check_out table and handle NULLs)
def fetch_finance_transactions(limit=500):
    
    try:
        q = """
        SELECT
            cart_id AS trans_id,
            MAX(date) AS trans_date,
            'Checkout' AS type,
            MAX(IFNULL(total, 0.00)) AS amount,
            'N/A' AS payment_method, 
            NULL AS employee_id      
        FROM check_out
        GROUP BY cart_id
        ORDER BY trans_date DESC LIMIT %s
        """
        rows = safe_query(q, (limit,))
        for r in rows:
            r['trans_date'] = r['trans_date']
        return rows
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []

def fetch_sales_data_for_plot():
    try:
        q = """
        SELECT
            DATE(t.trans_date) AS sale_day,
            SUM(t.trans_total) AS total_sales
        FROM (
            SELECT 
                cart_id, 
                MAX(date) AS trans_date, 
                MAX(IFNULL(total, 0.00)) AS trans_total
            FROM check_out
            GROUP BY cart_id
        ) AS t
        WHERE t.trans_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY sale_day
        ORDER BY sale_day ASC
        """
        rows = safe_query(q)
        return rows
    except Exception as e:
        print(f"Error fetching plot data: {e}")
        return []

def fetch_summary_data():
    """
    Fetches key financial summary metrics from check_out.
    Aggregates unique transactions (based on cart_id) for accurate counts/sums.
    Uses IFNULL to prevent NULL totals/item_totals.
    """
    summary = {}
    try:
        # Total Sales Last 30 Days and Total Orders (Unique Cart IDs)
        q_sales = """
        SELECT 
            SUM(t.trans_total) AS total_sales,
            COUNT(t.cart_id) AS total_orders
        FROM (
            SELECT cart_id, MAX(date) AS trans_date, MAX(IFNULL(total, 0.00)) AS trans_total
            FROM check_out
            GROUP BY cart_id
        ) AS t
        WHERE t.trans_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """
        result = safe_query(q_sales)
        summary.update(result[0] if result and result[0]['total_sales'] is not None else {'total_sales': 0, 'total_orders': 0})

        # Top 5 Products by Revenue (using item_total)
        q_top_products = """
        SELECT
            items AS name,
            SUM(IFNULL(item_total, 0.00)) AS revenue
        FROM check_out
        GROUP BY items
        ORDER BY revenue DESC
        LIMIT 5
        """
        summary['top_products'] = safe_query(q_top_products)
        
        return summary
    except Exception as e:
        print(f"Error fetching summary data: {e}")
        return {}

class FinanceApp(ctk.CTkScrollableFrame):
    def __init__(self, master):
        # Using CTkScrollableFrame as the primary container for all content
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        
        # 1. Fetch Data
        self.summary_data = fetch_summary_data()
        self.data = fetch_finance_transactions() # Transactions data
        self.row_counter = 0 # To manage grid rows inside the scrollable frame
 
        self.create_summary_widgets() 
        
        # 3. Build Transactions Table
        self.create_transactions_widgets() 

    def create_metric_card(self, parent, col, title, value, color):
        card = ctk.CTkFrame(parent, fg_color="white")
        card.grid(row=0, column=col, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(padx=10, pady=(5, 0))
        ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold"), text_color=color).pack(padx=10, pady=(0, 5))

    def create_sales_chart(self, parent):
        ctk.CTkLabel(parent, text="Daily Sales Trend (Last 30 Days)", font=("Arial", 16, "bold"), anchor="w").pack(padx=20, pady=(10, 5), fill="x")

        data = fetch_sales_data_for_plot()
        
        dates = [r['sale_day'] for r in data]
        sales = [r['total_sales'] for r in data]

        if not dates:
            ctk.CTkLabel(parent, text="No sales data available for the last 30 days.", 
                         font=("Arial", 14), text_color="#777777").pack(padx=20, pady=40)
            return

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(dates, sales, marker='o', linestyle='-', color='#A9A1E0')
        ax.set_title('Sales Over Time', fontsize=14)
        ax.set_ylabel('Total Sales ($)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        num_labels = min(5, len(dates))
        skip = max(1, len(dates) // num_labels)
        ax.set_xticks(dates[::skip])
        ax.set_xticklabels([d.strftime('%m-%d') for d in dates[::skip]], rotation=45, ha='right', fontsize=10)
        
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    def create_top_products_list(self, parent):
        ctk.CTkLabel(parent, text="Top 5 Products by Revenue", font=("Arial", 16, "bold"), anchor="w").pack(padx=20, pady=(10, 5), fill="x")
        
        products_data = self.summary_data.get('top_products', [])
        
        list_frame = ctk.CTkFrame(parent, fg_color="transparent")
        list_frame.pack(fill="x", padx=20, pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(list_frame, text="Product Name", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        ctk.CTkLabel(list_frame, text="Revenue", font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="e", pady=5)

        for i, product in enumerate(products_data):
            revenue = product.get('revenue')
            revenue_str = f"${revenue:,.2f}" if revenue is not None else "$0.00"
            
            ctk.CTkLabel(list_frame, text=product['name'], font=("Arial", 12)).grid(row=i+1, column=0, sticky="w", pady=2)
            ctk.CTkLabel(list_frame, text=revenue_str, font=("Arial", 12, "bold")).grid(row=i+1, column=1, sticky="e", pady=2)

    # --- Main Content Structure ---

    def create_summary_widgets(self):
        # 1. Key Metrics Section
        metrics_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        metrics_frame.grid(row=self.row_counter, column=0, padx=10, pady=10, sticky="ew")
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.row_counter += 1
        
        sales = self.summary_data.get('total_sales', 0)
        orders = self.summary_data.get('total_orders', 0)
        
        self.create_metric_card(metrics_frame, 0, "Total Sales (30 Days)", f"${sales:,.2f}", "green")
        self.create_metric_card(metrics_frame, 1, "Total Orders (30 Days)", f"{orders:,}", "blue")
        avg_value = sales / orders if orders and sales is not None else 0
        self.create_metric_card(metrics_frame, 2, "Avg. Order Value", f"${avg_value:,.2f}", "purple")
        
        # 2. Sales Trend Chart
        chart_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        chart_frame.grid(row=self.row_counter, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.row_counter += 1
        self.create_sales_chart(chart_frame)

        # 3. Top Products Table/List
        products_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        products_frame.grid(row=self.row_counter, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.row_counter += 1
        self.create_top_products_list(products_frame)

    def create_transactions_widgets(self):
        # 4. Transaction History Section
        transactions_container = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        # We need this container to expand to fill the available space, but it's nested in a ScrollableFrame.
        # We set row weight on the main master (the Admin Dashboard Content frame) to ensure this component expands.
        transactions_container.grid(row=self.row_counter, column=0, padx=10, pady=(0, 10), sticky="nsew")
        transactions_container.grid_columnconfigure(0, weight=1)
        transactions_container.grid_rowconfigure(1, weight=1)
        self.row_counter += 1
        
        # Header and Export Button
        header_frame = ctk.CTkFrame(transactions_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header_frame, text="Transaction History", font=("Arial", 18, "bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header_frame, text="Export to CSV", command=self.export_csv, width=120, fg_color="#A9A1E0", hover_color="#8F87C4").grid(row=0, column=1, sticky="e")
        
        # Treeview (Table)
        self.tree = ttk.Treeview(transactions_container, show="headings", columns=('id', 'date', 'type', 'amount'))
        self.tree.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Style the Treeview 
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#DDDDDD", foreground="#333333")
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        style.map("Treeview", background=[('selected', '#A9A1E0')], foreground=[('selected', 'white')])

        # Define columns
        self.tree.heading('id', text='Cart ID', anchor='w')
        self.tree.heading('date', text='Date', anchor='w')
        self.tree.heading('type', text='Type', anchor='w')
        self.tree.heading('amount', text='Total Amount', anchor='e')

        # Adjust column widths
        self.tree.column('id', width=100, anchor='w', stretch=tk.NO)
        self.tree.column('date', width=180, anchor='w')
        self.tree.column('type', width=100, anchor='w', stretch=tk.NO)
        self.tree.column('amount', width=120, anchor='e')

        # Scrollbar
        vsb = ttk.Scrollbar(transactions_container, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=1, sticky='ns', pady=(0, 10))
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.populate_treeview()

    def populate_treeview(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self.data:
            amount = row.get('amount')
            amount_str = f"${amount:,.2f}" if amount is not None else "$0.00"
            
            self.tree.insert('', 'end', values=(
                row['trans_id'],
                row['trans_date'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(row['trans_date'], datetime) else str(row['trans_date']),
                row['type'],
                amount_str
            ))

    def export_csv(self):
        rows = fetch_finance_transactions(limit=99999) # Fetch a large limit for full export
        if not rows:
            messagebox.showinfo("No Data", "No transactions to export.")
            return
        
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save transactions CSV")
        if not path:
            return

        fieldnames = ['trans_id', 'trans_date', 'type', 'amount', 'payment_method', 'employee_id']
        
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                r_cleaned = {
                    'trans_id': r.get('trans_id'),
                    'trans_date': r.get('trans_date').strftime("%Y-%m-%d %H:%M:%S") if isinstance(r.get('trans_date'), datetime) else r.get('trans_date'),
                    'type': r.get('type'),
                    'amount': r.get('amount') if r.get('amount') is not None else 0.00,
                    'payment_method': r.get('payment_method'),
                    'employee_id': r.get('employee_id')
                }
                w.writerow(r_cleaned)
                
        messagebox.showinfo("Exported", f"Transactions exported to {path}")

# standalone runner for testing
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    app = ctk.CTk()
    app.title("Finance Dashboard Test")
    app.geometry("1000x700")
    
    # Simple container to hold the scrollable frame
    container = ctk.CTkFrame(app)
    container.pack(fill="both", expand=True, padx=20, pady=20)
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)
    
    finance_view = FinanceApp(container)
    finance_view.grid(row=0, column=0, sticky="nsew")
    
    app.mainloop()