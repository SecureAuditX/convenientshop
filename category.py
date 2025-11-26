from db_file import Database
import customtkinter as ctk
import os
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error

# --- Configuration ---
IMAGE_ROOT_DIR = r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop" 

CARD_COLORS = [
    "#7DABDE",  # Blue
    "#87D7E0",  # Cyan
    "#EA7BBE",  # Pink
    "#BCEAA5",  # Light Green
    "#B9A5EA",  # Purple
    "#EAA5A6"   # Light Red
]

# --- Database Functions ---

def get_db_connection():
    # Establishes connection to the MySQL database
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="SECRET",  
        port=3306,
        database="convenient_shop" 
    )
    
def get_all_categories():
    # Fetches all categories and their aggregated quantity
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT category_id, category_name, quantity, image_url FROM category"
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"DB error: {e}")
        return []

def Get_products_by_category(category_id):
    # Fetches all products belonging to a specific category ID
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT product_id, product_name, price, stock_quantity, image_url FROM product WHERE category_id=%s"
        cursor.execute(query, (category_id,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"DB fetching error: {e}")
        return []

# --- Image Loaders ---

def category_load_image(path, size=(80, 80)):
    # Loads and resizes category icon image
    full_path = os.path.join(IMAGE_ROOT_DIR, path.replace('/', os.sep)) 
    try:
        img = Image.open(full_path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def product_load_image(path, size=(60, 60)):
    # Loads and resizes product image
    full_path = os.path.join(IMAGE_ROOT_DIR, path.replace('/', os.sep))
    try:
        img = Image.open(full_path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        return None


# --- Category Class ---

class Category(ctk.CTkScrollableFrame): 
    def __init__(self, parent_frame, card_colors, get_all_categories_func, category_load_image_func, get_products_by_category_func, customer_id, email, cart_update_callback):
        # Category is now a single CTkScrollableFrame
        super().__init__(parent_frame, fg_color="#f8f9ff")
        self.customer_id = customer_id
        self.email = email
        self.cart_update_callback = cart_update_callback
        
        # Configure main grid: 1 column for content alignment
        self.grid_columnconfigure(0, weight=1)
    
        # Store passed-in dependencies
        self.CARD_COLORS = card_colors
        self.get_all_categories = get_all_categories_func
        self.category_load_image = category_load_image_func
        self.Get_products_by_category = get_products_by_category_func
        
        # Search Bar (Row 0)
        self.search_bar = ctk.CTkEntry(self, placeholder_text="Search",
                                     font=("Arial", 16, "bold"), fg_color="#B4BAFF", corner_radius=27,
                                     width=850, height=40,
                                     justify="center", text_color="#F5F5F5")
        self.search_bar.grid(padx=40, pady=40, column=0, row=0, sticky="ew")
        
        # Category Title (Row 1)
        self.category_label = ctk.CTkLabel(self, text="Categories",
                                         font=("Arial", 20, "italic", "bold"))
        self.category_label.grid(row=1, column=0, sticky='w', padx=32, pady=(10, 0))
        
        # Frame to hold the large category cards (Overview mode - Row 2)
        self.overview_cards_frame = ctk.CTkFrame(self, fg_color="white")
        self.overview_cards_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        
        # Scrollable frame for horizontal category cards (Detail mode, initially hidden)
        self.horizontal_cards_container = ctk.CTkScrollableFrame(self, orientation='horizontal', fg_color="white")
        
        # Frame for displaying products (Placed in Row 3)
        self.products_container = ctk.CTkFrame(self, fg_color="White")
        self.products_container.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.products_container.grid_columnconfigure(0, weight=1) 
        
        # State variables
        self.active_category_id = None
        self.layout_mode = "overview" 
        self.category_cards = {} 
        self.horizontal_cards = {} 

        # Configure 4 equal columns for the overview cards frame
        for col in range(4):
            self.overview_cards_frame.grid_columnconfigure(col, weight=1)
        
        # Load and render initial large category cards
        categories = get_all_categories_func()
        for row_idx, (category_id, name, quantity, image_url) in enumerate(categories):
            card_color = CARD_COLORS[row_idx % len(CARD_COLORS)]
            self.make_category_card(
                parent=self.overview_cards_frame, 
                row=row_idx // 4, col=row_idx % 4,
                name=name,
                category_id=category_id,
                qty_text="Quantity ",
                qty_amount=str(quantity),
                icon_path=image_url if image_url else os.path.join("images", "default.png"), 
                bg=card_color
            ) 
        
    def make_category_card(self, parent, row, col, name, qty_text, qty_amount, icon_path, category_id, bg="#E8EEF9"):
        # Creates the large card used in the overview mode
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=30, width=190, height=200)
        card.grid(row=row, column=col, padx=20, pady=12, sticky="nw")
        card.grid_propagate(False) 
        
        for r in range(3): card.grid_rowconfigure(r, weight=1)
        card.grid_columnconfigure(0, weight=1)
        
        img = self.category_load_image(icon_path, size=(80, 80)) 
        img_lbl = ctk.CTkLabel(card, text="", image=img, fg_color=bg)
        img_lbl.image = img 
        img_lbl.grid(row=0, column=0, pady=(12, 0), sticky="n")
        
        name_lbl = ctk.CTkLabel(card, text=name, font=("Arial", 14, "bold"), justify="center")
        name_lbl.grid(row=1, column=0, pady=(6, 0), sticky="n")
        
        qty_frame = ctk.CTkFrame(card, fg_color=bg)
        qty_frame.grid(row=2, column=0, pady=(0, 10), sticky="n")
        qty_frame.grid_columnconfigure(0, weight=1)
        qty_frame.grid_columnconfigure(1, weight=1)
        
        qty_lbl = ctk.CTkLabel(qty_frame, text=qty_text, font=("Arial", 11), fg_color="transparent")
        qty_lbl.grid(row=0, column=0, padx=(0, 5), sticky="e") 
        
        qty_amount_lbl = ctk.CTkLabel(qty_frame, text=str(qty_amount), font=("Arial", 11, "bold"), fg_color="transparent")
        qty_amount_lbl.grid(row=0, column=1, padx=(5, 0), sticky="w")
        
        # Store card data for state tracking
        self.category_cards[category_id] = {
            "frame": card,
            "normal_bg": bg,
            "selected_bg": "#CFDBFD",      
            "img_label": img_lbl,
            "img_normal": img,
            "img_selected": None,  
        }
        
        # Bind click event to all child widgets
        def on_click_event(event, cid=category_id):
            self.on_category_click(cid)
            
        for widget in (card, img_lbl, name_lbl, qty_lbl, qty_amount_lbl, qty_frame):
            widget.bind("<Button-1>", on_click_event)
            widget.bind("<Enter>", lambda e, w=card: w.configure(cursor="hand2"))
            widget.bind("<Leave>", lambda e, w=card: w.configure(cursor=""))

        return card
    
    def make_horizontal_category_card(self,parent,row,col,name,qty_text,qty_amount,icon_path,category_id,bg="#E8EEF9"):
        # Creates the smaller card used in the detail mode's horizontal scrollbar
        card=ctk.CTkFrame(parent,fg_color=bg,corner_radius=30,width=130,height=170)
        card.grid(row=row,column=col,padx=20,pady=12,sticky="nw")
        card.grid_propagate(False)
        
        for r in range(3): card.grid_rowconfigure(r,weight=1)
        card.grid_columnconfigure(0,weight=1)
        
        img=category_load_image(icon_path,size=(80,80))
        img_lbl=ctk.CTkLabel(card,text="",image=img,fg_color=bg)
        img_lbl.image=img
        img_lbl.grid(row=0,column=0,pady=(12,0),sticky="n")
        
        name_lbl = ctk.CTkLabel(card, text=name, font=("Arial", 14, "bold"), justify="center")
        name_lbl.grid(row=1, column=0, pady=(6, 0), sticky="n")
        
        qty_frame = ctk.CTkFrame(card, fg_color=bg)
        qty_frame.grid(row=2,column=0,pady=(0,10),sticky="n")
        
        qty_lbl=ctk.CTkLabel(qty_frame,text=f"{qty_text}{qty_amount}",font=("Arial",11))
        qty_lbl.grid(row=0,column=0,padx=0,pady=0)
        
        # Store card data
        self.horizontal_cards[category_id] = {
            "frame": card,
            "normal_bg": bg,
            "selected_bg": "#CFDBFD",      
            "img_label": img_lbl,
            "img_normal": img,
            "img_selected": None,  
        }
        
        # Bind click event
        def on_click_event(event, cid=category_id):
            self.on_category_click(cid)
        
        for widget in (card, img_lbl, name_lbl, qty_lbl, qty_frame):
            widget.bind("<Button-1>", on_click_event)
            widget.bind("<Enter>", lambda e, w=card: w.configure(cursor="hand2"))
            widget.bind("<Leave>", lambda e, w=card: w.configure(cursor=""))

        return card
    
    def on_category_click(self, category_id):
        # Handles mode switch from overview to detail view
        if self.layout_mode=="overview":
            self.layout_mode="detail"
            # Hide large cards container (Row 2)
            self.overview_cards_frame.grid_remove()
            # Show horizontal scroll frame in place of the large cards container (Row 2)
            self.horizontal_cards_container.grid(row=2,column=0,sticky="ew",padx=20,pady=(10,0))
            
            # Populate horizontal cards if empty
            if not self.horizontal_cards:
                categories=self.get_all_categories()
                for idx,(cid,name,quantity,image_url) in enumerate(categories):
                    card_color = CARD_COLORS[idx % len(CARD_COLORS)]
                    self.make_horizontal_category_card(
                    parent=self.horizontal_cards_container,
                    row=0, col=idx,
                    name=name,
                    category_id=cid,
                    qty_text="Quantity ",
                    qty_amount=str(quantity),
                    icon_path=image_url if image_url else os.path.join("images", "default.png"), 
                    bg=card_color
                )
        
        # Update styling for selected horizontal card
        self.active_category_id=category_id
        
        for cid,info in self.horizontal_cards.items():
            card=info["frame"]
            if cid==category_id:
                card.configure(fg_color=info["selected_bg"])
                card.grid_configure(pady=(18,6)) # Raise slightly
            else:
                card.configure(fg_color=info["normal_bg"])
                card.grid_configure(pady=(12,12)) # Reset position

        # Render products in the product container (Row 3)
        self.render_products_for_category(category_id)
        
    
    def render_products_for_category(self, category_id):
        # Clears and displays new product cards based on category_id
        for child in self.products_container.winfo_children():
            child.destroy()

        products = self.Get_products_by_category(category_id)
        if not products:
            msg = ctk.CTkLabel(self.products_container, text="No product found for this category", font=("Arial", 16))
            msg.grid(row=0, column=0, padx=10, pady=10, sticky='w')
            return

        columns = 5
        for col in range(columns):
            self.products_container.grid_columnconfigure(col, weight=1)

        for index, (prod_id, name, price, stock_quantity, image_url) in enumerate(products):
            row = index // columns
            col = index % columns

            # Product card setup
            card = ctk.CTkFrame(self.products_container, fg_color="#F7F7F7", corner_radius=20, width=170, height=190)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='n')
            card.grid_propagate(False)

            # Image
            img = product_load_image(image_url, size=(60, 60)) if image_url else None
            if img:
                ctk.CTkLabel(card, image=img, text="").pack(pady=(8, 2))
            else:
                ctk.CTkLabel(card, text="🛒", font=("Arial", 20)).pack(pady=(8, 2))

            ctk.CTkLabel(card, text=name, font=("Arial", 12, "bold")).pack(pady=(2, 0))
            ctk.CTkLabel(card, text=f"${price}", font=("Arial", 14, "bold")).pack(pady=(0, 6))

            # Quantity control setup
            qty_frame = ctk.CTkFrame(card, fg_color="#DCE2FF", corner_radius=10)
            qty_frame.pack(pady=4)

            qty = 0 if stock_quantity == 0 else 1
            qty_var = ctk.IntVar(value=qty)

            minus_btn = ctk.CTkButton(qty_frame, text="-", width=24, height=24,
                                      fg_color="white", text_color="black", corner_radius=12,
                                      command=lambda qv=qty_var: self.decrease(qv))
            minus_btn.pack(side="left", padx=(4, 2))

            qty_lbl = ctk.CTkLabel(qty_frame, textvariable=qty_var, width=30)
            qty_lbl.pack(side="left")

            plus_btn = ctk.CTkButton(qty_frame, text="+", width=24, height=24,
                                      fg_color="white", text_color="black", corner_radius=12,
                                      command=lambda qv=qty_var, stock=stock_quantity: self.increase(qv, stock))
            plus_btn.pack(side="left", padx=(2, 4))

            if stock_quantity == 0:
                plus_btn.configure(state="disabled")
                minus_btn.configure(state="disabled")

            # Add to cart button
            add_btn = ctk.CTkButton(
                card,
                text="Add to Cart 🛒",
                width=80,
                height=40,
                fg_color="#A4A4EB",
                text_color="white",
                corner_radius=12,
                command=lambda pid=prod_id, n=name, p=price, qv=qty_var, s=stock_quantity, cat_id=category_id:
                self.add_to_cart(pid, n, p, qv, s, cat_id)
            )
            add_btn.pack(pady=(2, 4),padx=(2,4))
            
    def increase(self,qv, stock):
        # Increases product quantity, respecting stock limit
        current = qv.get()
        if current < stock:
            qv.set(current + 1)
        else:
            self.show_message("Insufficient stock!", "red")

    def decrease(self,qv):
        # Decreases product quantity, minimum of 1
        current = qv.get()
        if current > 1:
            qv.set(current - 1)
    
    def show_message(self,msg,color="green"):
        # Displays a temporary message popup
        popup=ctk.CTkLabel(self,text=msg,text_color=color,font=("Arial",14,"bold"))
        popup.place(relx=0.5, rely=0.05, anchor="center")
        self.after(2000,popup.destroy) 
            
    def add_to_cart(self, product_id, name, price, qty_var, stock_quantity, category_id):
        qty = qty_var.get()
        if qty <= 0 or qty > stock_quantity:
            self.show_message("Stock error or quantity is zero!", "red")
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Use the dynamically passed customer_id
            cursor.execute("""
                SELECT cart_id, quantity
                FROM check_out
                WHERE product_id = %s AND customer_id = %s AND total IS NULL
            """, (product_id, self.customer_id))

            row = cursor.fetchone()
            if row is None:
                # Insert new item
                cursor.execute("""
                    INSERT INTO check_out (product_id, customer_id, items, price, quantity, item_total) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (product_id, self.customer_id, name, price, qty, float(price) * qty))  

            else:
                # Update existing item quantity
                cart_id, current_qty = row
                new_qty = current_qty + qty
                new_total = new_qty * float(price)
                cursor.execute("""
                    UPDATE check_out
                    SET quantity = %s, item_total = %s
                    WHERE cart_id = %s AND total IS NULL
                """, (new_qty, new_total, cart_id))

            conn.commit()
            self.show_message(f"Added {qty} x {name} to cart!", "green")
            
            # After modifying the cart, update the cart item count
            if self.cart_update_callback:
                self.cart_update_callback()  # Call the callback to update the cart count
        
        except Exception as e:
            print(f"Cart Update error: {e}")
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass

    
    def update_cart_item_count(self):
        """
        Updates the number of items in the cart by checking the check_out table.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT SUM(quantity) AS total_items
                FROM check_out
                WHERE customer_id = %s AND total IS NULL
            """, (self.customer_id,))

            row = cursor.fetchone()

            total_items = row[0] if row[0] else 0  # If no items, set total_items to 0

            # Update the cart icon's label with the number of items
            self.item_count_label.configure(text=str(total_items))

        except Exception as e:
            print(f"Error updating cart item count: {e}")

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
         
             
    def load_image(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((100, 100), Image.LANCZOS) 
            return ImageTk.PhotoImage(img)
        except FileNotFoundError:
            return None  


CARD_COLORS = [
    "#7DABDE",  # Blue
    "#87D7E0",  # Cyan
    "#EA7BBE",  # Pink
    "#BCEAA5",  # Light Green
    "#B9A5EA",  # Purple
    "#EAA5A6"   # Light Red
    ]
  
    
def Get_products_by_category(category_id):
    try:
        conn=get_db_connection()
        cursor=conn.cursor()
        query="SELECT product_id,product_name,price,stock_quantity,image_url FROM product where category_id=%s"
        cursor.execute(query,(category_id,))
        results=cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"DB fetching error: {e}")
        return []
        
def get_all_categories():
    try:
        conn=get_db_connection()
        cursor=conn.cursor()
        query="SELECT category_id,category_name,quantity,image_url FROM category"
        cursor.execute(query)
        results=cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"DB error: {e}")
        return []
    

def category_load_image(path, size=(80,80)):
    # Construct the full absolute path
    full_path = os.path.join(IMAGE_ROOT_DIR, path.replace('/', os.sep)) 
    try:
        # Use the full path here
        img = Image.open(full_path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def product_load_image(path, size=(60, 60)):
    # Construct the full absolute path
    full_path = os.path.join(IMAGE_ROOT_DIR, path.replace('/', os.sep))
    try:
        # Use the full path here
        img = Image.open(full_path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Product image load error for {path}: {e}")
        return None


           
if __name__=="__main__":
#    app=Category(parent_frame, card_colors, get_all_categories_func, category_load_image_func, get_products_by_category_func, customer_id, email)
#    app.mainloop()
    pass