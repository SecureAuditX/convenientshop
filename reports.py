# reports.py
# Embeddable ReportsApp as CTkFrame with exports

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
    return mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME, ssl_ca=certifi.where())

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

def fetch_sales_rows():
    try:
        rows = safe_query("SELECT id, month, total_sales, orders, avg_order_value FROM sales ORDER BY id ASC")
        if rows:
            return rows
    except Exception:
        pass
    return [{"id":1,"month":"Jan","total_sales":4200,"orders":156,"avg_order_value":26.92}]

def fetch_inventory_rows():
    try:
        rows = safe_query("SELECT invent_id, product, current_stock, total_stock, total_sales, total_value FROM inventory ORDER BY product ASC")
        return rows or []
    except Exception:
        return []

def fetch_product_performance_rows(limit=10):
    try:
        rows = safe_query("SELECT id, product, quantity_sold, revenue, profit FROM product_performance ORDER BY revenue DESC LIMIT %s", (limit,))
        return rows or []
    except Exception:
        return []

def fetch_category_sales():
    try:
        q = """
        SELECT COALESCE(c.category_name,'Other') AS category, SUM(pp.revenue) AS sales
        FROM product_performance pp
        LEFT JOIN product p ON pp.product_id = p.product_id
        LEFT JOIN category c ON p.category_id = c.category_id
        GROUP BY c.category_name
        """
        rows = safe_query(q)
        if rows:
            total = sum(float(r["sales"] or 0) for r in rows)
            return [{"category": r["category"] or "Other", "sales": float(r["sales"] or 0), "percentage": round((float(r["sales"] or 0)/total*100) if total else 0)} for r in rows]
    except Exception:
        pass
    return []

def safe_draw(canvas):
    try:
        widget = canvas.get_tk_widget()
        if widget.winfo_exists():
            canvas.draw()
    except Exception:
        pass

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

class ReportsApp(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # header
        header = ctk.CTkFrame(self, fg_color="#F8F8F8")
        header.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Reports", font=("Helvetica",18,"bold")).grid(row=0, column=0, sticky="w", padx=10)
        ctk.CTkButton(header, text="Refresh", command=self.refresh_all, width=110).grid(row=0, column=1, sticky="e", padx=6)
        ctk.CTkButton(header, text="Export Sales", command=self.export_sales_csv, width=120).grid(row=0, column=2, sticky="e", padx=6)
        ctk.CTkButton(header, text="Export Inventory", command=self.export_inventory_csv, width=140).grid(row=0, column=3, sticky="e", padx=6)
        ctk.CTkButton(header, text="Export Products", command=self.export_products_csv, width=140).grid(row=0, column=4, sticky="e", padx=6)

        # top charts
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
        top.grid_columnconfigure(0, weight=2)
        top.grid_columnconfigure(1, weight=1)

        sales_holder = ctk.CTkFrame(top, fg_color="white", corner_radius=10)
        sales_holder.grid(row=0, column=0, sticky="nsew", padx=(0,6), pady=6)
        self.fig_sales, self.ax_sales = plt.subplots(figsize=(6,2), dpi=90)
        self.canvas_sales = FigureCanvasTkAgg(self.fig_sales, master=sales_holder)
        self.canvas_sales.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        cat_holder = ctk.CTkFrame(top, fg_color="white", corner_radius=10)
        cat_holder.grid(row=0, column=1, sticky="nsew", padx=(6,0), pady=6)
        self.fig_cat, self.ax_cat = plt.subplots(figsize=(3,2), dpi=90)
        self.canvas_cat = FigureCanvasTkAgg(self.fig_cat, master=cat_holder)
        self.canvas_cat.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # middle: tables
        middle = ctk.CTkFrame(self, fg_color="transparent")
        middle.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0,6))
        middle.grid_columnconfigure(0, weight=2)
        middle.grid_columnconfigure(1, weight=1)
        middle.grid_rowconfigure(0, weight=1)

        sales_frame = ctk.CTkFrame(middle, fg_color="white", corner_radius=10)
        sales_frame.grid(row=0, column=0, sticky="nsew", padx=(0,6), pady=6)
        self.sales_cols = ("month","total_sales","orders","avg_order_value")
        self.sales_tree = ttk.Treeview(sales_frame, columns=self.sales_cols, show="headings", height=8)
        for c in self.sales_cols:
            self.sales_tree.heading(c, text=c.replace("_"," ").title())
            self.sales_tree.column(c, width=120, anchor="center")
        self.sales_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        right_col = ctk.CTkFrame(middle, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(6,0), pady=6)
        right_col.grid_rowconfigure(1, weight=1)

        inv_frame = ctk.CTkFrame(right_col, fg_color="white", corner_radius=10)
        inv_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=(0,6))
        inv_cols = ("product","current_stock","total_stock","total_value")
        self.inv_tree = ttk.Treeview(inv_frame, columns=inv_cols, show="headings", height=6)
        for c in inv_cols:
            self.inv_tree.heading(c, text=c.replace("_"," ").title())
            self.inv_tree.column(c, width=100, anchor="center")
        self.inv_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        prod_frame = ctk.CTkFrame(right_col, fg_color="white", corner_radius=10)
        prod_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(6,0))
        prod_cols = ("product","quantity_sold","revenue","profit")
        self.prod_tree = ttk.Treeview(prod_frame, columns=prod_cols, show="headings", height=6)
        for c in prod_cols:
            self.prod_tree.heading(c, text=c.replace("_"," ").title())
            self.prod_tree.column(c, width=100, anchor="center")
        self.prod_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # bottom bar chart
        bottom = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        bottom.grid(row=3, column=0, sticky="nsew", padx=6, pady=6)
        bottom.grid_columnconfigure(0, weight=1)
        self.fig_bar, self.ax_bar = plt.subplots(figsize=(9,2.5), dpi=90)
        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, master=bottom)
        self.canvas_bar.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        # initial load
        self.refresh_all(notify=False)

    def refresh_all(self, notify=True):
        try:
            self.load_sales_chart()
            self.load_category_pie()
            self.load_sales_table()
            self.load_inventory_table()
            self.load_product_performance()
            self.load_product_bar()
            if notify:
                messagebox.showinfo("Refreshed", "Reports refreshed.")
        except ConnectionError as e:
            messagebox.showerror("DB Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_sales_chart(self):
        rows = fetch_sales_rows()
        months = [r.get("month") for r in rows]
        totals = [float(r.get("total_sales") or 0) for r in rows]
        self.ax_sales.clear()
        X = np.arange(len(months))
        self.ax_sales.plot(X, totals, marker="o")
        self.ax_sales.set_xticks(X)
        self.ax_sales.set_xticklabels(months, rotation=30, ha="right")
        self.ax_sales.set_title("Sales Over Time")
        self.fig_sales.tight_layout()
        safe_draw(self.canvas_sales)

    def load_category_pie(self):
        rows = fetch_category_sales()
        cats = [r["category"] for r in rows]
        vals = [float(r["sales"]) for r in rows]
        self.ax_cat.clear()
        if not vals:
            self.ax_cat.text(0.5,0.5,"No Data", ha="center")
        else:
            colors = ["#111111","#6b6b6b","#9ca3af","#d1d5db","#e5e7eb"][:len(vals)]
            self.ax_cat.pie(vals, labels=[f"{c} ({int((v/sum(vals))*100) if sum(vals) else 0}%)" for c,v in zip(cats,vals)], colors=colors, wedgeprops={"edgecolor":"white"})
            self.ax_cat.set_aspect("equal")
        self.fig_cat.tight_layout()
        safe_draw(self.canvas_cat)

    def load_sales_table(self):
        rows = fetch_sales_rows()
        for i in self.sales_tree.get_children():
            self.sales_tree.delete(i)
        for r in rows:
            vals = (r.get("month"), f"${float(r.get('total_sales') or 0):,.2f}", r.get("orders"), f"${float(r.get('avg_order_value') or 0):,.2f}")
            self.sales_tree.insert("", "end", values=vals)

    def load_inventory_table(self):
        rows = fetch_inventory_rows()
        for i in self.inv_tree.get_children():
            self.inv_tree.delete(i)
        for r in rows:
            vals = (r.get("product"), r.get("current_stock"), r.get("total_stock"), f"${float(r.get('total_value') or 0):,.2f}")
            self.inv_tree.insert("", "end", values=vals)

    def load_product_performance(self):
        rows = fetch_product_performance_rows(limit=10)
        for i in self.prod_tree.get_children():
            self.prod_tree.delete(i)
        for r in rows:
            vals = (r.get("product"), r.get("quantity_sold"), f"${float(r.get('revenue') or 0):,.2f}", f"${float(r.get('profit') or 0):,.2f}")
            self.prod_tree.insert("", "end", values=vals)

    def load_product_bar(self):
        rows = fetch_product_performance_rows(limit=8)
        names = [r.get("product") for r in rows]
        revenues = [float(r.get("revenue") or 0) for r in rows]
        self.ax_bar.clear()
        X = np.arange(len(names))
        self.ax_bar.bar(X, revenues)
        self.ax_bar.set_xticks(X)
        self.ax_bar.set_xticklabels(names, rotation=30, ha="right")
        self.ax_bar.set_title("Top Product Revenues")
        self.fig_bar.tight_layout()
        safe_draw(self.canvas_bar)

    # Exports
    def export_sales_csv(self):
        rows = fetch_sales_rows()
        if not rows:
            messagebox.showinfo("No Data", "No sales to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save sales CSV")
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
        rows = fetch_inventory_rows()
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

# standalone
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    root.geometry("1200x800")
    frame = ReportsApp(master=root)
    frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
    root.mainloop()
