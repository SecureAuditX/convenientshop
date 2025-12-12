from db_file import db
import customtkinter as ctk
import os
from PIL import Image, ImageTk
import mysql.connector

# --- Configuration ---
IMAGE_ROOT_DIR = r"C:\Users\Mubashra Nouman\Documents\phyton programs\ConvenientShop\convenientshop" 

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
        password="YourPasswordHere",  
        port=3306,
        database="conv_shop" 
    )
    

def get_cart_quantities_by_category(customer_id):
    """Returns total quantity in cart grouped by category."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        q = """
            SELECT 
                p.category_id,
                SUM(co.quantity) AS total_category_cart_qty
            FROM 
                check_out co
            JOIN 
                product p ON co.product_id = p.product_id
            WHERE 
                co.customer_id = %s 
                AND co.total IS NULL
            GROUP BY 
                p.category_id
        """

        cursor.execute(q, (customer_id,))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            row["category_id"]: row["total_category_cart_qty"]
            for row in results
        }

    except Exception as e:
        print(f"DB fetching error (categories cart): {e}")
        return {}





def get_cart_quantities_by_product(customer_id):
    """Returns how many of each product ID is currently in the cart."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        q = """
            SELECT 
                product_id,
                SUM(quantity) AS total_product_cart_qty
            FROM 
                check_out
            WHERE 
                customer_id = %s 
                AND total IS NULL
            GROUP BY 
                product_id
        """

        cursor.execute(q, (customer_id,))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            row["product_id"]: row["total_product_cart_qty"]
            for row in results
        }

    except Exception as e:
        print(f"DB fetching error (products cart): {e}")
        return {}


    
    
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
    if not path:
        return None

    # If database stores URL
    if path.startswith("http://") or path.startswith("https://"):
        try:
            import requests
            from io import BytesIO
            response = requests.get(path, timeout=5)
            img = Image.open(BytesIO(response.content)).resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print("Category image load error:", e)
            return None

    # Otherwise treat as local path
    full_path = os.path.join(IMAGE_ROOT_DIR, path.replace('/', os.sep))

    try:
        img = Image.open(full_path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print("Category image load error:", e)
        return None


def product_load_image(path, size=(60, 60)):
    if not path:
        return None

    # URL image: download it
    if path.startswith("http://") or path.startswith("https://"):
        try:
            import requests
            from io import BytesIO
            response = requests.get(path, timeout=5)
            img = Image.open(BytesIO(response.content)).resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print("Product image load error:", e)
            return None

    # Local file
    full_path = os.path.join(IMAGE_ROOT_DIR, path.replace('/', os.sep))

    try:
        img = Image.open(full_path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print("Product image load error:", e)
        return None




class Category(ctk.CTkScrollableFrame): 
    def __init__(self, parent_frame, card_colors, get_all_categories_func, category_load_image_func, 
                 get_products_by_category_func, customer_id, email, cart_update_callback, 
                 get_cart_quantities_by_category_func, 
                 get_cart_quantities_by_product_func,  
                 dashboard_badge_update_callback):
        super().__init__(parent_frame, fg_color="#f8f9ff")
        self.customer_id = customer_id
        self.email = email
        self.cart_update_callback = cart_update_callback
        self.dashboard_badge_update_callback = dashboard_badge_update_callback
        self.get_cart_quantities_by_product = get_cart_quantities_by_product_func
        self.get_category_quantities_func = get_cart_quantities_by_category_func 
        self.initial_category_quantities = self.get_category_quantities_func(self.customer_id)
        
        self.category_cart_qty_labels = {} 
        
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
        self.category_overview_badges = {}
        self.category_horizontal_badges = {}
        
        self.get_cart_quantities_by_category_func = get_cart_quantities_by_category_func


        # Configure 4 equal columns for the overview cards frame
        for col in range(4):
            self.overview_cards_frame.grid_columnconfigure(col, weight=1)
            
        initial_cart_quantities = self.get_cart_quantities_by_category(self.customer_id)        
        # Load and render initial large category cards
        categories = self.get_all_categories()
        for row_idx, (category_id, name, quantity, image_url) in enumerate(categories):
            cart_qty = initial_cart_quantities.get(category_id, 0) # Get current cart quantity
            card_color = self.CARD_COLORS[row_idx % len(self.CARD_COLORS)]
            self.make_category_card(
                parent=self.overview_cards_frame, 
                row=row_idx // 4, col=row_idx % 4,
                name=name,
                category_id=category_id,
                qty_text="Quantity ",
                qty_amount=str(quantity),
                cart_qty=cart_qty, # PASS CART QUANTITY
                icon_path=image_url if image_url else os.path.join("images", "default.png"), 
                bg=card_color
            )
        
    def make_category_card(self, parent, row, col, name, qty_text, qty_amount, icon_path, cart_qty, category_id, bg="#E8EEF9"):
        # Creates the large card used in the overview mode
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=30, width=190, height=200)
        card.grid(row=row, column=col, padx=20, pady=12, sticky="nw")
        card.grid_propagate(False) 
        
        for r in range(3): card.grid_rowconfigure(r, weight=1)
        card.grid_columnconfigure(0, weight=1)
        
       

        img = self.category_load_image(icon_path, size=(80, 80)) 
        img_lbl = ctk.CTkLabel(card, text="", image=img, fg_color=bg)
        
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
    
    def make_horizontal_category_card(self,parent,row,col,name,qty_text,qty_amount, cart_qty,icon_path,category_id,bg="#E8EEF9"):
        # Creates the smaller card used in the detail mode's horizontal scrollbar
        card=ctk.CTkFrame(parent,fg_color=bg,corner_radius=30,width=130,height=170)
        card.grid(row=row,column=col,padx=20,pady=12,sticky="nw")
        card.grid_propagate(False)
        
        # --- NEW: Cart Badge Implementation ---
        qty_badge = ctk.CTkLabel(
            card, 
            text=str(cart_qty),
            width=24, height=24,
            fg_color="red",
            text_color="white",
            font=("Arial", 12, "bold"),
            corner_radius=12 # Makes it a circle
        )
        qty_badge.place(relx=0.9, rely=0.1, anchor="center") 
        
        if cart_qty == 0:
            qty_badge.place_forget() 
        
        # Store the reference
        if category_id not in self.category_horizontal_badges:
            self.category_horizontal_badges[category_id] = []
        self.category_horizontal_badges[category_id].append(qty_badge)
        # --- END NEW: Cart Badge Implementation ---
        
        img=category_load_image(icon_path,size=(80,80))
        
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
        if self.layout_mode == "overview":
            self.layout_mode = "detail"

            # Hide large cards container (Row 2)
            self.overview_cards_frame.grid_remove()

            # Show horizontal scroll frame (Row 2)
            self.horizontal_cards_container.grid(
                row=2, column=0, sticky="ew", padx=20, pady=(10, 0)
            )

            # Populate horizontal cards if empty
            if not self.horizontal_cards:
                categories = self.get_all_categories()

                #  Correct way to fetch cart quantities
                cart_quantities = self.get_cart_quantities_by_category_func(self.customer_id)

                for idx, (cid, name, quantity, image_url) in enumerate(categories):

                    #  Get quantity for that category
                    cart_qty = cart_quantities.get(cid, 0)

                    card_color = CARD_COLORS[idx % len(CARD_COLORS)]

                    self.make_horizontal_category_card(
                        parent=self.horizontal_cards_container,
                        row=0,
                        col=idx,
                        name=name,
                        qty_text="Quantity ",
                        qty_amount=str(quantity),
                        cart_qty=cart_qty,  # <--- REQUIRED
                        icon_path=image_url if image_url else os.path.join("images", "default.png"),
                        category_id=cid,  # <--- REQUIRED
                        bg=card_color
                    )

        # Update styling for selected horizontal card
        self.active_category_id = category_id

        for cid, info in self.horizontal_cards.items():
            card = info["frame"]
            if cid == category_id:
                card.configure(fg_color=info["selected_bg"])
                card.grid_configure(pady=(18, 6))
            else:
                card.configure(fg_color=info["normal_bg"])
                card.grid_configure(pady=(12, 12))

        # Render products in the product container (Row 3)
        self.render_products_for_category(category_id)

        
    
    def render_products_for_category(self, category_id):
        """Display all products under a category with product-level cart badges."""
        
        self.category_cart_qty_labels.clear()
        
        # 1. Clear previous product cards
        for child in self.products_container.winfo_children():
            child.destroy()

        # 2. Fetch product list
        products = self.Get_products_by_category(category_id)
        if not products:
            msg = ctk.CTkLabel(
                self.products_container,
                text="No product found for this category",
                font=("Arial", 16)
            )
            msg.grid(row=0, column=0, padx=10, pady=10, sticky="w")
            return

        # 3. Fetch per-product active cart quantities
        product_cart_quantities = get_cart_quantities_by_product(self.customer_id)

        # 4. Configure responsive 5-column grid
        columns = 5
        for col in range(columns):
            self.products_container.grid_columnconfigure(col, weight=1)

        # 5. Build product cards
        for index, (prod_id, name, price, stock_quantity, image_url) in enumerate(products):
            row = index // columns
            col = index % columns

            # Product Card
            card = ctk.CTkFrame(
                self.products_container,
                fg_color="#F7F7F7",
                corner_radius=20,
                width=170,
                height=210
            )
            card.grid(row=row, column=col, padx=12, pady=12, sticky="n")
            card.grid_propagate(False)

            # ----------- PRODUCT BADGE (RED CIRCLE) -----------
            current_qty = product_cart_quantities.get(prod_id, 0)

            qty_badge = ctk.CTkLabel(
                card,
                text=str(current_qty),
                width=24, height=24,
                fg_color="red",
                text_color="white",
                font=("Arial", 12, "bold"),
                corner_radius=12
            )
            qty_badge.place(relx=0.88, rely=0.08, anchor="center")

            if current_qty == 0:
                qty_badge.place_forget()

            # Store badge reference for updates
            if prod_id not in self.category_cart_qty_labels:
                self.category_cart_qty_labels[prod_id] = []
            self.category_cart_qty_labels[prod_id].append(qty_badge)
            # ---------------------------------------------------

            # 7. Product Image
            img = product_load_image(image_url, size=(60, 60)) if image_url else None
            if img:
                image_label = ctk.CTkLabel(card, image=img, text="")
                image_label.image = img
                image_label.pack(pady=(10, 4))
            else:
                ctk.CTkLabel(card, text="🛒", font=("Arial", 22)).pack(pady=(10, 4))

            # 8. Product Name & Price
            ctk.CTkLabel(card, text=name, font=("Arial", 13, "bold")).pack(pady=(0, 0))
            ctk.CTkLabel(card, text=f"${price:.2f}", font=("Arial", 14, "bold")).pack(pady=(0, 6))

            # 9. Quantity Selector
            qty_frame = ctk.CTkFrame(card, fg_color="#DCE2FF", corner_radius=10)
            qty_frame.pack(pady=4)

            qty_var = ctk.IntVar(value=1 if stock_quantity > 0 else 0)

            minus_btn = ctk.CTkButton(
                qty_frame, text="-", width=24, height=24,
                fg_color="white", text_color="black",
                corner_radius=12,
                command=lambda qv=qty_var: self.decrease(qv)
            )
            minus_btn.pack(side="left", padx=(4, 2))

            qty_lbl = ctk.CTkLabel(qty_frame, textvariable=qty_var, width=30)
            qty_lbl.pack(side="left")

            plus_btn = ctk.CTkButton(
                qty_frame, text="+", width=24, height=24,
                fg_color="white", text_color="black",
                corner_radius=12,
                command=lambda qv=qty_var, stock=stock_quantity: self.increase(qv, stock)
            )
            plus_btn.pack(side="left", padx=(2, 4))

            if stock_quantity == 0:
                minus_btn.configure(state="disabled")
                plus_btn.configure(state="disabled")

            # 10. Add to Cart Button
            add_btn = ctk.CTkButton(
                card,
                text="Add to Cart 🛒",
                width=130,
                height=40,
                fg_color="#A4A4EB",
                text_color="white",
                corner_radius=12,
                command=lambda pid=prod_id, n=name, p=price, qv=qty_var, s=stock_quantity, cat_id=category_id:
                    self.add_to_cart(pid, n, p, qv, s, cat_id)
            )
            add_btn.pack(pady=(6, 10))


            
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

            # Check if already in cart
            cursor.execute("""
                SELECT cart_id, quantity
                FROM check_out
                WHERE product_id = %s AND customer_id = %s AND total IS NULL
            """, (product_id, self.customer_id))

            row = cursor.fetchone()

            if row is None:
                # Insert new row
                cursor.execute("""
                    INSERT INTO check_out (product_id, customer_id, items, price, quantity, item_total) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (product_id, self.customer_id, name, price, qty, float(price) * qty))
            else:
                # Update existing
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

            #  UPDATE CATEGORY BADGES HERE (no badge creation)
            self.update_category_badges()

            # Update top cart count
            if self.cart_update_callback:
                self.cart_update_callback()

            # Update dashboard badges
            if self.dashboard_badge_update_callback:
                self.dashboard_badge_update_callback()

        except Exception as e:
            print(f"Cart Update error: {e}")

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass

            
    
    def get_cart_quantity_for_product(self, product_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT SUM(quantity) AS total_qty
                FROM check_out
                WHERE customer_id = %s AND product_id = %s AND total IS NULL
            """, (self.customer_id, product_id))

            row = cursor.fetchone()
            return row["total_qty"] if row["total_qty"] else 0

        except Exception as e:
            print("Cart qty fetch error:", e)
            return 0

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
            
    def update_category_badges(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT product_id, SUM(quantity) AS total_qty
                FROM check_out
                WHERE customer_id = %s AND total IS NULL
                GROUP BY product_id
            """, (self.customer_id,))

            rows = cursor.fetchall()
            qty_map = {r["product_id"]: r["total_qty"] for r in rows}

            # Update all labels
            for product_id, labels in self.category_cart_qty_labels.items():
                qty = qty_map.get(product_id, 0)

                for lbl in labels:
                    if qty > 0:
                        lbl.configure(text=str(qty))
                        lbl.place(relx=0.85, rely=0.08, anchor="center")
                    else:
                        lbl.place_forget()

        except Exception as e:
            print("Badge update error:", e)

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass


            
    def get_cart_quantities_by_category(self, customer_id):
        try:
            q = """
                SELECT 
                    p.category_id, 
                    SUM(co.quantity) AS total_category_cart_qty
                FROM 
                    check_out co
                JOIN 
                    product p ON co.product_id = p.product_id
                WHERE 
                    co.customer_id = %s AND co.total IS NULL
                GROUP BY 
                    p.category_id
            """
            rows = db.fetchall(q, (customer_id,))
            
            # Convert list of dicts to a single dict {category_id: total_quantity}
            category_quantities = {r['category_id']: r['total_category_cart_qty'] for r in rows}
            return category_quantities

        except Exception as e:
            print(f"Error fetching active cart quantities by category: {e}")
            return {}

    
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