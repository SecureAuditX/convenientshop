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

    


class Checkout(ctk.CTk): 
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
        self.dashboard_image = self.load_image("images/home.png")  # home image for Dashboard
        self.categories_image = self.load_image("images/category.png")  # category image for Categories
        self.checkout_image = self.load_image("images/checkout.png")  # cart image for Checkout
        self.payment_image = self.load_image("images/payment.png")  # credit card image for Payment
        self.history_image = self.load_image("images/history.png")  # history image for History
        self.settings_image = self.load_image("images/settings.png")  # gear image for Settings
        self.logout_image = self.load_image("images/logout.png")  # logout image for Exit button

          # Sidebar Buttons with Images and distance between buttons
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
        
        #<chechout start from here>
        
        
        # content_frame
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=10)
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
        
        # title checkout
        self.cats_label=ctk.CTkLabel(self.content_frame,text="Carts",
                                        font=("Arial",20,"italic","bold"))
        self.cats_label.grid(row=1,column=0,sticky='w',padx=32,pady=5)
        
        #check_out
        self.check_out_container=ctk.CTkFrame(self.content_frame,fg_color="#B4BAFF",corner_radius=10, width=1100, height=350)
        self.check_out_container.grid(row=2,padx=20,pady=20,sticky="nsew")
        self.check_out_container.grid_propagate(False)
        self.check_out_container.pack_propagate(False)
        
        # checkout_product
        self.checkout_product_container=ctk.CTkScrollableFrame(self.check_out_container,fg_color="#ECEFFA",width=820,height=260)
        self.checkout_product_container.grid(row=2,padx=(15,15),pady=(15,15),sticky="nsew")
        
        #total frame
        self.total_frame=ctk.CTkFrame(self.content_frame,fg_color="#B4BAFF",corner_radius=10,width=770,height=180)
        self.total_frame.grid(row=3,padx=20,pady=(1,5),sticky="nsew")
        self.total_frame.grid_propagate(False)
        self.total_frame.pack_propagate(False)
                # value labels (right side)
        self.sub_total_val = ctk.CTkLabel(self.total_frame, text="$0.00", font=("Arial",15))
        self.sub_total_val.grid(row=0, column=1, padx=(0,50), pady=(5,5), sticky="e")

        self.shipping_val = ctk.CTkLabel(self.total_frame, text="$0.00", font=("Arial",15))
        self.shipping_val.grid(row=1, column=1, padx=(0,50), pady=(5,5), sticky="e")

        self.total_val = ctk.CTkLabel(self.total_frame, text="$0.00",
                                      font=("Arial",15,"bold"), text_color="#975102")
        self.total_val.grid(row=3, column=1, padx=(0,50), pady=(5,5), sticky="e")

        # action buttons
        self.clear_btn = ctk.CTkButton(
            self.total_frame, text="Clear Cart",
            fg_color="#FF6B6B", hover_color="#E05757",
            width=120, height=36, corner_radius=18,
            command=self.clear_cart
        )

        self.clear_btn.grid(row=4, column=0, padx=(50,0), pady=(20,20), sticky="w")

        self.checkout_btn = ctk.CTkButton(
            self.total_frame, text="Checkout",
            fg_color="#4169E1", hover_color="#2F54B4",
            width=120, height=36, corner_radius=18,
           
        )

        self.checkout_btn.grid(row=4, column=1, padx=(500,50), pady=(20,20), sticky="e")

        
        # item label
        self.item_lbl=ctk.CTkLabel(self.check_out_container,text="Items",font=("Arial",15,"italic","bold"))
        self.item_lbl.grid(row=0,padx=(50,0),pady=(10,0),sticky='w')
        
        # description label
        self.desc_lbl=ctk.CTkLabel(self.check_out_container,text="Description",font=("Arial",15,"bold","italic"))
        self.desc_lbl.grid(row=0,column=0,padx=(200,0),pady=(10,0),sticky="nw")
        
        #price label
        self.price_lbl=ctk.CTkLabel(self.check_out_container,text="Price",font=("Arial",15,"italic","bold"))
        self.price_lbl.grid(row=0,padx=(400,0),pady=(10,0),sticky="nw")
        
        # quantity label
        self.qty_lbl=ctk.CTkLabel(self.check_out_container,text="Quantity",font=("Arial",15,"italic","bold")) 
        self.qty_lbl.grid(row=0,padx=(0,200),pady=(10,0),sticky="ne")
        
        #item_total
        self.item_total_lbl=ctk.CTkLabel(self.check_out_container,text="Item Total",font=("Arial",15,"italic","bold"))
        self.item_total_lbl.grid(row=0,padx=(0,50),pady=(10,0),sticky="ne")    
        
        #sub total label
        self.sub_total_lbl=ctk.CTkLabel(self.total_frame,text="SubTotal",font=("Arial",15,"italic","bold"))
        self.sub_total_lbl.grid(row=0,column=0,padx=(50,0),pady=(5,5),sticky="nw")
        
        #Shipping fee label
        self.shipping_lbl=ctk.CTkLabel(self.total_frame,text="Shipping Fee",font=("Arial",15,"italic","bold"))
        self.shipping_lbl.grid(row=1,column=0,padx=(50,0),pady=(5,5),sticky="w")
        
        #Total_label
        self.total_lbl=ctk.CTkLabel(self.total_frame,text="Total",font=("Arial",15,"italic","bold"),text_color="#975102")
        self.total_lbl.grid(row=3,padx=(50,0),pady=(5,5),sticky="w")
        self.customer_id=2  # change the id later and take it from login 
        self.load_cart()
    
    
    def load_cart(self):
        for child in self.checkout_product_container.winfo_children():
            child.destroy()
            
        rows=get_cart_items(self.customer_id)
        print("Rows fetched:", rows)
        
        if not rows:
            self.checkout_product_container.grid_rowconfigure(0, weight=1)
            self.checkout_product_container.grid_columnconfigure(0, weight=1)
            msg=ctk.CTkLabel(self.checkout_product_container,text="Your cart is empty",font=("Arial",30),text_color="red")
            msg.grid(row=0,column=0,padx=(20,20),pady=(100,100),sticky="nsew")
            self.update_totals_from_rows([])
            return
        
        subtotal=0.0
        
        for r_index, (cart_id, product_id, name, price, qty, item_total, img_url) in enumerate(rows):
            price = float(price)
            qty = int(qty)
    
            if item_total is None:
               item_total = price * qty
            else:
               item_total = float(item_total)
    
            subtotal += item_total  
            self.checkout_product_container.grid_columnconfigure(0, weight=1)

            row = ctk.CTkFrame(
              self.checkout_product_container,
              fg_color="#F6F7FF",
              corner_radius=10,
              height=70
             )
            row.grid(row=r_index,column=0,sticky="ew",padx=(5,0),pady=(0,1))
            row.grid_columnconfigure(1,weight=1)
            row.grid_propagate(False)
            
            img=cart_product_load_image(img_url)
            if img:
                img_lbl=ctk.CTkLabel(row,image=img,text="")
                img_lbl.image=img
            else:
                img_lbl=ctk.CTkLabel(row,text="🛒",font=("Arial",15))
            img_lbl.grid(row=0,column=0,padx=(25,10),sticky="w")
            
            name_lbl=ctk.CTkLabel(row,text=name,font=("Arial",13))
            name_lbl.grid(row=0,column=1,sticky="w",padx=(95,0),pady=(10,0))
            
            price_lbl=ctk.CTkLabel(row,text=f"{price:.2f}",font=("Arial",13))
            price_lbl.grid(row=0,column=2,padx=(0,170),pady=(10,0))
            
            qty_frame = ctk.CTkFrame(row, fg_color="#DCE2FF", corner_radius=16)
            qty_frame.grid(row=0,column=3,padx=(0,70),pady=(10,0))
            
            minus_btn=ctk.CTkButton(qty_frame,text="-",
                                    width=18,height=24,
                                    fg_color="transparent",text_color="black",
                                    hover_color="#C0C8F5",
                                    command=lambda cid=cart_id: self.change_cart_quantity(cid,-1))
            minus_btn.pack(side="left",padx=(4,2))
            
            qty_lbl=ctk.CTkLabel(qty_frame,text=str(qty),width=24)
            qty_lbl.pack(side="left")
            
            plus_btn=ctk.CTkButton(qty_frame,text="+",width=18,height=24,
                                   fg_color="transparent",text_color="black",
                                   hover_color="#C0C8F5",
                                   command=lambda cid=cart_id: self.change_cart_quantity(cid,+1))
            plus_btn.pack(side="left",padx=(2,4))
            
            item_total_lbl=ctk.CTkLabel(row,text=f"${item_total:.2f}",font=("Arial",13))
            item_total_lbl.grid(row=0,column=4,padx=(20,40))
        
        self.update_totals_from_rows(rows)
        
    
    def update_totals_from_rows(self,rows):
        subtotal=0.0
        for (_, _, _, price, qty, item_total, _) in rows:
            price=float(price)
            qty=int(qty)
            if item_total is None:
                subtotal+=price*qty
            else:
                subtotal+=float(item_total)
        
        shipping=6.10 if subtotal > 0 else 0.0
        total=subtotal+shipping
        
        self.sub_total_val.configure(text=f"${subtotal:.2f}")
        self.shipping_val.configure(text=f"${shipping:.2f}")
        self.total_val.configure(text=f"${total:.2f}")
        
    def change_cart_quantity(self,cart_id,delta):
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("SELECT quantity, price FROM check_out WHERE cart_id=%s and customer_id=%s AND total IS NULL",(cart_id,self.customer_id))
            row=cursor.fetchone()
            if not row:
               cursor.close()
               conn.close()
               return
        
            qty,price=row
            qty=int(qty)
            price=float(price)
            new_qty=qty+delta
        
            if new_qty <= 0:
               cursor.execute("DELETE FROM check_out WHERE cart_id=%s and customer_id=%s AND total IS NULL",(cart_id,self.customer_id))
            else:
                cursor.execute("UPDATE check_out SET quantity=%s, item_total=price*%s WHERE cart_id=%s and customer_id=%s AND total IS NULL",(new_qty,new_qty,cart_id,self.customer_id))
        
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Quantity update error: {e}")
        
        self.load_cart()
        
    def clear_cart(self):
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("DELETE FROM check_out WHERE customer_id=%s AND total IS NULL",(self.customer_id,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Clear Cart error: {e}")
        self.load_cart()
        
    


    
            
        
        

   
            
    
    
    
    
    def load_image(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((30, 30), Image.LANCZOS)  
            return ImageTk.PhotoImage(img)
        except FileNotFoundError:
            return None  

    
        
    
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
        self.destroy()  


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


def cart_product_load_image(path, size=(50,50)):
        try:
            img = Image.open(path).resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None



           
if __name__=="__main__":
    app=Checkout()
    app.mainloop()




