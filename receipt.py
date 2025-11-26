import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from db_file import db
from decimal import Decimal
from datetime import datetime

LOGO_PATH = r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop\logo.png"

BG = "#AFC0FF"
PANEL_BG = "#AFC0FF"
ACCENT = "#7380E6"
TEXT = "#111827"
MUTED = "#666666"
TOTAL_BG = "#7380E6"


class ReceiptWindow(tk.Toplevel):

    def __init__(self, order_no, customer_id):
        super().__init__()
        self.order_no = order_no
        self.customer_id = customer_id

        self.title("Receipt")
        self.configure(bg=BG)
        self.geometry("1200x900")
        self.resizable(False, False)

        container = tk.Frame(self, bg=BG, padx=20, pady=20)
        container.pack(expand=True, fill="both")

        main = tk.Frame(container, bg="#AFC0FF")
        main.pack(expand=True, fill="both")

        # ---------------- HEADER ----------------
        header = tk.Frame(main, bg="#AFC0FF")
        header.pack(fill="x", pady=(10, 0))

        # LEFT SIDE → logo + business info
        left = tk.Frame(header, bg="#AFC0FF")
        left.pack(side="left", padx=10)

        try:
            logo = Image.open(LOGO_PATH).resize((70, 70))
            self.logo_img = ImageTk.PhotoImage(logo)
            tk.Label(left, image=self.logo_img, bg="#AFC0FF").pack()
        except Exception:
            tk.Label(left, text="LOGO", bg="#AFC0FF").pack()

        tk.Label(left, text="BrightviewShop Inc.",
                 font=("Arial", 18, "bold"), bg="#AFC0FF", fg=TEXT).pack(anchor="w")
        tk.Label(left, text="1342 Nanchang",
                 font=("Arial", 11), bg="#AFC0FF", fg=MUTED).pack(anchor="w")

        # RIGHT SIDE → title + customer info
        right = tk.Frame(header, bg="#AFC0FF")
        right.pack(side="right", padx=10)

        tk.Label(right, text="Transaction Receipt",
                 font=("Arial", 14, "bold"), bg="#AFC0FF").pack(anchor="e")

        # Fetch customer + order info
        try:
            cust = db.fetchone("SELECT first_name, last_name FROM customers WHERE customer_id=%s",
                               (customer_id,))

            fname = cust.get("first_name", "") if cust else ""
            lname = cust.get("last_name", "") if cust else ""
            customer_name = f"{fname} {lname}".strip()
        except:
            customer_name = "Customer"

        # Fetch order rows
        q_order = """
            SELECT order_id, cart_id, address, quantity, time, total
            FROM order_history
            WHERE order_no=%s AND customer_id=%s
            ORDER BY order_id ASC
        """
        order_rows = db.fetchall(q_order, (order_no, customer_id)) or []

        address = ""
        date_val = ""
        cart_ids = []

        if order_rows:
            first = order_rows[0]
            address = first.get("address", "")
            time_val = first.get("time")
            date_val = time_val.strftime("%Y-%m-%d") if isinstance(time_val, datetime) else ""
            cart_ids = [row.get("cart_id") for row in order_rows]

        # Customer Info under title (RIGHT SIDE)
        tk.Label(right, text=f"Name: {customer_name}", font=("Arial", 11),
                 bg="#AFC0FF").pack(anchor="e")
        tk.Label(right, text=f"Address: {address}", font=("Arial", 11),
                 bg="#AFC0FF").pack(anchor="e")
        tk.Label(right, text=f"Order No: #{order_no}", font=("Arial", 11),
                 bg="#AFC0FF").pack(anchor="e")
        tk.Label(right, text=f"Order Date: {date_val}", font=("Arial", 11),
                 bg="#AFC0FF").pack(anchor="e")

        # ---------------- TABLE HEADER ----------------
        table_header = tk.Frame(main, bg=ACCENT, height=40)
        table_header.pack(fill="x", pady=(20, 0))

        tk.Label(table_header, text="QTY", font=("Arial", 12, "bold"),
                 bg=ACCENT, fg="white").place(x=20, y=8)
        tk.Label(table_header, text="DESCRIPTION", font=("Arial", 12, "bold"),
                 bg=ACCENT, fg="white").place(x=120, y=8)
        tk.Label(table_header, text="COST", font=("Arial", 12, "bold"),
                 bg=ACCENT, fg="white").place(x=500, y=8)
        tk.Label(table_header, text="TOTAL", font=("Arial", 12, "bold"),
                 bg=ACCENT, fg="white").place(x=650, y=8)

        # ---------------- SCROLLABLE ITEMS AREA ----------------
        items_container = tk.Frame(main, bg="#AFC0FF")
        items_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(items_container, bg="#AFC0FF", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(items_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        inner = tk.Frame(canvas, bg="#AFC0FF")
        canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # ---------------- FETCH ITEMS FROM check_out ----------------
        subtotal = Decimal("0.00")
        shipping_fee = Decimal("0.00")
        items = []

        if cart_ids:
            ph = ",".join(["%s"] * len(cart_ids))
            q = f"""
                SELECT description, price, quantity, item_total, shipping_fee
                FROM check_out
                WHERE cart_id IN ({ph})
                ORDER BY cart_id ASC
            """
            rows = db.fetchall(q, tuple(cart_ids)) or []

            for r in rows:
                desc = r.get("description") or ""
                price = Decimal(str(r.get("price") or 0))
                qty = int(r.get("quantity") or 0)
                total_item = Decimal(str(r.get("item_total") or price * qty))

                items.append((qty, desc, price, total_item))
                subtotal += total_item

                if r.get("shipping_fee") is not None:
                    shipping_fee = Decimal(str(r.get("shipping_fee") or 0))

        total_amount = subtotal + shipping_fee

        # ---------------- RENDER EACH ITEM ----------------
        
        for i, (qty, desc, price, total_item) in enumerate(items):
            ypad = 8

            # FIXED: description now displays because column expands properly
            inner.grid_columnconfigure(0, weight=0)
            inner.grid_columnconfigure(1, weight=1)
            inner.grid_columnconfigure(2, weight=0)
            inner.grid_columnconfigure(3, weight=0)

            tk.Label(inner, text=str(qty), bg="#AFC0FF", font=("Arial", 12)).grid(
                row=i, column=0, sticky="w", padx=20, pady=ypad)

            tk.Label(inner, text=desc, bg="#AFC0FF",
                    font=("Arial", 12, "italic"), anchor="w").grid(
                row=i, column=1, sticky="w", padx=20, pady=ypad)

            tk.Label(inner, text=f"${price:.2f}", bg="#AFC0FF", font=("Arial", 12)).grid(
                row=i, column=2, sticky="e", padx=60, pady=ypad)

            tk.Label(inner, text=f"${total_item:.2f}", bg="#AFC0FF",
                    font=("Arial", 12, "bold")).grid(
                row=i, column=3, sticky="e", padx=60, pady=ypad)


        # ---------------- TOTAL BOX (fixed text color ONLY) ----------------
        summary_frame = tk.Frame(main, bg="#AFC0FF")
        summary_frame.pack(fill="x", pady=(10, 10))

        total_box = tk.Frame(summary_frame, bg=TOTAL_BG, padx=10, pady=5)
        total_box.grid(row=2, column=0, columnspan=2, sticky="e", pady=(10, 10))

        # FIXED: TOTAL (USD) text is now BLACK
        tk.Label(total_box, text="TOTAL (USD)", font=("Arial", 12, "bold"),
                bg=TOTAL_BG, fg="black").pack(side="left", padx=8)

        tk.Label(total_box, text=f"${total_amount:.2f}", font=("Arial", 12, "bold"),
                bg=TOTAL_BG, fg="white").pack(side="right", padx=8)


        # ---------------- PAYMENT STATUS (fixed order) ----------------
        status = tk.Frame(main, bg="#AFC0FF")
        status.pack(fill="x")

        # FIXED: Payment Status THEN Success (correct order)
        tk.Label(status, text="Payment Status:",
                font=("Arial", 12), bg="#AFC0FF").pack(side="left", padx=(20, 5))

        tk.Label(status, text="SUCCESS",
                font=("Arial", 14, "bold"), fg="red", bg="#AFC0FF").pack(side="left")

        # Final center window
        self.update_idletasks()
        w = 900
        h = 750
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.grab_set()
        self.focus_force()
