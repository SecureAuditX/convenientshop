import customtkinter as ctk
import os
from PIL import Image, ImageTk
import mysql.connector
import Payment
from mysql.connector import Error
import subprocess


IMAGE_ROOT_DIR = r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop" 

# --- Database Functions ---

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="SECRET",  
        port=3306,
        database="convenient_shop" 
    )

def get_cart_items(customer_id):
    # Fetches active cart items for a customer
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

# --- Image Loaders ---

def cart_product_load_image(path, size=(50, 50)):
    # Loads and resizes product image from path
    full_path = os.path.join(IMAGE_ROOT_DIR, path.replace('/', os.sep))
    try:
        img = Image.open(full_path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None



class Checkout(ctk.CTkFrame): 
    def __init__(self, parent_frame, customer_id, email):
        # Checkout is the single main frame
        super().__init__(parent_frame, fg_color="#f8f9ff")
        self.customer_id = customer_id
        self.email = email
    
        
        # Configure grid for the Checkout frame (self)
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(0, weight=1)
        
       
        self.content_area = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.content_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Grid setup for the content area: 1 column, rows for Search/Title/Cart/Total
        self.content_area.grid_columnconfigure(0, weight=1) 
        self.content_area.grid_rowconfigure(3, weight=1) # Row 3 (cart container) expands
        
        # Search Bar (Row 0)
        self.search_bar = ctk.CTkEntry(self.content_area, placeholder_text="🔍Search",
                                      font=("Arial", 16, "bold"), fg_color="#979EEC", corner_radius=20,
                                      width=850, height=40,
                                      justify="center", text_color="#F5F5F5")
        self.search_bar.grid(padx=40, pady=40, column=0, row=0, sticky="ew")
        
        # Title "Carts" (Row 1)
        self.cats_label = ctk.CTkLabel(self.content_area, text="Carts",
                                       font=("Arial", 20, "italic", "bold"))
        self.cats_label.grid(row=1, column=0, sticky='w', padx=32, pady=5)
        
        # Cart View Container (Holds Headers and Scrollable List - Row 2)
        self.check_out_container = ctk.CTkFrame(self.content_area, fg_color="#B4BAFF", corner_radius=10)
        self.check_out_container.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.check_out_container.grid_columnconfigure(0, weight=1) 
        self.check_out_container.grid_rowconfigure(1, weight=1) 
        
        # Cart Item Headers (Inside check_out_container - Row 0)
        self.header_frame = ctk.CTkFrame(self.check_out_container, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        
        # Header Labels (using placement logic within header_frame)
        self.item_lbl=ctk.CTkLabel(self.header_frame,text="Items",font=("Arial",15,"italic","bold"))
        self.item_lbl.pack(side="left", padx=(30, 0))
        
        self.desc_lbl=ctk.CTkLabel(self.header_frame,text="Description",font=("Arial",15,"bold","italic"))
        self.desc_lbl.pack(side="left", padx=(100, 0))
        
        self.price_lbl=ctk.CTkLabel(self.header_frame,text="Price",font=("Arial",15,"italic","bold"))
        self.price_lbl.pack(side="left", padx=(100, 0))
        
        self.qty_lbl=ctk.CTkLabel(self.header_frame,text="Quantity",font=("Arial",15,"italic","bold")) 
        self.qty_lbl.pack(side="right", padx=(0, 180))
        
        self.item_total_lbl=ctk.CTkLabel(self.header_frame,text="Item Total",font=("Arial",15,"italic","bold"))
        self.item_total_lbl.pack(side="right", padx=(0, 30)) 
        
        # Scrollable Frame for Products (Inside check_out_container - Row 1)
        self.checkout_product_container = ctk.CTkScrollableFrame(self.check_out_container, fg_color="#ECEFFA")
        self.checkout_product_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.checkout_product_container.grid_columnconfigure(0, weight=1) 
        
        # Total Frame (Fixed bottom panel - Row 3)
        self.total_frame = ctk.CTkFrame(self.content_area, fg_color="#B4BAFF", corner_radius=10, height=180)
        self.total_frame.grid(row=3, column=0, padx=20, pady=(1, 20), sticky="ew")
        self.total_frame.grid_propagate(False) 
        
        # Total Frame Grid setup (2 columns for labels/values, 5 rows)
        self.total_frame.grid_columnconfigure(0, weight=1) 
        self.total_frame.grid_columnconfigure(1, weight=1) 

        # SubTotal Label (Left)
        self.sub_total_lbl = ctk.CTkLabel(self.total_frame, text="SubTotal", font=("Arial", 15, "italic", "bold"))
        self.sub_total_lbl.grid(row=0, column=0, padx=(50, 0), pady=(5, 5), sticky="w")
        
        # Shipping Fee Label (Left)
        self.shipping_lbl = ctk.CTkLabel(self.total_frame, text="Shipping Fee", font=("Arial", 15, "italic", "bold"))
        self.shipping_lbl.grid(row=1, column=0, padx=(50, 0), pady=(5, 5), sticky="w")
        
        # Total Label (Left)
        self.total_lbl = ctk.CTkLabel(self.total_frame, text="Total", font=("Arial", 15, "italic", "bold"), text_color="#975102")
        self.total_lbl.grid(row=3, column=0, padx=(50, 0), pady=(5, 5), sticky="w")
        
        # Value Labels (Right)
        self.sub_total_val = ctk.CTkLabel(self.total_frame, text="$0.00", font=("Arial", 15))
        self.sub_total_val.grid(row=0, column=1, padx=(0, 50), pady=(5, 5), sticky="e")

        self.shipping_val = ctk.CTkLabel(self.total_frame, text="$0.00", font=("Arial", 15))
        self.shipping_val.grid(row=1, column=1, padx=(0, 50), pady=(5, 5), sticky="e")

        self.total_val = ctk.CTkLabel(self.total_frame, text="$0.00",
                                       font=("Arial", 15, "bold"), text_color="#975102")
        self.total_val.grid(row=3, column=1, padx=(0, 50), pady=(5, 5), sticky="e")

        # Action Buttons (Row 4)
        self.clear_btn = ctk.CTkButton(
            self.total_frame, text="Clear Cart",
            fg_color="#FF6B6B", hover_color="#E05757",
            width=120, height=36, corner_radius=18,
            command=self.clear_cart
        )
        self.clear_btn.grid(row=4, column=0, padx=(50, 0), pady=(20, 20), sticky="w")

        self.checkout_btn = ctk.CTkButton(
            self.total_frame, text="Checkout",
            fg_color="#4169E1", hover_color="#2F54B4",
            width=120, height=36, corner_radius=18,
            command=self.open_payment
            
        )
        self.checkout_btn.grid(row=4, column=1, padx=(0, 50), pady=(20, 20), sticky="e")

        self.load_cart()
    
    
    def open_payment(self):
        """Open the Payment.py file when the checkout button is clicked"""
        print("Button clicked, proceeding to Payment...")
        
        payment_script_path = r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop\Payment.py"
        
        if os.path.exists(payment_script_path):
            print(f"Found the file at {payment_script_path}")
            subprocess.Popen(["python", payment_script_path])  # Runs the script in the background
        else:
            print(f"Error: The file {payment_script_path} does not exist.")


    
    def load_cart(self):
        # Clears and reloads all cart items from the database
        for child in self.checkout_product_container.winfo_children():
            child.destroy()
            
        rows = get_cart_items(self.customer_id)
        
        if not rows:
            # Display 'Cart is empty' message
            self.checkout_product_container.grid_rowconfigure(0, weight=1)
            self.checkout_product_container.grid_columnconfigure(0, weight=1)
            msg = ctk.CTkLabel(self.checkout_product_container, text="Your cart is empty", font=("Arial", 30), text_color="red")
            msg.grid(row=0, column=0, sticky="nsew")
            self.update_totals_from_rows([])
            return
        
        for r_index, (cart_id, product_id, name, price, qty, item_total, img_url) in enumerate(rows):
            price = float(price)
            qty = int(qty)
            item_total = float(item_total) if item_total is not None else price * qty
    
            self.checkout_product_container.grid_columnconfigure(0, weight=1)

            # Cart item row frame
            row = ctk.CTkFrame(
              self.checkout_product_container,
              fg_color="#F6F7FF",
              corner_radius=10,
              height=70
             )
            row.grid(row=r_index, column=0, sticky="ew", padx=(5, 0), pady=(0, 1))
            row.grid_columnconfigure(1, weight=1) # Name column gets weight
            row.grid_propagate(False)
            
            # Product image/icon
            img = cart_product_load_image(img_url) if img_url else None
            img_lbl = ctk.CTkLabel(row, image=img, text="") if img else ctk.CTkLabel(row, text="🛒", font=("Arial", 15))
            if img: img_lbl.image = img
            img_lbl.grid(row=0, column=0, padx=(25, 10), sticky="w")
            
            # Product name/description
            name_lbl = ctk.CTkLabel(row, text=name, font=("Arial", 13))
            # Positioned relative to image and before price/qty controls
            name_lbl.grid(row=0, column=1, sticky="w", padx=(50, 0), pady=(10, 0)) 
            
            # Price
            price_lbl = ctk.CTkLabel(row, text=f"{price:.2f}", font=("Arial", 13))
            price_lbl.grid(row=0, column=2, padx=(20, 0)) # Fixed position
            
            # Quantity controls
            qty_frame = ctk.CTkFrame(row, fg_color="#DCE2FF", corner_radius=16)
            qty_frame.grid(row=0, column=3, padx=(0, 50)) # Fixed position
            
            minus_btn = ctk.CTkButton(qty_frame, text="-", width=18, height=24,
                                       fg_color="transparent", text_color="black", hover_color="#C0C8F5",
                                       command=lambda cid=cart_id: self.change_cart_quantity(cid, -1))
            minus_btn.pack(side="left", padx=(4, 2))
            
            qty_lbl = ctk.CTkLabel(qty_frame, text=str(qty), width=24)
            qty_lbl.pack(side="left")
            
            plus_btn = ctk.CTkButton(qty_frame, text="+", width=18, height=24,
                                      fg_color="transparent", text_color="black", hover_color="#C0C8F5",
                                      command=lambda cid=cart_id: self.change_cart_quantity(cid, +1))
            plus_btn.pack(side="left", padx=(2, 4))
            
            # Item total
            item_total_lbl = ctk.CTkLabel(row, text=f"${item_total:.2f}", font=("Arial", 13))
            item_total_lbl.grid(row=0, column=4, padx=(0, 40), sticky='e') # Fixed position
        
        self.update_totals_from_rows(rows)
        
    
    def update_totals_from_rows(self, rows):
        # Calculates and updates SubTotal, Shipping, and Total labels
        subtotal = sum(float(row[5]) if row[5] is not None else float(row[3]) * int(row[4]) for row in rows)
        
        shipping = 6.10 if subtotal > 0 else 0.0
        total = subtotal + shipping
        
        self.sub_total_val.configure(text=f"${subtotal:.2f}")
        self.shipping_val.configure(text=f"${shipping:.2f}")
        self.total_val.configure(text=f"${total:.2f}")
        
    def change_cart_quantity(self, cart_id, delta):
        # Updates the quantity of an item in the database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT quantity, price FROM check_out WHERE cart_id=%s and customer_id=%s AND total IS NULL", (cart_id, self.customer_id))
            row = cursor.fetchone()
            if not row:
               cursor.close()
               conn.close()
               return
            
            qty, price = row
            new_qty = int(qty) + delta
        
            if new_qty <= 0:
               cursor.execute("DELETE FROM check_out WHERE cart_id=%s and customer_id=%s AND total IS NULL", (cart_id, self.customer_id))
            else:
                # Use SQL calculation for item_total
                cursor.execute("UPDATE check_out SET quantity=%s, item_total=price*%s WHERE cart_id=%s and customer_id=%s AND total IS NULL", (new_qty, new_qty, cart_id, self.customer_id))
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Quantity update error: {e}")
        
        self.load_cart()
        
    def clear_cart(self):
        # Deletes all active cart items for the customer
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM check_out WHERE customer_id=%s AND total IS NULL", (self.customer_id,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Clear Cart error: {e}")
        self.load_cart()
    
# --- Application Execution ---

if __name__ == "__main__":
    #app = ctk.CTk()
    #app.title("Checkout Example")
    #app.geometry("1000x800")
    
    # Create an instance of the Checkout frame
    #checkout_page = Checkout(master=app, fg_color="#F5F5F5") 
    #checkout_page.pack(expand=True, fill="both")
    
    #app.mainloop()
    pass