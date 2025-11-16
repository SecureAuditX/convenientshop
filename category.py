import customtkinter as ctk
import os
from PIL import Image,ImageTk
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    return mysql.connector.connect(
        host="mysql-convenientshop-conveniencestore01.b.aivencloud.com",
        user="avnadmin",  
        password="SECRET_HERE",  
        port = 24122,
        database="conv_shop_db" 
    )

    
def test_db_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Test query to see all categories
        cursor.execute("SELECT * FROM category")
        results = cursor.fetchall()
        print("Available categories:", results)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Connection error: {e}")



class Category(ctk.CTk): 
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Category")
        self.geometry("1200x800")
        self.resizable(False, False)
        ctk.set_appearance_mode("system")
        
        # main frame
        self.main_frame=ctk.CTkFrame(self,fg_color="#F5F5F5",corner_radius=10)
        self.main_frame.pack(expand=True,fill="both",pady=10,padx=10)
        
        # Left Sidebar
        self.sidebar_frame = ctk.CTkFrame(self.main_frame, width=250, fg_color="#B4C9F9", corner_radius=10)
        self.sidebar_frame.pack(side="left", fill="y", padx=(10, 0))
        
          # Sidebar Images 
        self.dashboard_image = self.load_image("images/home.png")  
        self.categories_image = self.load_image("images/category.png")  
        self.checkout_image = self.load_image("images/checkout.png") 
        self.payment_image = self.load_image("images/payment.png")  
        self.history_image = self.load_image("images/history.png")  
        self.settings_image = self.load_image("images/settings.png") 
        self.logout_image = self.load_image("images/logout.png")  

          # Sidebar Buttons 
        self.dashboard_button = ctk.CTkButton(self.sidebar_frame, image=self.dashboard_image, text="Dashboard", width=200, height=40, font=("Arial", 16), fg_color="#A4A4EB", hover_color="#7777CA", compound="left")
        self.dashboard_button.pack(padx=10, pady=(10, 15), fill="x")

        self.categories_button = ctk.CTkButton(self.sidebar_frame, image=self.categories_image, text="Categories", command=self.show_categories, width=200, height=40, font=("Arial", 16), fg_color="#A4A4EB", hover_color="#7777CA", compound="left")
        self.categories_button.pack(padx=10, pady=10, fill="x")

        self.checkout_button = ctk.CTkButton(self.sidebar_frame, image=self.checkout_image, text="Checkout", command=self.show_checkout, width=200, height=40, font=("Arial", 16), fg_color="#A4A4EB", hover_color="#7777CA", compound="left")
        self.checkout_button.pack(padx=10, pady=10, fill="x")

        self.payment_button = ctk.CTkButton(self.sidebar_frame, image=self.payment_image, text="Payment", command=self.show_payment, width=200, height=40, font=("Arial", 16), fg_color="#A4A4EB", hover_color="#7777CA", compound="left")
        self.payment_button.pack(padx=10, pady=10, fill="x")

        self.history_button = ctk.CTkButton(self.sidebar_frame, image=self.history_image, text="History", command=self.show_history, width=200, height=40, font=("Arial", 16), fg_color="#A4A4EB", hover_color="#7777CA", compound="left")
        self.history_button.pack(padx=10, pady=10, fill="x")

        self.settings_button = ctk.CTkButton(self.sidebar_frame, image=self.settings_image, text="Settings", command=self.show_settings, width=200, height=40, font=("Arial", 16), fg_color="#A4A4EB", hover_color="#7777CA", compound="left")
        self.settings_button.pack(padx=10, pady=10, fill="x")

        
          # Exit Button 
        self.logout_button = ctk.CTkButton(self.sidebar_frame, image=self.logout_image, text="Logout", command=self.logout, width=200, height=40, font=("Arial", 16), fg_color="#A4A4EB", hover_color="#7777CA", compound="left")
        self.logout_button.pack(side="bottom", padx=10, pady=15, fill="x")
        
                #<category start from here>
        
        # content_frame
        self.content_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="white", corner_radius=10)
        self.content_frame.pack(side="right", expand=True, fill="both", padx=20, pady=20,)
       
       # grid setup
        self.content_frame.grid_columnconfigure(0,weight=1)  
        self.content_frame.grid_rowconfigure(3,weight=1)   
         
        #search bar
        self.search_bar=ctk.CTkEntry(self.content_frame,placeholder_text="🔍Search",
                                     font=("Arial",16,"bold"),fg_color="#979EEC",corner_radius=20,
                                     width=850,height=40,
                                     justify="center",text_color="#F5F5F5")
        self.search_bar.grid(padx=40,pady=40,column=0,row=0,sticky="ew")
        
        # title category
        self.category_label=ctk.CTkLabel(self.content_frame,text="Categories",
                                        font=("Arial",20,"italic","bold"))
        self.category_label.grid(row=1,column=0,sticky='w',padx=32,pady=(10,0))
        
        # meowww
        self.horizontal_cards_container=ctk.CTkScrollableFrame(self.content_frame,orientation='horizontal',fg_color="white")
        self.horizontal_cards_container.grid(row=2, column=0, sticky="ew", padx=20, pady=(10,0))
    
        
        # category cards container
        self.cards_container=ctk.CTkFrame(self.content_frame,fg_color="white")
        self.cards_container.grid(row=2,column=0,sticky="nsew",padx=20,pady=20)
        
        # frame for active category card
        self.active_category_id=None
        
        # frame for products
        self.products_container=ctk.CTkFrame(self.content_frame,fg_color="White")
        self.products_container.grid(row=3,column=0,sticky="nsew",padx=20,pady=(0,20))
        self.content_frame.grid_rowconfigure(3,weight=1)
        # store cards
        self.category_cards={}
        self.horizontal_cards={}
        #layout 
        
        self.layout_mode="overview"
        
        # 4 equal columns for cards
        for col in range(4):
            self.cards_container.grid_columnconfigure(col,weight=1)
        
       
  
        # categories
        categories=get_all_categories()
        for row,(category_id,name,quantity,image_url) in enumerate(categories):
            card_color = CARD_COLORS[row % len(CARD_COLORS)]
            self.make_category_card(
            parent=self.cards_container,
            row=row //4, col=row % 4,
            name=name,
            category_id=category_id,
            qty_text="Quantity ",
            qty_amount=str(quantity),
            icon_path=image_url if image_url else os.path.join("images", "default.png"),  
           bg= card_color
        )  
       
        
    def make_category_card(self,parent,row,col,name,qty_text,qty_amount,icon_path,category_id,bg="#E8EEF9"):
        card=ctk.CTkFrame(parent,fg_color=bg,corner_radius=30,width=190,height=200)
       
        card.grid(row=row,column=col,padx=20,pady=12,sticky="nw")
        
        #stop size form strech
        card.pack_propagate(False)
        card.grid_propagate(False)
        
        #grid inside the card
        for r in range(3):
            card.grid_rowconfigure(r,weight=1)
        card.grid_columnconfigure(0,weight=1)
        
        #image
        img=category_load_image(icon_path,size=(80,80))
        img_lbl=ctk.CTkLabel(card,text="",image=img,fg_color=bg)
        img_lbl.image=img
        img_lbl.grid(row=0,column=0,pady=(12,0),sticky="n")
        
        #name
        name_lbl = ctk.CTkLabel(card, text=name, font=("Arial", 14, "bold"), justify="center")
        name_lbl.grid(row=1, column=0, pady=(6, 0), sticky="n")
        
        #quantity
        qty_lbl=ctk.CTkLabel(card,text=qty_text,font=("Arial",11))
        qty_lbl.grid(row=2,column=0,pady=10,padx=0,sticky="n")
        
        # quantity amount
        qty_amount=ctk.CTkLabel(card,text=qty_amount,font=("Arial",11))
        qty_amount.grid(row=2,column=1,padx=12,pady=0)
        
        # store card

        self.category_cards[category_id] = {
    "frame": card,
    "normal_bg": bg,
    "selected_bg": "#CFDBFD",      
    "img_label": img_lbl,
    "img_normal": img,
    "img_selected": None,   
}
        
        #make whole card clickable
        def on_click(event, cid=category_id):
            self.on_category_click(cid)
       
            print(f"Clicked category: {name}")  
        for widget in (card, img_lbl, name_lbl, qty_lbl,qty_amount):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", lambda e, w=card: w.configure(cursor="hand2"))
            widget.bind("<Leave>", lambda e, w=card: w.configure(cursor=""))

        return card
    
    # for horizontal
    
    def make_horizontal_category_card(self,parent,row,col,name,qty_text,qty_amount,icon_path,category_id,bg="#E8EEF9"):
        card=ctk.CTkFrame(parent,fg_color=bg,corner_radius=30,width=130,height=170)
       
        card.grid(row=row,column=col,padx=20,pady=12,sticky="nw")
        
        #stop size form strech
        card.pack_propagate(False)
        card.grid_propagate(False)
        
        #grid inside the card
        for r in range(3):
            card.grid_rowconfigure(r,weight=1)
        card.grid_columnconfigure(0,weight=1)
        
        #image
        img=category_load_image(icon_path,size=(80,80))
        img_lbl=ctk.CTkLabel(card,text="",image=img,fg_color=bg)
        img_lbl.image=img
        img_lbl.grid(row=0,column=0,pady=(12,0),sticky="n")
        
        #name
        name_lbl = ctk.CTkLabel(card, text=name, font=("Arial", 14, "bold"), justify="center")
        name_lbl.grid(row=1, column=0, pady=(6, 0), sticky="n")
        
        #quantity
        qty_lbl=ctk.CTkLabel(card,text=qty_text,font=("Arial",11))
        qty_lbl.grid(row=2,column=0,pady=10,padx=0,sticky="n")
        
        # quantity amount
        qty_amount=ctk.CTkLabel(card,text=qty_amount,font=("Arial",11))
        qty_amount.grid(row=2,column=1,padx=12,pady=0)
        
        # store card

        self.horizontal_cards[category_id] = {
    "frame": card,
    "normal_bg": bg,
    "selected_bg": "#CFDBFD",      
    "img_label": img_lbl,
    "img_normal": img,
    "img_selected": None,   
    }
        
        #make whole card clickable
        def on_click(event, cid=category_id):
            self.on_category_click(cid)
       
            print(f"Clicked category: {name}")  
        for widget in (card, img_lbl, name_lbl, qty_lbl,qty_amount):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", lambda e, w=card: w.configure(cursor="hand2"))
            widget.bind("<Leave>", lambda e, w=card: w.configure(cursor=""))

        return card
    
    def on_category_click(self, category_id):
        print(f"Category Clicked{category_id}")
        
        if self.layout_mode=="overview":
            # self.switch_to_horizontal_layout(category_id)  # changing layout to horizontal
            self.layout_mode="detail"
            self.cards_container.grid_remove()
            self.horizontal_cards_container.grid()
            # self.horizontal_cards_container.grid(row=2,column=0,stikcy="ew",padx=20,pady=(10,0))
            
            if not self.horizontal_cards:
                categories=get_all_categories()
                for idx,(category_id,name,quantity,image_url) in enumerate(categories):
                   card_color = CARD_COLORS[idx % len(CARD_COLORS)]
                   self.make_horizontal_category_card(
                   parent=self.horizontal_cards_container,
                   row=0, col=idx,
                   name=name,
                   category_id=category_id,
                   qty_text="Quantity ",
                   qty_amount=str(quantity),
                   icon_path=image_url if image_url else os.path.join("images", "default.png"),  
                   bg=card_color
            )
            
        else:
            pass
        
        self.active_category_id=category_id
        
        for cid,info in self.horizontal_cards.items():
            card=info["frame"]
            
            if cid==category_id:
                # select card ko diff style
                card.configure(fg_color=info["selected_bg"])
                card.grid_configure(pady=(18,6))
                if info["img_selected"] is not None:
                    info["img_label"].configure(image=info["img_selected"])
            else:
                    card.configure(fg_color=info["normal_bg"])
                    card.grid_configure(pady=(12,12))
                    if info["img_selected"] is not None:
                        info["img_label"].configure(image=info["img_normal"])
            
        self.render_products_for_category(category_id)
        
    
    def switch_to_horizontal_layout(self,catgeory_id):
        
        order=[catgeory_id] + [cid for cid in self.category_cards.keys() if cid != catgeory_id]
        
        
        
        for current_col,cid in enumerate(order):
            info=self.category_cards[cid]
            card=info["frame"]
            card.configure(width=130,height=170)
            card.grid_propagate(True)
            card.grid_configure(row=0,column=current_col,padx=30,pady=(20,10), sticky="n")
            
        
        for col in range(len(order)):
            self.cards_container.grid_columnconfigure(col,weight=1)
                
            
    
    
    def render_products_for_category(self, category_id):
        # Clear previous cards
        for child in self.products_container.winfo_children():
            child.destroy()

        products = Get_products_by_category(category_id)
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

            # Product card
            card = ctk.CTkFrame(self.products_container, fg_color="#F7F7F7", corner_radius=20, width=170, height=190)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='n')
            card.grid_propagate(False)
            card.pack_propagate(False)

            # Image
            img = product_load_image(image_url, size=(60, 60)) if image_url else None
            if img:
                ctk.CTkLabel(card, image=img, text="").pack(pady=(8, 2))
            else:
                ctk.CTkLabel(card, text="🛒", font=("Arial", 20)).pack(pady=(8, 2))

            ctk.CTkLabel(card, text=name, font=("Arial", 12, "bold")).pack(pady=(2, 0))
            ctk.CTkLabel(card, text=f"${price}", font=("Arial", 14, "bold")).pack(pady=(0, 6))

            # Quantity control
            qty_frame = ctk.CTkFrame(card, fg_color="#DCE2FF", corner_radius=10)
            qty_frame.pack(pady=4)
            # qty_frame.pack_propagate(False)

            # starting qty
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
                                     command=lambda  qv=qty_var, stock=stock_quantity: self.increase(qv, stock))
            plus_btn.pack(side="left", padx=(2, 4))

            if stock_quantity == 0:
                plus_btn.configure(state="disabled")
                minus_btn.configure(state="disabled")

            # Add to cart button
            add_btn = ctk.CTkButton(
                card,
                text="Add to Cart 🛒",
                width=80,
                height=200,
                fg_color="#A4A4EB",
                text_color="white",
                corner_radius=12,
                command=lambda pid=prod_id, n=name, p=price, qv=qty_var, s=stock_quantity, cat_id=category_id:
                self.add_to_cart(pid, n, p, qv, s, cat_id)
            )
            add_btn.pack(pady=(2, 4),padx=(2,4))
            
    def increase(self,qv, stock):
                current = qv.get()
                if current < stock:
                    qv.set(current + 1)
                else:
                    self.show_message("Insufficient stock!", "red")

    def decrease(self,qv):
                current = qv.get()
                if current > 1:
                    qv.set(current - 1)
    
    def show_message(self,msg,color="green"):
        popup=ctk.CTkLabel(self,text=msg,text_color=color,font=("Arial",14,"bold"))
        popup.place(relx=0.5, rely=0.05, anchor="center")
        self.after(2000,popup.destroy) 
           
    def add_to_cart(self,product_id,name,price,qty_var,stock_quantity,category_id):
        qty=qty_var.get()
        if qty <= 0:
            self.show_message("Insufficient stock!","red")
            return
        
        if qty > stock_quantity:
            self.show_message("Not enough stock avaliable!","red")
            return
        
        customer_id=2   # update this later when integrating all parts to take id from login
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            
            cursor.execute("""
              SELECT cart_id, quantity
              FROM check_out
              WHERE product_id = %s
               AND customer_id = %s
             AND total IS NULL        --
    """, (product_id, customer_id))

            row=cursor.fetchone()
            if row is None:
                cursor.execute("INSERT INTO check_out (product_id, customer_id, items, price, quantity, item_total) VALUES (%s, %s, %s, %s, %s, %s)",
               (product_id, customer_id, name, price, qty, float(price) * qty))  

            else:
                cart_id, current_qty = row
                new_qty = current_qty + qty            #
                new_total = new_qty * float(price)
                cursor.execute("""
                  UPDATE check_out
                 SET quantity = %s,
                  item_total = %s
                 WHERE cart_id = %s
                AND total IS NULL                -
                """, (new_qty, new_total, cart_id))

            conn.commit()
            self.show_message(f"Added {qty} x {name} to cart!","green")
        except Exception as e:
            print(f"Cart Update error{e}")
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

    def dashboard(self):
        pass
    
    def show_categories(self):
        pass

    def show_checkout(self):
        pass

    def show_payment(self):
        pass

    def show_history(self):
        pass

    def show_settings(self):
        pass

    def logout(self):
        self.destroy()  # Close the current dashboard and exit the a


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
        try:
            img = Image.open(path).resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

def product_load_image(path, size=(60, 60)):
    try:
        img = Image.open(path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Product image load error for {path}: {e}")
        return None


           
if __name__=="__main__":
    app=Category()
    app.mainloop()




