import customtkinter as ctk
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error
import os
import re
import random
from datetime import datetime


IMAGE_ROOT_DIR = r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop" 

# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="SECRET",  
        port=3306,
        database="convenient_shop" 
    )

def get_cart_items(customer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT c.cart_id,
             c.product_id,
             c.items,
             c.price,
             c.quantity,
             (c.price * c.quantity) AS item_total,
             p.image_url
        FROM check_out c
        JOIN product p ON p.product_id = c.product_id
        WHERE c.customer_id = %s
          AND c.total IS NULL 
        ORDER BY c.cart_id
          """
        cursor.execute(query, (customer_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"DB cart fetch error: {e}")
        return []

class Payment(ctk.CTkFrame):
    def __init__(self, parent_frame, customer_id, email):
        # Payment is the single main frame
        super().__init__(parent_frame, fg_color="#f8f9ff")
        self.customer_id = customer_id
        self.email = email
        
        # Configure grid for the Payment frame (self)
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(0, weight=1)
        
        # Content Area - This replaces self.main_frame and self.content_frame
        # It takes up the entire area of the Payment frame and gives the white background
        self.content_area = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.content_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Grid setup for the content area: 1 column, rows for Search/Title/Containers
        self.content_area.grid_columnconfigure(0, weight=1) 
        self.content_area.grid_columnconfigure(1, weight=1) # Empty column to push elements
        self.content_area.grid_rowconfigure(2, weight=1) # Row 2 (containers) expands

        # Search Bar (Row 0, Column 0/1)
        self.search_bar = ctk.CTkEntry(self.content_area, placeholder_text="🔍Search",
                                       font=("Arial", 16, "bold"), fg_color="#979EEC", corner_radius=20,
                                       height=40, justify="center", text_color="#F5F5F5")
        self.search_bar.grid(padx=40, pady=40, column=0, columnspan=2, row=0, sticky="ew")

        # Title "Payment Options" (Row 1)
        self.payment_label = ctk.CTkLabel(self.content_area, text="Payment Options",
                                          font=("Arial", 20, "italic", "bold"))
        self.payment_label.grid(row=1, column=0, sticky='w', padx=32, pady=(10, 0))
        
       
        
        # Add Card Container (Left - Row 2, Column 0)
        self.add_card_container = ctk.CTkFrame(self.content_area, fg_color="#F6F7FF", corner_radius=20, width=600, height=450)
        self.add_card_container.grid(row=2, column=0, sticky="nsw", padx=(30, 10), pady=(10, 10))
        self.add_card_container.grid_propagate(False)
        self.add_card_container.grid_columnconfigure(0, weight=1)
        self.add_card_container.grid_columnconfigure(1, weight=1)
        
        # Card Labels and Inputs
        self.card_lbl = ctk.CTkLabel(self.add_card_container, text="Credit/Debit Card", text_color="blue", font=("Arial", 20, "bold"))
        self.card_lbl.grid(row=0, column=0, sticky="nw", padx=(20, 10), pady=(20, 10))
        
        self.secure_lbl = ctk.CTkLabel(self.add_card_container, text="Secure transfer using your bank account", text_color="black", font=("Arial", 14, "italic", "bold"))
        self.secure_lbl.grid(row=0, column=0, sticky="nw", padx=(30, 10), pady=(50, 10))
        
        # Card Images (Loading images from the base path)
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        def load_card_image(filename):
            path = os.path.join(self.base_path, "images", filename)
            try:
                img = Image.open(path)
                return ctk.CTkImage(light_image=img, size=(50, 50))
            except FileNotFoundError:
                return None

        # UnionPay
        unionpay_img = load_card_image("unionpay.png")
        if unionpay_img:
            unionpay_lbl = ctk.CTkLabel(self.add_card_container, text="", image=unionpay_img, width=50, height=50)
            unionpay_lbl.grid(row=0, column=1, sticky="ne", padx=(20, 20), pady=(10, 10))

        # MasterCard
        mastercard_img = load_card_image("mastercard.png")
        if mastercard_img:
            mastercard_lbl = ctk.CTkLabel(self.add_card_container, image=mastercard_img, text="", width=50, height=50)
            mastercard_lbl.grid(row=0, column=1, sticky="ne", padx=(10, 80), pady=(10, 10))

        # Visa
        visa_img = load_card_image("visa.png")
        if visa_img:
            visa_lbl = ctk.CTkLabel(self.add_card_container, image=visa_img, text="", width=50, height=50)
            visa_lbl.grid(row=0, column=1, sticky="ne", padx=(10, 135), pady=(10, 10))
        
        # Name Input
        name_lbl = ctk.CTkLabel(self.add_card_container, text="Full Name", text_color="black", font=("Arial", 16))
        name_lbl.grid(row=1, column=0, sticky="nw", padx=(25, 10), pady=(10, 10))
        astrix_lbl = ctk.CTkLabel(self.add_card_container, text="*", text_color="red", font=("Arial", 17)) 
        astrix_lbl.grid(row=1, column=0, sticky="nw", padx=(95, 10), pady=(10, 10))
        self.name_input = ctk.CTkEntry(self.add_card_container, placeholder_text="(eg. Jhon Alex)", fg_color="#D6D9FF", border_color="#D6D9FF", width=250, height=40)
        self.name_input.grid(row=1, column=0, sticky="w", padx=(20, 10), pady=(40, 10))
        
        # Card Type Combo
        card_type_lbl = ctk.CTkLabel(self.add_card_container, text="Card Type", text_color="black", font=("Arial", 16))
        card_type_lbl.grid(row=1, column=1, sticky="nw", padx=(10, 25), pady=(10, 10))
        astrix_lbl = ctk.CTkLabel(self.add_card_container, text="*", text_color="red", font=("Arial", 17)) 
        astrix_lbl.grid(row=1, column=1, sticky="nw", padx=(85, 15), pady=(10, 10))
        self.card_combo = ctk.CTkComboBox(self.add_card_container, values=["Visa", "Master Card", "Union Pay"], fg_color="#D6D9FF", border_color="#D6D9FF", width=250, height=40)
        self.card_combo.grid(row=1, column=1, sticky="e", padx=(10, 20), pady=(40, 10))
        self.card_combo.set("Visa") # Capitalized for consistency

        # Card Number
        card_numbr_lbl = ctk.CTkLabel(self.add_card_container, text="Card No", text_color="black", font=("Arial", 16))
        card_numbr_lbl.grid(row=2, column=0, sticky="nw", padx=(25, 10), pady=(10, 10))
        astrix_lbl = ctk.CTkLabel(self.add_card_container, text="*", text_color="red", font=("Arial", 17)) 
        astrix_lbl.grid(row=2, column=0, sticky="nw", padx=(85, 15), pady=(10, 10))
        self.card_numbr_entry = ctk.CTkEntry(self.add_card_container, placeholder_text="(eg. 4335-6765-74300)", fg_color="#D6D9FF", border_color="#D6D9FF", width=250, height=40)
        self.card_numbr_entry.grid(row=2, column=0, sticky="w", padx=(20, 10), pady=(40, 10))
        
        # Expiry
        card_expiry_lbl = ctk.CTkLabel(self.add_card_container, text="Expiration Date", text_color="black", font=("Arial", 16))
        card_expiry_lbl.grid(row=2, column=1, sticky="nw", padx=(10, 0), pady=(10, 10))
        astrix_lbl = ctk.CTkLabel(self.add_card_container, text="*", text_color="red", font=("Arial", 17)) 
        astrix_lbl.grid(row=2, column=1, sticky="nw", padx=(120, 15), pady=(10, 10))
        self.card_expiry_entry = ctk.CTkEntry(self.add_card_container, placeholder_text="(eg. MM/YY)", fg_color="#D6D9FF", border_color="#D6D9FF", width=150, height=40)
        self.card_expiry_entry.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=(40, 10))

        # CVV
        cvv_lbl = ctk.CTkLabel(self.add_card_container, text="CVV", text_color="black", font=("Arial", 16))
        cvv_lbl.grid(row=2, column=1, sticky="ne", padx=(10, 85), pady=(10, 10))
        astrix_lbl = ctk.CTkLabel(self.add_card_container, text="*", text_color="red", font=("Arial", 17)) 
        astrix_lbl.grid(row=2, column=1, sticky="ne", padx=(10, 75), pady=(10, 10))
        self.cvv_entry = ctk.CTkEntry(self.add_card_container, placeholder_text="(eg. 342)", fg_color="#D6D9FF", border_color="#D6D9FF", width=100, height=40)
        self.cvv_entry.grid(row=2, column=1, sticky="e", padx=(10, 20), pady=(40, 10))
        
        # Address
        address_lbl = ctk.CTkLabel(self.add_card_container, text="Address", text_color="black", font=("Arial", 16))
        address_lbl.grid(row=3, column=0, sticky="nw", padx=(25, 10), pady=(10, 10))
        astrix_lbl = ctk.CTkLabel(self.add_card_container, text="*", text_color="red", font=("Arial", 17)) 
        astrix_lbl.grid(row=3, column=0, sticky="nw", padx=(85, 10), pady=(10, 10))
        self.address_entry = ctk.CTkEntry(self.add_card_container, placeholder_text="(eg. building 27, Nanchang University)", fg_color="#D6D9FF", border_color="#D6D9FF", width=300, height=40)
        self.address_entry.grid(row=3, column=0, sticky="w", padx=(20, 10), pady=(40, 10))
        
        # Email
        email_lbl = ctk.CTkLabel(self.add_card_container, text="Email", text_color="black", font=("Arial", 16))
        email_lbl.grid(row=3, column=1, sticky="nw", padx=(10, 0), pady=(10, 10))
        astrix_lbl = ctk.CTkLabel(self.add_card_container, text="*", text_color="red", font=("Arial", 17)) 
        astrix_lbl.grid(row=3, column=1, sticky="nw", padx=(50, 0), pady=(10, 10))
        self.email_entry = ctk.CTkEntry(self.add_card_container, placeholder_text="(eg. name@gmail.com)", fg_color="#D6D9FF", border_color="#D6D9FF", width=250, height=40)
        self.email_entry.grid(row=3, column=1, sticky="e", padx=(10, 20), pady=(40, 10))
        
        # Alipay/Wechat Pay Container
        self.alipay_container = ctk.CTkFrame(self.add_card_container, fg_color="#D6D9FF", height=80, corner_radius=10)
        self.alipay_container.grid(row=5, column=0, columnspan=2, sticky="ew", padx=(20, 20), pady=(60, 10))
        self.alipay_container.grid_columnconfigure(0, weight=1)
        self.alipay_container.grid_columnconfigure(1, weight=1)
        self.alipay_container.grid_propagate(False)
        
        # Scan & Pay label
        scan_lbl = ctk.CTkLabel(self.alipay_container, text="Scan & Pay", justify="center", text_color="black", font=("Arial", 20))
        scan_lbl.grid(row=0, column=0, columnspan=2, pady=(12, 10))
        
        # Alipay Button
        alipay_img = load_card_image("alipay.png")
        alipay_btn = ctk.CTkButton(self.alipay_container, text="", image=alipay_img, width=90, height=65, corner_radius=20)
        alipay_btn.grid(row=0, column=0, sticky="w", padx=(20, 20), pady=(10, 10))
        
        # WePay Button
        wepay_img = load_card_image("wepay.png")
        wepay_btn = ctk.CTkButton(self.alipay_container, text="", image=wepay_img, width=90, height=65, corner_radius=20)
        wepay_btn.grid(row=0, column=1, sticky="e", padx=(20, 20), pady=(10, 10))
        
        # Cart Bill Container (Right - Row 2, Column 1)
        self.cart_bill_container = ctk.CTkFrame(self.content_area, fg_color="#D6D9FF", corner_radius=20, width=260, height=450)
        self.cart_bill_container.grid(row=2, column=1, sticky="nse", padx=(10, 30), pady=(10, 10))
        self.cart_bill_container.grid_columnconfigure(0, weight=1)
        self.cart_bill_container.grid_columnconfigure(1, weight=1)
        self.cart_bill_container.grid_propagate(False)
        
        # Cart Bill Details
        cart_bill_lbl = ctk.CTkLabel(self.cart_bill_container, text="Cart Bill", font=("Arial", 20), text_color="black")
        cart_bill_lbl.grid(row=0, column=0, columnspan=2, pady=(20, 20))
        
        subtotal_lbl = ctk.CTkLabel(self.cart_bill_container, text="Subtotal", text_color="black", font=("Arial", 15))
        subtotal_lbl.grid(row=1, column=0, sticky="w", padx=(20, 0), pady=(5, 5))
        
        shipping_lbl = ctk.CTkLabel(self.cart_bill_container, text="Shipping fee", font=("Arial", 16), text_color="black")
        shipping_lbl.grid(row=2, column=0, sticky="w", padx=(20, 0), pady=(5, 5))
        
        total_label = ctk.CTkLabel(self.cart_bill_container, text="Total: ", text_color="#975102", font=("Arial", 15, "italic", "bold"))
        total_label.grid(row=3, column=0, sticky="w", padx=(20, 0), pady=(20, 20))
        
        # Value labels (right side)
        self.sub_total_val = ctk.CTkLabel(self.cart_bill_container, text="$0.00", font=("Arial", 15))
        self.sub_total_val.grid(row=1, column=1, padx=(0, 20), pady=(5, 5), sticky="e")

        self.shipping_val = ctk.CTkLabel(self.cart_bill_container, text="$0.00", font=("Arial", 15))
        self.shipping_val.grid(row=2, column=1, padx=(0, 20), pady=(5, 5), sticky="e")

        self.total_val = ctk.CTkLabel(self.cart_bill_container, text="$0.00",
                                      font=("Arial", 15, "bold"), text_color="#975102")
        self.total_val.grid(row=3, column=1, padx=(0, 20), pady=(20, 20), sticky="e")
        
        # Save and Pay Button
        save_pay_btn = ctk.CTkButton(self.cart_bill_container, text="Save and Pay", text_color="black", fg_color="#727AE0", font=("Arial", 18), corner_radius=20, width=80, height=37, hover_color="#9197EB", command=self.on_save_and_pay)
        save_pay_btn.grid(row=4, column=0, columnspan=2, padx=40, pady=(250, 20))

        # Initial total update
        self.update_totals()
        
    def update_totals(self):
        try:
            rows = get_cart_items(self.customer_id)
        except Exception as e:
            print(f"Error loading cart items in payment: {e}")
            rows = []
        
        subtotal = 0.0
        
        for (_, _, _, price, qty, item_total, _) in rows:
            price = float(price)
            qty = int(qty)
            
            if item_total is None:
                subtotal += price * qty
            else:
                subtotal += float(item_total)
                
        shipping = 6.10 if subtotal > 0 else 0.00
        total = subtotal + shipping
        
        self.sub_total_val.configure(text=f"${subtotal:.2f}")
        self.shipping_val.configure(text=f"${shipping:.2f}")
        self.total_val.configure(text=f"${total:.2f}") 
        
        self.current_subtotal = subtotal
        self.current_shipping = shipping
        self.current_total = total
        
    def validate_payment_form(self):
        full_name = self.name_input.get().strip()
        card_type = self.card_combo.get().strip()
        card_no_raw = self.card_numbr_entry.get().replace(" ", "").replace("-", "")
        exp_raw = self.card_expiry_entry.get().strip()
        cvv_raw = self.cvv_entry.get().strip()
        address = self.address_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not full_name or not re.match(r"^[A-Za-z\s]+$", full_name): # Added \s for spaces
            return False, "Please enter a valid full name (letters and spaces only)"
        if not card_no_raw.isdigit() or not (13 <= len(card_no_raw) <= 19):
            return False, "Please enter a valid card number (13-19 digits)."
        
        card_no_masked = "**** **** **** " + card_no_raw[-4:]
        
        if not re.match(r"^\d{2}/\d{2}$", exp_raw):
            return False, "Expiration date must be in MM/YY Format"
        
        try:
            month = int(exp_raw[:2])
            year = 2000 + int(exp_raw[3:])
        except ValueError:
            return False, "Invalid date format."

        if not (1 <= month <= 12):
            return False, "Expiration month must be between 01 and 12"
        
        now = datetime.now()
        # Check if the card has expired
        if year < now.year or (year == now.year and month < now.month):
            return False, "Card is expired"
        
        if not cvv_raw.isdigit() or len(cvv_raw) not in (3, 4):
            return False, "CVV must be 3 or 4 digits"
        
        if not address:
            return False, "Address is required"
        
        if len(address) > 255:
            return False, "Address is too long"
        
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return False, "Please enter a valid email address"
        
        # Prepare data for insertion (using the first day of the month for the date field)
        exp_date = datetime(year, month, 1)
        data = {
            "full_name": full_name,
            "card_type": card_type,
            "card_no_masked": card_no_masked,
            "exp_date": exp_date,
            "cvv_masked": "***", # Storing masked CVV
            "address": address,
            "email": email
        }
        return True, data
    
    def card_is_valid(self,card_no):
        nDigits=len(card_no)
        nSum=0
        isSecond=False
        
        for i in range(nDigits -1, -1, -1):
            d=ord(card_no[i])-ord('0')
            if(isSecond==True):
                d=d*2
                
            nSum+=d // 10
            nSum+= d % 10
            isSecond=not isSecond
        if(nSum % 10 == 0):
            return True
        else:
            return False        
        
    def detect_card_type(self,number):
        if number.startswith("4"):
            return "Visa"
        elif  number.startswith(("51", "52", "53", "54", "55")):
            return "Master Card"
        elif  number.startswith(("62", "60", "65")):
            return "Union Pay"
        else:
            return None
        
    def update_card_type(self,event=None):
        num=self.card_numbr_entry.get().replace(" ", "").replace("-", "")
        card=self.detect_card_type(num)
        if card:
            self.card_combo.set(card)
        
    def show_message(self, msg, color="red"):
        popup = ctk.CTkLabel(self, text=msg, text_color=color, font=("Arial", 14, "bold"))
        # Place the popup in the top center of the *Payment* frame (self)
        popup.place(relx=0.5, rely=0.05, anchor="center")
        self.after(2000, popup.destroy) 
        
    def on_save_and_pay(self):
        #  Validate Form
        ok, data_or_msg = self.validate_payment_form()
        if not ok:
            self.show_message(data_or_msg, "red")
            return

        data = data_or_msg

        #  Get Cart Items
        rows = get_cart_items(self.customer_id)
        if not rows:
            self.show_message("Your cart is empty.", "red")
            return

        #  Calculate Totals (redundant check, but ensures data integrity before final steps)
        subtotal = 0.0
        for (_, _, _, price, qty, item_total, _) in rows:
            price = float(price)
            qty = int(qty)
            item_total = float(item_total) if item_total is not None else price * qty
            subtotal += item_total

        shipping = 6.10 if subtotal > 0 else 0.00
        total = subtotal + shipping

        # 4. Database Transaction
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert into payment table
            cursor.execute(
                """
                INSERT INTO payment
                (customer_id, full_name, card_no, expiration_date, cvv, email, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    self.customer_id,
                    data["full_name"],
                    data["card_no_masked"],
                    data["exp_date"],
                    data["cvv_masked"],
                    data["email"],
                    "Paid",
                )
            )

            # Generate order number
            order_no = random.randint(100000, 999999)

            # Process each cart item: insert into order_history, update product stock, update category quantity
            for (cart_id, product_id, _, price, qty, item_total, _) in rows:
                price = float(price)
                qty = int(qty)
                item_total = float(item_total) if item_total is not None else price * qty

                # Insert into order_history
                cursor.execute(
                    """
                    INSERT INTO order_history
                    (order_no, cart_id, customer_id, address, quantity, delivery_status, total)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        order_no,
                        cart_id,
                        self.customer_id,
                        data["address"],
                        qty,
                        "Pending",
                        item_total,
                    )
                )

                # Update product stock
                cursor.execute(
                    """
                    UPDATE product
                    SET stock_quantity = stock_quantity - %s
                    WHERE product_id = %s
                    """,
                    (qty, product_id)
                )

                # Update category quantity
                cursor.execute(
                    "SELECT category_id FROM product WHERE product_id = %s",
                    (product_id,)
                )
                cat_row = cursor.fetchone()
                if cat_row and cat_row[0] is not None:
                    category_id = cat_row[0]
                    cursor.execute(
                        """
                        UPDATE category
                        SET quantity = quantity - %s
                        WHERE category_id = %s
                        """,
                        (qty, category_id)
                    )

            # Mark checkout items as paid by setting the total fields
            cursor.execute(
                """
                UPDATE check_out
                SET subtotal = %s,
                    shipping_fee = %s,
                    total = %s
                WHERE customer_id = %s
                  AND total IS NULL
                """,
                (subtotal, shipping, total, self.customer_id)
            )

            conn.commit()

        except Exception as e:
            if conn:
                conn.rollback()
            print("Save & Pay error:", e)
            self.show_message("Payment failed. Please try again.", "red")
            return
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        #  Final UI Update
        self.update_totals() 
        self.show_message(f"Payment successful! Order #{order_no}", "green")
        
        # --- Show Receipt After Successful Payment ---
        from receipt import ReceiptWindow
        ReceiptWindow(order_no, self.customer_id)


# The redundant load_image function from the original code is removed as it's unused.
"""
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Payment Example")
    app.geometry("1000x800")
    
    # Create an instance of the Payment frame
    payment_page = Payment(parent_frame=app, customer_id=None, email=None)
    payment_page.pack(expand=True, fill="both")
    
    app.mainloop()
"""