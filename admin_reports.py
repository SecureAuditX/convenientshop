import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import mysql.connector
import certifi
import csv

# ---------- DB CONFIG ----------
DB_HOST = "mysql-convenientshop-conveniencestore01.b.aivencloud.com"
DB_PORT = 24122
DB_NAME = "conv_shop_db"
DB_USER = "avnadmin"
DB_PASS = "SECRET"

def get_db_connection():
    # Use buffered=True to allow multiple queries on the same connection
    return mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME, ssl_ca=certifi.where())

def safe_query(query, params=()):
    try:
        conn = get_db_connection()
    except mysql.connector.Error as e:
        # Instead of crashing the entire app, raise a specific error or return empty
        raise ConnectionError(f"DB connection failed: {e}")
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def fetch_sales_rows():
    """Fetches mock or real sales data for the report."""
    try:
        rows = safe_query("SELECT id, month, total_sales, orders, avg_order_value FROM sales ORDER BY id ASC")
        if rows:
            return rows
    except Exception:
        pass
    # Placeholder/Mock data if DB fails or is empty
    return [
        {"id": 1, "month": "Jan", "total_sales": 12500, "orders": 300, "avg_order_value": 41.67},
        {"id": 2, "month": "Feb", "total_sales": 15000, "orders": 350, "avg_order_value": 42.86},
        {"id": 3, "month": "Mar", "total_sales": 18000, "orders": 400, "avg_order_value": 45.00},
        {"id": 4, "month": "Apr", "total_sales": 16500, "orders": 380, "avg_order_value": 43.42},
        {"id": 5, "month": "May", "total_sales": 20000, "orders": 450, "avg_order_value": 44.44},
    ]

def fetch_product_performance_rows(limit=10):
    """Fetches mock or real product performance data."""
    try:
        rows = safe_query(f"SELECT p.product_name, SUM(ci.quantity) AS total_sold, SUM(ci.quantity * ci.price) AS total_revenue FROM cart_item ci JOIN products p ON ci.product_id = p.id GROUP BY p.product_name ORDER BY total_revenue DESC LIMIT {limit}")
        if rows:
            return rows
    except Exception:
        pass
    # Placeholder/Mock data
    return [
        {"product_name": "Soda Can", "total_sold": 500, "total_revenue": 1000.00},
        {"product_name": "Chocolate Bar", "total_sold": 450, "total_revenue": 900.00},
        {"product_name": "Bag of Chips", "total_sold": 400, "total_revenue": 800.00},
        {"product_name": "Bottled Water", "total_sold": 600, "total_revenue": 600.00},
        {"product_name": "Energy Drink", "total_sold": 200, "total_revenue": 500.00},
    ]

def fetch_inventory_summary():
    """Fetches mock or real inventory summary data."""
    try:
        rows = safe_query("SELECT p.product_name, p.current_stock, p.low_stock_threshold, (p.current_stock < p.low_stock_threshold) AS is_low_stock FROM products p ORDER BY is_low_stock DESC, p.current_stock ASC LIMIT 20")
        if rows:
            return rows
    except Exception:
        pass
    # Placeholder/Mock data
    return [
        {"product_name": "Apples", "current_stock": 5, "low_stock_threshold": 10, "is_low_stock": True},
        {"product_name": "Bananas", "current_stock": 15, "low_stock_threshold": 20, "is_low_stock": False},
        {"product_name": "Oranges", "current_stock": 8, "low_stock_threshold": 10, "is_low_stock": True},
        {"product_name": "Milk (L)", "current_stock": 25, "low_stock_threshold": 10, "is_low_stock": False},
        {"product_name": "Bread Loaf", "current_stock": 9, "low_stock_threshold": 10, "is_low_stock": True},
    ]


class ReportApp(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Configure this frame's grid to host the UI elements
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Row 1 for the tabview (main content)
        
        # --- Title ---
        self.title_label = ctk.CTkLabel(self, text="Business Performance Reports", 
                                        font=("Arial", 28, "bold"), 
                                        text_color="#333333")
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")
        
        # --- Tab View (Main Content) ---
        self.tab_view = ctk.CTkTabview(self, fg_color="#FFFFFF", segmented_button_selected_color="#6A5ACD", segmented_button_selected_hover_color="#5B4FAD")
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # Tab creation
        self.sales_tab = self.tab_view.add("Sales Analysis")
        self.product_tab = self.tab_view.add("Product Performance")
        self.inventory_tab = self.tab_view.add("Inventory Health")

        # Configure tab layouts
        self.configure_sales_tab()
        self.configure_product_tab()
        self.configure_inventory_tab()
        
    def configure_sales_tab(self):
        # Sales Tab Layout: Chart on left, Table on right
        tab = self.sales_tab
        tab.grid_columnconfigure(0, weight=1) # Chart area
        tab.grid_columnconfigure(1, weight=1) # Table area
        tab.grid_rowconfigure(0, weight=1)
        
        # Chart Frame
        chart_frame = ctk.CTkFrame(tab, fg_color="transparent")
        chart_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)
        
        self.plot_sales_chart(chart_frame)
        
        # Table Frame (for Sales Data)
        table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        table_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        self.display_sales_table(table_frame)
        
        # Export Button
        export_button = ctk.CTkButton(tab, text="Export Sales Data (CSV)", command=self.export_sales_csv,
                                      fg_color="#6A5ACD", hover_color="#5B4FAD")
        export_button.grid(row=1, column=0, columnspan=2, pady=(0, 10))

    def plot_sales_chart(self, master):
        """Generates and displays a sales chart."""
        rows = fetch_sales_rows()
        if not rows:
            ctk.CTkLabel(master, text="No Sales Data Available for Chart.", text_color="#333333").grid(row=0, column=0, sticky="nsew")
            return

        months = [row['month'] for row in rows]
        sales = [row['total_sales'] for row in rows]
        orders = [row['orders'] for row in rows]

        fig, ax1 = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('white') # Set figure background

        # Plot Sales
        ax1.bar(months, sales, color='#A4A4EB', alpha=0.7, label='Total Sales (LHS)')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Total Sales ($)', color='#A4A4EB')
        ax1.tick_params(axis='y', labelcolor='#A4A4EB')
        
        # Create second axis for Orders
        ax2 = ax1.twinx()
        ax2.plot(months, orders, color='#A4A4EB', marker='o', linewidth=2, label='Orders (RHS)')
        ax2.set_ylabel('Number of Orders', color='#A4A4EB')
        ax2.tick_params(axis='y', labelcolor='#A4A4EB')
        
        plt.title('Monthly Sales and Order Trend', color='#333333')
        fig.tight_layout()

        # Embed plot into CTkinter
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        canvas.draw()

    def display_sales_table(self, master):
        """Displays sales data in a Treeview table."""
        rows = fetch_sales_rows()
        
        table = ttk.Treeview(master, columns=("ID", "Month", "Sales", "Orders", "Avg Order Value"), show="headings", style="Custom.Treeview")
        table.grid(row=0, column=0, sticky="nsew")

        # Define headings
        table.heading("ID", text="ID")
        table.heading("Month", text="Month")
        table.heading("Sales", text="Total Sales")
        table.heading("Orders", text="Orders")
        table.heading("Avg Order Value", text="AOV")

        # Define column width
        table.column("ID", width=40, anchor="center")
        table.column("Month", width=80, anchor="center")
        table.column("Sales", width=100, anchor="e")
        table.column("Orders", width=80, anchor="center")
        table.column("Avg Order Value", width=80, anchor="e")
        
        # Populate table
        for row in rows:
            table.insert("", "end", values=(
                row['id'],
                row['month'],
                f"${row['total_sales']:,.2f}",
                row['orders'],
                f"${row['avg_order_value']:,.2f}"
            ))

        # Add scrollbar
        scrollbar = ctk.CTkScrollbar(master, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def configure_product_tab(self):
        # Product Tab Layout: Table at top, Chart at bottom
        tab = self.product_tab
        tab.grid_columnconfigure(0, weight=1) 
        tab.grid_rowconfigure(0, weight=1) # Row for Table
        tab.grid_rowconfigure(1, weight=1) # Row for Chart
        
        # Table Frame
        table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        table_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        self.display_product_table(table_frame)
        
        # Chart Frame
        chart_frame = ctk.CTkFrame(tab, fg_color="transparent")
        chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)
        
        self.plot_product_chart(chart_frame)

        # Export Button
        export_button = ctk.CTkButton(tab, text="Export Product Data (CSV)", command=self.export_products_csv,
                                      fg_color="#6A5ACD", hover_color="#5B4FAD")
        export_button.grid(row=2, column=0, pady=(0, 10))

    def display_product_table(self, master):
        """Displays product performance data in a Treeview table."""
        rows = fetch_product_performance_rows(limit=10)
        
        table = ttk.Treeview(master, columns=("Name", "Sold", "Revenue"), show="headings", style="Custom.Treeview")
        table.grid(row=0, column=0, sticky="nsew")

        # Define headings
        table.heading("Name", text="Product Name")
        table.heading("Sold", text="Units Sold")
        table.heading("Revenue", text="Total Revenue")

        # Define column width
        table.column("Name", width=250, anchor="w")
        table.column("Sold", width=100, anchor="center")
        table.column("Revenue", width=150, anchor="e")
        
        # Populate table
        for row in rows:
            table.insert("", "end", values=(
                row['product_name'],
                row['total_sold'],
                f"${row['total_revenue']:,.2f}"
            ))

        # Add scrollbar
        scrollbar = ctk.CTkScrollbar(master, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def plot_product_chart(self, master):
        """Generates and displays a bar chart of product revenue."""
        rows = fetch_product_performance_rows(limit=5)
        if not rows:
            ctk.CTkLabel(master, text="No Product Data Available for Chart.", text_color="#333333").grid(row=0, column=0, sticky="nsew")
            return

        products = [row['product_name'] for row in rows]
        revenue = [row['total_revenue'] for row in rows]
        
        # Use simpler names for chart labels
        short_products = [name.split(' ')[0] for name in products]

        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor('white') 

        # Plot Revenue
        ax.bar(short_products, revenue, color='#A4A4EB')
        ax.set_ylabel('Total Revenue ($)')
        ax.set_title('Top 5 Product Revenue Contribution')
        
        plt.xticks(rotation=15, ha="right")
        fig.tight_layout()

        # Embed plot into CTkinter
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        canvas.draw()


    def configure_inventory_tab(self):
        # Inventory Tab Layout: Table
        tab = self.inventory_tab
        tab.grid_columnconfigure(0, weight=1) 
        tab.grid_rowconfigure(0, weight=1)
        
        # Table Frame
        table_frame = ctk.CTkFrame(tab, fg_color="transparent")
        table_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        self.display_inventory_table(table_frame)
        
        # Export Button
        export_button = ctk.CTkButton(tab, text="Export Inventory Data (CSV)", command=self.export_inventory_csv,
                                      fg_color="#6A5ACD", hover_color="#5B4FAD")
        export_button.grid(row=1, column=0, pady=(0, 10))

    def display_inventory_table(self, master):
        """Displays inventory summary data in a Treeview table."""
        rows = fetch_inventory_summary()
        
        table = ttk.Treeview(master, columns=("Name", "Stock", "Threshold", "Status"), show="headings", style="Custom.Treeview")
        table.grid(row=0, column=0, sticky="nsew")

        # Define headings
        table.heading("Name", text="Product Name")
        table.heading("Stock", text="Current Stock")
        table.heading("Threshold", text="Low Stock Threshold")
        table.heading("Status", text="Status")

        # Define column width
        table.column("Name", width=250, anchor="w")
        table.column("Stock", width=100, anchor="center")
        table.column("Threshold", width=150, anchor="center")
        table.column("Status", width=100, anchor="center")
        
        # Populate table and add tags for coloring
        table.tag_configure('low_stock', background='#FFCCCC', foreground='black') # Light Red
        table.tag_configure('good_stock', background='#10B981', foreground='black') # Light Green

        for row in rows:
            status = "LOW" if row['is_low_stock'] else "OK"
            tag = 'low_stock' if row['is_low_stock'] else 'good_stock'
            
            table.insert("", "end", values=(
                row['product_name'],
                row['current_stock'],
                row['low_stock_threshold'],
                status
            ), tags=(tag,))

        # Add scrollbar
        scrollbar = ctk.CTkScrollbar(master, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    # --- Export Functions ---
    def export_sales_csv(self):
        rows = fetch_sales_rows()
        if not rows:
            messagebox.showinfo("No Data", "No sales data to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save Sales CSV")
        if not path:
            return
        keys = rows[0].keys()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        messagebox.showinfo("Exported", f"Sales exported to {path}")

    def export_inventory_csv(self):
        rows = fetch_inventory_summary()
        if not rows:
            messagebox.showinfo("No Data", "No inventory to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save inventory CSV")
        if not path:
            return
        keys = rows[0].keys()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        messagebox.showinfo("Exported", f"Inventory exported to {path}")

    def export_products_csv(self):
        rows = fetch_product_performance_rows(limit=1000)
        if not rows:
            messagebox.showinfo("No Data", "No product performance to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save products CSV")
        if not path:
            return
        keys = rows[0].keys()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        messagebox.showinfo("Exported", f"Products exported to {path}")


# standalone runner for testing
if __name__ == "__main__":
    # Customizing Treeview Style for better looks
    style = ttk.Style()
    style.theme_use("default")
    # Configure the heading colors
    style.configure("Custom.Treeview.Heading", background="#D7D2F4", foreground="black", font=("Arial", 12, "bold"))
    # Configure the row colors
    style.configure("Custom.Treeview", background="#E0DDF0", foreground="black", rowheight=25, fieldbackground="#E0DDF0")
    style.map("Custom.Treeview", background=[('selected', '#B8B3D9')])
    
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    app = ctk.CTk()
    app.title("Report App Test")
    app.geometry("800x600")
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)
    
    report_ui = ReportApp(app) 
    report_ui.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    app.mainloop()