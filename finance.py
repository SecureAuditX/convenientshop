# finance.py
# Embeddable FinanceApp as CTkFrame. Uses .grid() only.

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

# ---------- DB CONFIG ----------
DB_HOST = "mysql-convenientshop-conveniencestore01.b.aivencloud.com"
DB_PORT = 24122
DB_NAME = "conv_shop_db"
DB_USER = "avnadmin"
DB_PASS = "AVNS_2jwXFZ6i4VHBaoWwW6u"

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME, ssl_ca=certifi.where()
    )

def safe_query(query, params=()):
    try:
        conn = get_db_connection()
    except mysql.connector.Error as e:
        raise ConnectionError(f"DB connection failed: {e}")
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

# Fetchers (same logic as before but kept compact)
def fetch_finance_transactions(limit=500):
    try:
        q = """
        SELECT cart_id AS trans_id, date AS trans_date, 'Checkout' AS type,
               IFNULL(description,'Checkout') AS category,
               IFNULL(total, item_total) AS amount,
               'Completed' AS status, customer_id, NULL AS supplier_id, NULL AS payment_method, 'check_out' AS source
        FROM check_out
        WHERE total IS NOT NULL OR item_total IS NOT NULL
        UNION ALL
        SELECT order_id AS trans_id, time AS trans_date, 'Order' AS type,
               IFNULL(delivery_status,'Order') AS category,
               IFNULL(total,0) AS amount, IFNULL(delivery_status,'Completed') AS status,
               customer_id, NULL AS supplier_id, NULL AS payment_method, 'order_history' AS source
        FROM order_history
        ORDER BY trans_date DESC
        LIMIT %s
        """
        rows = safe_query(q, (limit,))
        if rows:
            return rows
    except Exception:
        pass
    # fallback
    return [{"trans_id":1,"trans_date":datetime.now(),"type":"Sample","category":"Sale","amount":120.0,"status":"Completed","customer_id":None,"supplier_id":None,"payment_method":None,"source":"sample"}]

def fetch_monthly_sales():
    try:
        rows = safe_query("SELECT month, total_sales, orders, avg_order_value FROM sales ORDER BY id ASC")
        if rows:
            return rows
        rows = safe_query("""SELECT DATE_FORMAT(time,'%%b %%Y') AS month, COALESCE(SUM(total),0) AS total_sales,
                             COUNT(*) AS orders, CASE WHEN COUNT(*)=0 THEN 0 ELSE ROUND(SUM(total)/COUNT(*),2) END AS avg_order_value
                             FROM order_history GROUP BY DATE_FORMAT(time,'%%Y-%%m') ORDER BY MIN(time) ASC""")
        return rows
    except Exception:
        return [{"month":"Jan","total_sales":4200,"orders":156,"avg_order_value":26.92}]

def fetch_product_performance(limit=8):
    try:
        rows = safe_query("SELECT product_id, product, quantity_sold, revenue, profit FROM product_performance ORDER BY revenue DESC LIMIT %s", (limit,))
        if rows:
            return rows
    except Exception:
        pass
    return [{"product":"Sample A","quantity_sold":50,"revenue":1200.0,"profit":300.0}]

def fetch_inventory_summary():
    try:
        rows = safe_query("SELECT invent_id, product, current_stock, total_stock, total_sales, total_value FROM inventory ORDER BY product ASC")
        return rows or []
    except Exception:
        return []

# safe draw helper
def safe_draw(canvas):
    try:
        widget = canvas.get_tk_widget()
        if widget.winfo_exists():
            canvas.draw()
    except Exception:
        pass

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

class FinanceApp(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        # grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # header
        header = ctk.CTkFrame(self, fg_color="#F8F8F8")
        header.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Finance", font=("Helvetica", 16, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=6)

        # Export + refresh buttons
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e", padx=8)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.refresh_all, width=90).grid(row=0, column=0, padx=6)
        ctk.CTkButton(btn_frame, text="Export Transactions", command=self.export_transactions_csv, width=160).grid(row=0, column=1, padx=6)
        ctk.CTkButton(btn_frame, text="Export Inventory", command=self.export_inventory_csv, width=140).grid(row=0, column=2, padx=6)

        # charts row
        charts = ctk.CTkFrame(self, fg_color="transparent")
        charts.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
        charts.grid_columnconfigure(0, weight=1)
        charts.grid_columnconfigure(1, weight=1)

        # sales chart holder
        sales_holder = ctk.CTkFrame(charts, fg_color="white", corner_radius=10)
        sales_holder.grid(row=0, column=0, sticky="nsew", padx=(0,6), pady=6)
        sales_holder.grid_columnconfigure(0, weight=1)
        self.fig_sales, self.ax_sales = plt.subplots(figsize=(5,2), dpi=90)
        self.canvas_sales = FigureCanvasTkAgg(self.fig_sales, master=sales_holder)
        self.canvas_sales.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # top products holder
        prod_holder = ctk.CTkFrame(charts, fg_color="white", corner_radius=10)
        prod_holder.grid(row=0, column=1, sticky="nsew", padx=(6,0), pady=6)
        prod_holder.grid_columnconfigure(0, weight=1)
        self.fig_prod, self.ax_prod = plt.subplots(figsize=(5,2), dpi=90)
        self.canvas_prod = FigureCanvasTkAgg(self.fig_prod, master=prod_holder)
        self.canvas_prod.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # bottom row: transactions + inventory
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=6, pady=6)
        bottom.grid_columnconfigure(0, weight=3)
        bottom.grid_columnconfigure(1, weight=1)

        tx_frame = ctk.CTkFrame(bottom, fg_color="white", corner_radius=10)
        tx_frame.grid(row=0, column=0, sticky="nsew", padx=(0,6), pady=6)
        tx_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(tx_frame, text="Recent Transactions", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(8,0))
        cols = ("trans_id","trans_date","type","category","amount","status","customer_id","supplier_id","payment_method","source")
        self.tx_tree = ttk.Treeview(tx_frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.tx_tree.heading(c, text=c)
            self.tx_tree.column(c, width=110 if c=="amount" else 95, anchor="center")
        self.tx_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=8)

        inv_frame = ctk.CTkFrame(bottom, fg_color="white", corner_radius=10)
        inv_frame.grid(row=0, column=1, sticky="nsew", padx=(6,0), pady=6)
        ctk.CTkLabel(inv_frame, text="Inventory Summary", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(8,0))
        inv_cols = ("invent_id","product","current_stock","total_stock","total_sales","total_value")
        self.inv_tree = ttk.Treeview(inv_frame, columns=inv_cols, show="headings", height=12)
        for c in inv_cols:
            self.inv_tree.heading(c, text=c)
            self.inv_tree.column(c, width=100, anchor="center")
        self.inv_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=8)

        # initial load
        self.refresh_all(notify=False)

    def refresh_all(self, notify=True):
        try:
            self.load_monthly_sales_chart()
            self.load_top_products_chart()
            self.load_transactions_table()
            self.load_inventory_table()
            if notify:
                messagebox.showinfo("Refreshed", "Finance refreshed.")
        except ConnectionError as e:
            messagebox.showerror("DB Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_monthly_sales_chart(self):
        rows = fetch_monthly_sales()
        months = [r.get("month") for r in rows]
        totals = [float(r.get("total_sales") or 0) for r in rows]
        self.ax_sales.clear()
        X = np.arange(len(months))
        self.ax_sales.bar(X, totals)
        self.ax_sales.set_xticks(X)
        self.ax_sales.set_xticklabels(months, rotation=30, ha="right")
        self.ax_sales.set_title("Sales by Month")
        self.fig_sales.tight_layout()
        safe_draw(self.canvas_sales)

    def load_top_products_chart(self):
        rows = fetch_product_performance(limit=8)
        names = [r.get("product") for r in rows]
        revenues = [float(r.get("revenue") or 0) for r in rows]
        self.ax_prod.clear()
        X = np.arange(len(names))
        self.ax_prod.bar(X, revenues)
        self.ax_prod.set_xticks(X)
        self.ax_prod.set_xticklabels(names, rotation=30, ha="right")
        self.ax_prod.set_title("Top Product Revenues")
        self.fig_prod.tight_layout()
        safe_draw(self.canvas_prod)

    def load_transactions_table(self):
        rows = fetch_finance_transactions(limit=500)
        for r in self.tx_tree.get_children():
            self.tx_tree.delete(r)
        for r in rows:
            td = r.get("trans_date")
            td_str = td.strftime("%Y-%m-%d %H:%M:%S") if isinstance(td, datetime) else str(td)
            vals = (r.get("trans_id"), td_str, r.get("type"), r.get("category"), float(r.get("amount") or 0), r.get("status"),
                    r.get("customer_id"), r.get("supplier_id"), r.get("payment_method"), r.get("source"))
            self.tx_tree.insert("", "end", values=vals)

    def load_inventory_table(self):
        rows = fetch_inventory_summary()
        for r in self.inv_tree.get_children():
            self.inv_tree.delete(r)
        for r in rows:
            vals = (r.get("invent_id"), r.get("product"), r.get("current_stock"), r.get("total_stock"), r.get("total_sales"), float(r.get("total_value") or 0))
            self.inv_tree.insert("", "end", values=vals)

    # Export helpers
    def export_transactions_csv(self):
        rows = fetch_finance_transactions(limit=10000)
        if not rows:
            messagebox.showinfo("No Data", "No transactions to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save transactions CSV")
        if not path:
            return
        keys = rows[0].keys()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                r2 = {k:(v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v) for k,v in r.items()}
                w.writerow(r2)
        messagebox.showinfo("Exported", f"Transactions exported to {path}")

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

# standalone runner for testing
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    root.geometry("1100x700")
    root.grid_columnconfigure(0, weight=1)
    frame = FinanceApp(master=root)
    frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    root.mainloop()
