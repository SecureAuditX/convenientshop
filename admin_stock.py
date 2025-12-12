import customtkinter as ctk
import os
import re
import datetime
from PIL import Image, ImageTk
import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="SECRET",  
        port = 3306,
        database="convenient_shop" 
    )

def image_path_join(*parts):
    """Return normalize absolute path for images"""
    candidate = os.path.join(*parts)
    if os.path.isabs(candidate):
        return os.path.normpath(candidate)
 
    candidate2 = os.path.join(IMAGE_BASE_DIR, *parts[1:]) if len(parts) > 1 else os.path.join(IMAGE_BASE_DIR, parts[0])
    if os.path.exists(candidate2):
        return os.path.normpath(candidate2)
    base = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(base, *parts))

IMAGE_BASE_DIR = r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop\images"

class Stock(ctk.CTkFrame): 
    def __init__(self, parent_frame, customer_id, email):
        super().__init__(parent_frame, fg_color="white", corner_radius=15)
        self.customer_id = customer_id
        self.email = email
    
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
                
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent",  
        bg_color="transparent", corner_radius=10)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame._parent_canvas.configure(width=1200, height=850)
        self.content_frame.pack_propagate(False)
        
        #lbl
        self.dashboard_lbl=ctk.CTkLabel(self.content_frame,text="Stock Management",font=("Arial",22,"bold"),text_color="black")
        self.dashboard_lbl.grid(row=0,padx=(20,20),pady=(20,20),sticky="w",columnspan=4)
        
        self.back_lbl=ctk.CTkLabel(self.content_frame,text="Manage your inventory and stock levels.",font=("Arial",17),text_color="grey")
        self.back_lbl.grid(row=0,padx=(30,20),pady=(80,20),sticky="w",columnspan=4)
        
        #additem btn
        self.add_item=ctk.CTkButton(self.content_frame,text="+    Add Item",fg_color="#A4A4EB",text_color="white",width=80,height=40,corner_radius=20,command=self.open_add_dialog)
        self.add_item.grid(row=0,sticky="e",padx=(20,20),pady=(20,20),columnspan=4)
        
        
        self.total_items=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=300,height=100,corner_radius=20)
        self.total_items.grid(row=2,column=0,padx=(10,10),pady=(10,10),sticky="w")
        self.total_items.grid_propagate(False)
        
        self.total_items_lbl=ctk.CTkLabel(self.total_items,text="Total items ",text_color="grey",font=("Arial",14,"bold"))
        self.total_items_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")
        # val lbl idhr ayein gye
        self.items_val=ctk.CTkLabel(self.total_items,text="$0.00",font=("Arial",15))
        self.items_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,50))
              
        self.total_stock=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=300,height=100,corner_radius=20)
        self.total_stock.grid(row=2,column=1,padx=(10,10),pady=(10,10),sticky="w")
        self.total_stock.grid_propagate(False)
        
        self.total_stock_lbl=ctk.CTkLabel(self.total_stock,text="Total Stock Value",text_color="grey",font=("Arial",14,"bold"))
        self.total_stock_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")
        # val lbl idhr ayein gye
        self.stock_val=ctk.CTkLabel(self.total_stock,text="0",font=("Arial",15))
        self.stock_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,50))
              
        self.low_stock_items=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=300,height=100,corner_radius=20)
        self.low_stock_items.grid(row=2,column=2,padx=(10,10),pady=(10,10),sticky="e")
        self.low_stock_items.grid_propagate(False)
        
        self.low_lbl=ctk.CTkLabel(self.low_stock_items,text="Low Stock Items",text_color="grey",font=("Arial",14,"bold"))
        self.low_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")
        # val lbl idhr ayein gye
        self.low_val=ctk.CTkLabel(self.low_stock_items,text="$0.00",font=("Arial",15))
        self.low_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,50))
        
        self.search_bar=ctk.CTkEntry(self.content_frame,placeholder_text="🔍Search",
                                     font=("Arial",16,"bold"),fg_color="#D4D4D4",corner_radius=20,
                                     width=620,height=40,
                                     justify="center",text_color="#F5F5F5")
        self.search_bar.grid(padx=(20,20),pady=(20,20),column=0,row=3,sticky="w",columnspan=4)
        self.search_bar.bind("<KeyRelease>", lambda e: self.refresh_table())
   
        self.card_combo=ctk.CTkComboBox(self.content_frame,values=["Drinks","Vegetables","Bread","Cereals","Snacks","Fruits","All Categories"],fg_color="white",text_color="black", border_width=2,border_color="grey",width=200,height=40)
        self.card_combo.grid(row=3,column=2,sticky="e",padx=(10,20),pady=(20,10))
        self.card_combo.set("All Categories")
        self.card_combo.configure(command=lambda choice: self.refresh_table())
        
        self.header_table(start_row=4)
        self.update_summary_cards()
        self.load_stock_table()
        #self.show_dashboard_content()

       # grid setup
        for i in range(4):
              self.content_frame.grid_columnconfigure(i, weight=1)

        
        for r in range(5):
            self.content_frame.grid_rowconfigure(r, weight=0)
            
    def load_image(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((100, 100), Image.LANCZOS) 
            return ImageTk.PhotoImage(img)
        except FileNotFoundError:
            return None  
        
    
    def update_summary_cards(self):
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM product;")
            items=cursor.fetchone()[0] or 0
            cursor.execute("SELECT SUM(quantity*price) FROM stock_management;")
            value=cursor.fetchone()[0] or 0
            cursor.execute("""
            SELECT COUNT(*)
            FROM stock_management
            WHERE quantity < minimum_quantity;
            """)
            qty=cursor.fetchone()[0] or 0
            conn.close()
            cursor.close()
            self.items_val.configure(text=str(items))
            self.stock_val.configure(text=f"${value:.2f}")
            self.low_val.configure(text=str(qty))
        except Exception as e:
            print(f"DB feteching error: {e}")
         
    def header_table(self,start_row: int):
        header=ctk.CTkFrame(
            self.content_frame,
            fg_color="#F0F0F5",
            corner_radius=10,
            height=30
        )    
        header.grid(row=start_row,
                    column=0,
                    sticky="ew",
                    padx=(5,5),
                    pady=(5,5),
                    columnspan=9,
                    )
        
       
        header.grid_columnconfigure(0, weight=2, uniform="a") 
        header.grid_columnconfigure(1, weight=3, uniform="a") 
        header.grid_columnconfigure(2, weight=2, uniform="a") 
        header.grid_columnconfigure(3, weight=2, uniform="a") 
        header.grid_columnconfigure(4, weight=2, uniform="a") 
        header.grid_columnconfigure(5, weight=2, uniform="a") 
        header.grid_columnconfigure(6, weight=2, uniform="a") 
        header.grid_columnconfigure(7, weight=3, uniform="a") 
        header.grid_columnconfigure(8, weight=2, uniform="a") 
       
        header.grid_propagate(False)
        
        labels=[
            ("Product",0),
            ("Category",1),
            ("SKU",2),
            ("Quantity",3),
            ("Price",4),
            ("Cost",5),
            ("Supplier",6),
            ("Last Restocked",7),
            ("Actions",8),
        ]
        
        for text,col in labels:
            lbl=ctk.CTkLabel(header,text=text,font=("Arial",13,"bold"))
            anchor="w" if col < 3 else "e"
            lbl.grid(row=0,column=col,padx=(10,10),pady=(5,5),sticky=anchor)
        
        
    def load_stock_table(self):
        
        search_text=self.search_bar.get().strip()
        category=self.card_combo.get()
        if search_text or category:
            rows=self.get_filtered_stock(search_text,category)
        else:
            rows = get_stock_management()

        start_row = 5   

        for r_idx, (stock_id,name, category, sku, qty, price, cost, supplier, last_restock) in enumerate(rows):
            row = ctk.CTkFrame(
            self.content_frame,
            fg_color="#F6F7FF",
            corner_radius=10,
            height=40
        )
            row.grid(row=start_row + r_idx, column=0, sticky="ew",padx=(10,10), pady=(10, 10), columnspan=9)
           
            row.grid_columnconfigure(0, weight=3, uniform="a") 
            row.grid_columnconfigure(1, weight=2, uniform="a") 
            row.grid_columnconfigure(2, weight=3, uniform="a") 
            row.grid_columnconfigure(3, weight=2, uniform="a") 
            row.grid_columnconfigure(4, weight=2, uniform="a") 
            row.grid_columnconfigure(5, weight=2, uniform="a")
            row.grid_columnconfigure(6, weight=3, uniform="a") 
            row.grid_columnconfigure(7, weight=4, uniform="a") 
            row.grid_columnconfigure(8, weight=2, uniform="a") 
        
            row.grid_propagate(False)
 
            
            name_lbl=ctk.CTkLabel(row,text=name,font=("Arial",13))
            name_lbl.grid(row=0,column=0,sticky="w",padx=(17,15),pady=(10,10))
            
            category_lbl=ctk.CTkLabel(row,text=category,font=("Arial",13),text_color="black")
            category_lbl.grid(row=0,column=1,sticky="w",padx=(5,5),pady=(10,10))
            
            sku_lbl=ctk.CTkLabel(row,text=sku,font=("Arial",13))
            sku_lbl.grid(row=0,column=2,sticky="w",padx=(17,15),pady=(10,10))
            
            qty_lbl=ctk.CTkLabel(row,text=str(qty),font=("Arial",13))
            qty_lbl.grid(row=0,column=3,sticky="e",padx=(17,15),pady=(10,10))
            
            price_lbl=ctk.CTkLabel(row,text=str(price),font=("Arial",13))
            price_lbl.grid(row=0,column=4,sticky="e",padx=(5,5),pady=(10,10))
            
            cost_lbl=ctk.CTkLabel(row,text=str(cost),font=("Arial",13))
            cost_lbl.grid(row=0,column=5,sticky="e",padx=(5,5),pady=(10,10))
            
            supplier_lbl=ctk.CTkLabel(row,text=supplier,font=("Arial",13))
            supplier_lbl.grid(row=0,column=6,sticky="e",padx=(17,15),pady=(10,10))
            
            last_restock_lbl=ctk.CTkLabel(row,text=str(last_restock),font=("Arial",13))
            last_restock_lbl.grid(row=0,column=7,sticky="e",padx=(17,15),pady=(10,10))
            
            actions_frame = ctk.CTkFrame(row, fg_color="transparent")
            actions_frame.grid(row=0, column=8, sticky="e")
            # actions_frame.grid_propagate(False)
            
            action_edit_btn = ctk.CTkButton(actions_frame, text="✏️",
                                font=("Arial", 15),
                                width=20, height=25,
                                fg_color="white",
                                text_color="black",
                                corner_radius=5,
                                command=lambda sid=stock_id: self.open_edit_dialog(sid))
            action_edit_btn.grid(row=0, column=0, padx=(5, 5))

            action_del_btn = ctk.CTkButton(actions_frame, text="🗑️",
                               font=("Arial", 15),
                               width=20, height=25,
                               fg_color="white",
                               text_color="black",
                               corner_radius=5,
                               command=lambda sid=stock_id: self.delete_stock_item(sid))
            action_del_btn.grid(row=0, column=1,padx=(0,10))
            
            
    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Stock Item")
        
        dialog.geometry("580x650") 
        dialog.transient(self) 
        dialog.grab_set()

       
        ctk.CTkLabel(dialog, text="Add New Stock Item", font=("Arial", 18, "bold")).pack(pady=(20, 0))
        ctk.CTkLabel(dialog, text="Fill in the details to add a new item to your inventory.", font=("Arial", 12)).pack(pady=(0, 15))

        
        input_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        input_frame.pack(padx=30, fill="x", expand=False)
        
        
        input_frame.grid_columnconfigure(0, weight=1, uniform="b")
        input_frame.grid_columnconfigure(1, weight=1, uniform="b")

        
        structured_fields = [
            
            {"label": "Product Name", "key": "name", "row": 0, "col": 0, "span": 1, "default": ""},
            {"label": "Category", "key": "category", "row": 0, "col": 1, "span": 1, "default": ""},
            
            {"label": "SKU", "key": "sku", "row": 1, "col": 0, "span": 1, "default": ""},
            {"label": "Supplier", "key": "supplier", "row": 1, "col": 1, "span": 1, "default": ""},
            
            {"label": "Current Quantity", "key": "qty", "row": 2, "col": 0, "span": 1, "default": "0"},
            {"label": "Minimum Quantity", "key": "min_qty", "row": 2, "col": 1, "span": 1, "default": "10"},
            
            {"label": "Selling Price", "key": "price", "row": 3, "col": 0, "span": 1, "default": "0.00"},
            {"label": "Cost Price", "key": "cost", "row": 3, "col": 1, "span": 1, "default": "0.00"},
            
            {"label": "Last Restocked (YYYY-MM-DD HH:MM:SS)", "key": "restock", "row": 4, "col": 0, "span": 2, "default": "2025-11-01 08:00:00"},
            
            {"label": "Image URL / Path", "key": "img_url", "row": 5, "col": 0, "span": 2, "default": ""},
        ]

        entries = {}
        
        for field in structured_fields:
            col_span = field["span"]
            
            
            field_group_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
            field_group_frame.grid(
                row=field["row"], 
                column=field["col"], 
                columnspan=col_span, 
                sticky="ew", 
                padx=(10, 10), 
                pady=(5, 10)
            )
            
            
            ctk.CTkLabel(field_group_frame, 
                         text=field["label"], 
                         font=("Arial", 13, "bold"), 
                         anchor="w").pack(fill="x", pady=(0, 2))
            
            
            ent = ctk.CTkEntry(field_group_frame, height=35)
            if field["default"]:
                ent.insert(0, field["default"])
                
            entries[field["key"]] = ent
            ent.pack(fill="x") 

        def save_item():
            vals = {k: v.get().strip() for k, v in entries.items()}
            
            ok, data_or_msg = self.validate_fields(dialog,vals)
            if not ok:
                self.show_message(data_or_msg, "red")
                return

            try:
                qty = int(vals["qty"])
                price = float(vals["price"])
                cost = float(vals["cost"])
                min_qty = int(vals["min_qty"]) if vals["min_qty"] else 10

                
                category_id = get_category_id(vals["category"])

                conn = get_db_connection()
                cursor = conn.cursor()

                
                cursor.execute(
                """
                INSERT INTO product
                (category_id, product_name, price, stock_quantity,
                 is_popular, is_new, sku, discount, image_url)
                VALUES (%s,%s,%s,%s, 0,0,%s,0.00,%s)
                """,
                (
                    category_id,
                    vals["name"],
                    price,
                    qty,
                    vals["sku"],
                    vals["img_url"],
                ),
                )
                product_id = cursor.lastrowid

                cursor.execute(
                """
                INSERT INTO stock_management
                (products, product_id, category, quantity, price,
                 cost, supplier, last_restocked, sku, category_id, minimum_quantity)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    vals["name"],
                    product_id,
                    vals["category"],
                    qty,
                    price,
                    cost,
                    vals["supplier"],
                    vals["restock"],
                    vals["sku"],
                    category_id,
                    min_qty,
                    ),
                    )
                conn.commit()
                cursor.close()
                conn.close()
                dialog.destroy()
                self.update_summary_cards()
                self.refresh_table()
            except Exception as e:
                print("Add Item Error:", e)

       
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        
        button_frame.pack(fill="x", pady=(10, 20), padx=30)
        button_frame.grid_columnconfigure(0, weight=1) 
        
        
        ctk.CTkButton(
            button_frame, 
            text="Cancel", 
            fg_color="black", 
            text_color="white", 
            command=dialog.destroy, 
            hover_color="black"
        ).grid(row=0, column=1, padx=(10, 10), sticky="e") 

        
        ctk.CTkButton(
            button_frame, 
            text="Add Item", 
            fg_color="#A4A4EB",
            text_color="white", 
            command=save_item
        ).grid(row=0, column=2, sticky="e")
        
    
    def open_edit_dialog(self, stock_id: int):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Stock Item")
        dialog.geometry("580x650") 
        dialog.transient(self)
        dialog.grab_set()

       
        ctk.CTkLabel(dialog, text="Edit Stock Item", font=("Arial", 18, "bold")).pack(pady=(20, 0))
        ctk.CTkLabel(dialog, text="Update the details of the selected item.", font=("Arial", 12)).pack(pady=(0, 15))

      
        input_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        input_frame.pack(padx=30, fill="x", expand=False)
        input_frame.grid_columnconfigure(0, weight=1, uniform="b")
        input_frame.grid_columnconfigure(1, weight=1, uniform="b")

     
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT s.products, s.category, s.sku, s.quantity, s.price, s.cost,
                s.supplier, s.minimum_quantity, s.last_restocked,
                p.image_url, p.product_id, s.category_id
            FROM stock_management s
            JOIN product p ON s.product_id = p.product_id
            WHERE s.stock_id = %s
            """,
            (stock_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            print("No stock row found for id", stock_id)
            return

        (name, category, sku, qty, price, cost,
        supplier, min_qty, restock, image_url, product_id, category_id) = row

        
        structured_fields = [
            {"label": "Product Name", "key": "name", "row": 0, "col": 0, "span": 1, "default": name},
            {"label": "Category", "key": "category", "row": 0, "col": 1, "span": 1, "default": category},
            {"label": "SKU", "key": "sku", "row": 1, "col": 0, "span": 1, "default": sku},
            {"label": "Quantity", "key": "qty", "row": 1, "col": 1, "span": 1, "default": str(qty)},
            {"label": "Price", "key": "price", "row": 2, "col": 0, "span": 1, "default": str(price)},
            {"label": "Cost", "key": "cost", "row": 2, "col": 1, "span": 1, "default": str(cost)},
            {"label": "Supplier", "key": "supplier", "row": 3, "col": 0, "span": 1, "default": supplier},
            {"label": "Minimum Quantity", "key": "min_qty", "row": 3, "col": 1, "span": 1, "default": str(min_qty)},
            {"label": "Last Restocked", "key": "restock", "row": 4, "col": 0, "span": 2, "default": str(restock)},
            {"label": "Image URL / Path", "key": "img_url", "row": 5, "col": 0, "span": 2, "default": image_url},
        ]

        entries = {}
        for field in structured_fields:
            col_span = field["span"]

           
            field_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
            field_frame.grid(
                row=field["row"],
                column=field["col"],
                columnspan=col_span,
                sticky="ew",
                padx=(10, 10),
                pady=(5, 10)
            )

           
            ctk.CTkLabel(field_frame, text=field["label"], font=("Arial", 13, "bold"), anchor="w").pack(fill="x", pady=(0, 2))

        
            ent = ctk.CTkEntry(field_frame, height=35)
            ent.insert(0, field["default"])
            ent.pack(fill="x")
            entries[field["key"]] = ent

       
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 20), padx=30)
        button_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(button_frame, text="Cancel", fg_color="transparent",
                    text_color="#6B7280", command=dialog.destroy, hover_color="#F3F4F6").grid(row=0, column=1, padx=(10,10), sticky="e")

        def update_item():
            vals = {k: v.get().strip() for k, v in entries.items()}

            ok, data_or_msg = self.validate_fields(dialog, vals)
            if not ok:
                self.show_message(data_or_msg, "red")
                return
            try:
                new_qty = int(vals["qty"])
                new_price = float(vals["price"])
                new_cost = float(vals["cost"])
                new_min_qty = int(vals["min_qty"])
                new_category_id = get_category_id(vals["category"])

                conn2 = get_db_connection()
                cur2 = conn2.cursor()

                cur2.execute("""
                    UPDATE product
                    SET category_id=%s,
                        product_name=%s,
                        price=%s,
                        stock_quantity=%s,
                        sku=%s,
                        image_url=%s
                    WHERE product_id=%s
                """, (new_category_id, vals["name"], new_price, new_qty, vals["sku"], vals["img_url"], product_id))

                cur2.execute("""
                    UPDATE stock_management
                    SET products=%s,
                        category=%s,
                        sku=%s,
                        quantity=%s,
                        price=%s,
                        cost=%s,
                        supplier=%s,
                        minimum_quantity=%s,
                        last_restocked=%s,
                        category_id=%s
                    WHERE stock_id=%s
                """, (vals["name"], vals["category"], vals["sku"], new_qty, new_price, new_cost,
                    vals["supplier"], new_min_qty, vals["restock"], new_category_id, stock_id))

                conn2.commit()
                cur2.close()
                conn2.close()

                dialog.destroy()
                self.update_summary_cards()
                self.refresh_table()
            except Exception as e:
                print("Update Error:", e)

        ctk.CTkButton(button_frame, text="Update Item", fg_color="#3B82F6", text_color="white", command=update_item).grid(row=0, column=2, sticky="e")


    def validate_fields(self,dialog,vals):
        required=["name","category","sku","qty","price","cost","supplier"]
        
        for field in required:
            if not vals[field]:
                return False,"cannot be empty"
        
        if not re.match(r"^[A-Za-z].*$", vals["name"]):
            return False, "Please enter a valid product name "
        
        if  len(vals['name']) > 50:
            return False, "Product name cannot be more then 50 characters "
        
        
        if not re.match(r"^[A-Z0-9]{3,8}-[0-9]{3,5}$", vals["sku"]):
            return False, "SKU format is invalid. (e.g., BRD-101 or SNACK02-23456)"
        
        if not vals["name"].strip():
            return False, "Product name cannot be blank."
        
        if vals["qty"] and not vals["qty"].isdigit():
            return False,"Quantity should be digit."
        
        if not vals["qty"].isdigit():
            return False, "Quantity should be a whole number."
        

        if int(vals['qty']) >= 1000:
            return False,"Quantity should be less then 1000"
        
        try:
            float(vals["price"])
        except:
            return False,"price must be in float"
        
        if float(vals['price'])<=0.0:
            return False,"Price cannot be zero."
        
        try:
            
            float(vals["cost"])
        except:
            return False,"cost must be in float"
        
        if float(vals['cost']) <= 0.0:
            return False,"cost cannot be zero."
        
        if vals["min_qty"] and not vals["min_qty"].isdigit():
            return False,"Minimun quantity must be a whole number."
        
        if int(vals["min_qty"])<=0 or int(vals['qty'])<=0:
            return False,"Quantity cannot be zero"
        
        if vals["min_qty"] > vals['qty']:
            return False,"Minimun quantity cannot be greater then current quantity"
        
        
        
        try:
            datetime.datetime.strptime(vals["restock"], "%Y-%m-%d %H:%M:%S")
        except:
            return False,"Date is not dating"
        
        return True, vals
    
    def show_message(self,msg,color="red"):
        popup=ctk.CTkLabel(self,text=msg,text_color=color,font=("Arial",14,"bold"))
        popup.place(relx=0.5, rely=0.05, anchor="center")
        self.after(2000,popup.destroy) 
    
    def delete_stock_item(self,stock_id:int):
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("DELETE FROM stock_management WHERE stock_id=%s",(stock_id,))
            conn.commit()
            cursor.close()
            conn.close()
            self.refresh_table()
        except Exception as e:
            print(f"Delete error: {e}")
            
    def refresh_table(self):
        for widget in self.content_frame.winfo_children():
            if isinstance(widget,ctk.CTkFrame) and widget not in (self.total_items,self.total_stock,self.low_stock_items):
                widget.destroy()
        self.header_table(start_row=4)
        self.load_stock_table()
        
    def get_filtered_stock(self,search_text,category):
        conn=get_db_connection()
        cursor=conn.cursor()
        
        query=("SELECT stock_id, products, category, sku, quantity, price, cost, supplier, last_restocked FROM stock_management WHERE 1=1 ")
        params=[]
        
        if search_text:
            query+="AND (products LIKE %s OR category LIKE %s OR sku LIKE %s)"
            params+=[f"%{search_text}%",f"%{search_text}%",f"%{search_text}%"]
        if category and category != "All Categories":
            query+=" AND category=%s"
            params+=[category]
        
        cursor.execute(query,params)
        rows=cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
                
   
def get_category_id(category_name: str) -> int:
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category_id FROM category WHERE category_name=%s",
        (category_name,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise ValueError(f"Category '{category_name}' not found in category table.")
    return row[0]

def get_stock_management():
    try:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("""
            SELECT stock_id, products, category, sku, quantity, price, cost, supplier, last_restocked
            FROM stock_management
            ORDER BY last_restocked DESC
        """)
        result=cursor.fetchall()
        conn.close()
        cursor.close()
        return result
    except Exception as e:
        print(f"DB  fetching stock error: {e}")
        return []