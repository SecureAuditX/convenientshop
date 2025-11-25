import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error
import os
import re
import random
from datetime import datetime

# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="mysql-convenientshop-conveniencestore01.b.aivencloud.com",
        user="avnadmin",  
        password="SECRET_HERE",  
        port = 24122,
        database="conv_shop_db" 
    )

class Payment(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("User Dashboard")
        self.geometry("1200x700")
        self.resizable(False, False)
        ctk.set_appearance_mode("system")

        # Main Frame
        self.main_frame = ctk.CTkFrame(self, fg_color="#F5F5F5", corner_radius=10)
        self.main_frame.pack(expand=True, fill="both", pady=10, padx=10)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Left Sidebar
        self.sidebar_frame = ctk.CTkFrame(self.main_frame, width=250, fg_color="#B4C9F9", corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=10)
        

        # Sidebar Images 
        self.dashboard_image = self.load_image("images/home.png")  # home image for Dashboard
        self.categories_image = self.load_image("images/category.png")  # category image for Categories
        self.checkout_image = self.load_image("images/checkout.png")  # cart image for Checkout
        self.payment_image = self.load_image("images/payment.png")  # credit card image for Payment
        self.history_image = self.load_image("images/history.png")  # history image for History
        self.settings_image = self.load_image("images/settings.png")  # gear image for Settings
        self.logout_image = self.load_image("images/logout.png")  # logout image for Exit button

        # Sidebar Buttons with Images and distance between buttons
        self.dashboard_button = ctk.CTkButton(self.sidebar_frame, image=self.dashboard_image, text="Dashboard", command=self.show_dashboard, width=200, height=40, font=("Arial", 16), fg_color="#A4A4EB", hover_color="#7777CA", compound="left")
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

        # Content area (where the dashboard items will be shown)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="white", corner_radius=10)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Search Bar
        self.search_bar=ctk.CTkEntry(self.content_frame,placeholder_text="🔍Search",
                                     font=("Arial",16,"bold"),fg_color="#979EEC",corner_radius=20,
                                     width=840,height=40,
                                     justify="center",text_color="#F5F5F5")
        self.search_bar.grid(padx=40,pady=40,column=0,row=0,sticky="ew")

        #<_______payment start here_____________>
        self.payment_label=ctk.CTkLabel(self.content_frame,text="Payment Options",
                                        font=("Arial",20,"italic","bold"))
        self.payment_label.grid(row=1,column=0,sticky='w',padx=32,pady=(10,0))
        
        self.customer_id=2 #hard coded for now
        
        #add card container
        self.add_card_container=ctk.CTkFrame(self.content_frame,fg_color="#F6F7FF",corner_radius=20,width=600,height=450)
        self.add_card_container.grid(row=2,sticky="nsw",padx=(30,10),pady=(10,10))
        self.add_card_container.grid_propagate(False)
        self.add_card_container.pack_propagate(False)
        self.add_card_container.grid_columnconfigure(0,weight=1)
        self.add_card_container.grid_columnconfigure(1,weight=1)
        # card lbl
        self.card_lbl=ctk.CTkLabel(self.add_card_container,text="Credit/Debit Card",text_color="blue",font=("Arial",20,"bold"))
        self.card_lbl.grid(row=0,sticky="nw",padx=(20,10),pady=(20,10))
        #heading
        self.secure_lbl=ctk.CTkLabel(self.add_card_container,text="Secure transfer using your bank account",text_color="black",font=("Arial",15,"italic","bold"))
        self.secure_lbl.grid(row=0,sticky="nw",padx=(30,10),pady=(50,10))
        
        #card imag lbls
        self.base_path=os.path.dirname(os.path.abspath(__file__))
        img=os.path.join(self.base_path,"images","unionpay.png")
        img=Image.open(img)
        img = ctk.CTkImage(light_image=img, size=(50, 50))
        unionpay_lbl=ctk.CTkLabel(self.add_card_container,text="",image=img,width=50,height=50)
        unionpay_lbl.grid(row=0,column=1,sticky="ne",padx=(20,20),pady=(10,10))

        img=os.path.join(self.base_path,"images","mastercard.png")
        img=Image.open(img)
        img=ctk.CTkImage(light_image=img,size=(50,50))
        mastercard_lbl=ctk.CTkLabel(self.add_card_container,image=img,text="",width=50,height=50)
        mastercard_lbl.grid(row=0,column=1,sticky="ne",padx=(10,80),pady=(10,10))

        img=os.path.join(self.base_path,"images","visa.png")
        img=Image.open(img)
        img=ctk.CTkImage(light_image=img,size=(50,50))
        mastercard_lbl=ctk.CTkLabel(self.add_card_container,image=img,text="",width=50,height=50)
        mastercard_lbl.grid(row=0,column=1,sticky="ne",padx=(10,135),pady=(10,10))
        
        #name
        name_lbl=ctk.CTkLabel(self.add_card_container,text="Full Name",text_color="black",font=("Arial",16))
        name_lbl.grid(row=1,sticky="nw",padx=(25,10),pady=(10,10))
        astrix_lbl=ctk.CTkLabel(self.add_card_container,text="*",text_color="red",font=("Arial",17)) 
        astrix_lbl.grid(row=1,sticky="nw",padx=(95,10),pady=(10,10))
        self.name_input=ctk.CTkEntry(self.add_card_container,placeholder_text="(eg. Jhon Alex)",fg_color="#D6D9FF",border_color="#D6D9FF",width=250,height=40)
        self.name_input.grid(row=1,sticky="w",padx=(20,10),pady=(40,10))
        # card combo
        card_type_lbl=ctk.CTkLabel(self.add_card_container,text="Card Type",text_color="black",font=("Arial",16))
        card_type_lbl.grid(row=1,column=1,sticky="nw",padx=(10,25),pady=(10,10))
        astrix_lbl=ctk.CTkLabel(self.add_card_container,text="*",text_color="red",font=("Arial",17)) 
        astrix_lbl.grid(row=1,column=1,sticky="nw",padx=(85,15),pady=(10,10))
        self.card_combo=ctk.CTkComboBox(self.add_card_container,values=["Visa","Master Card","Union Pay"],fg_color="#D6D9FF",border_color="#D6D9FF",width=250,height=40)
        self.card_combo.grid(row=1,column=1,sticky="e",padx=(10,20),pady=(40,10))
        self.card_combo.set("visa")
        # card num
        card_numbr_lbl=ctk.CTkLabel(self.add_card_container,text="Card No",text_color="black",font=("Arial",16))
        card_numbr_lbl.grid(row=2,sticky="nw",padx=(25,10),pady=(10,10))
        astrix_lbl=ctk.CTkLabel(self.add_card_container,text="*",text_color="red",font=("Arial",17)) 
        astrix_lbl.grid(row=2,sticky="nw",padx=(85,15),pady=(10,10))
        self.card_numbr_entry=ctk.CTkEntry(self.add_card_container,placeholder_text="(eg. 4335-6765-74300)",fg_color="#D6D9FF",border_color="#D6D9FF",width=250,height=40)
        self.card_numbr_entry.grid(row=2,sticky="w",padx=(20,10),pady=(40,10))
        self.card_numbr_entry.bind("<KeyRelease>", self.update_card_type)
        # expiry
        card_expiry_lbl=ctk.CTkLabel(self.add_card_container,text="Expiration Date",text_color="black",font=("Arial",16))
        card_expiry_lbl.grid(row=2,column=1,sticky="nw",padx=(10,150),pady=(10,10))
        astrix_lbl=ctk.CTkLabel(self.add_card_container,text="*",text_color="red",font=("Arial",17)) 
        astrix_lbl.grid(row=2,column=1,sticky="nw",padx=(120,15),pady=(10,10))
        self.card_expiry_entry=ctk.CTkEntry(self.add_card_container,placeholder_text="(eg. MM/YY)",fg_color="#D6D9FF",border_color="#D6D9FF",width=150,height=40)
        self.card_expiry_entry.grid(row=2,column=1,sticky="e",padx=(10,150),pady=(40,10))
       # cvv
        cvv_lbl=ctk.CTkLabel(self.add_card_container,text="CVV",text_color="black",font=("Arial",16))
        cvv_lbl.grid(row=2,column=1,sticky="ne",padx=(10,85),pady=(10,10))
        astrix_lbl=ctk.CTkLabel(self.add_card_container,text="*",text_color="red",font=("Arial",17)) 
        astrix_lbl.grid(row=2,column=1,sticky="ne",padx=(10,75),pady=(10,10))
        self.cvv_entry=ctk.CTkEntry(self.add_card_container,placeholder_text="(eg. 342)",fg_color="#D6D9FF",border_color="#D6D9FF",width=100,height=40)
        self.cvv_entry.grid(row=2,column=1,sticky="e",padx=(10,20),pady=(40,10))
        # address
        address_lbl=ctk.CTkLabel(self.add_card_container,text="Address",text_color="black",font=("Arial",16))
        address_lbl.grid(row=3,column=0,sticky="nw",padx=(25,10),pady=(10,10))
        astrix_lbl=ctk.CTkLabel(self.add_card_container,text="*",text_color="red",font=("Arial",17)) 
        astrix_lbl.grid(row=3,column=0,sticky="nw",padx=(85,10),pady=(10,10))
        self.address_entry=ctk.CTkEntry(self.add_card_container,placeholder_text="(eg. building 27, Nanchang University)",fg_color="#D6D9FF",border_color="#D6D9FF",width=300,height=40)
        self.address_entry.grid(row=3,column=0,sticky="w",padx=(20,10),pady=(40,10))
        # email
        email_lbl=ctk.CTkLabel(self.add_card_container,text="Email",text_color="black",font=("Arial",16))
        email_lbl.grid(row=3,column=1,sticky="ne",padx=(10,210),pady=(10,10))
        astrix_lbl=ctk.CTkLabel(self.add_card_container,text="*",text_color="red",font=("Arial",17)) 
        astrix_lbl.grid(row=3,column=1,sticky="ne",padx=(10,200),pady=(10,10))
        self.email_entry=ctk.CTkEntry(self.add_card_container,placeholder_text="(eg. chlbehchl@gmail.com)",fg_color="#D6D9FF",border_color="#D6D9FF",width=250,height=40)
        self.email_entry.grid(row=3,column=1,sticky="e",padx=(10,20),pady=(40,10))
        
        # alipay/wechat pay container
        self.alipay_container=ctk.CTkFrame(self.add_card_container,fg_color="#D6D9FF",height=80,corner_radius=10)
        self.alipay_container.grid(row=5,column=0,columnspan=2,sticky="ew",padx=(20,20),pady=(2,4))
        self.alipay_container.grid_propagate(False)
        
        # scan&pay label
        scan_lbl=ctk.CTkLabel(self.alipay_container,text="Scan & Pay",justify="center",text_color="black",font=("Arial",20))
        scan_lbl.grid(row=0,column=0,sticky="w",padx=(250,10),pady=(30,30))
        
        #logo
        self.base_path=os.path.dirname(os.path.abspath(__file__))
        img=os.path.join(self.base_path,"images","alipay.png")
        img=Image.open(img)
        img = ctk.CTkImage(light_image=img, size=(50, 50))
        alipay_btn=ctk.CTkButton(self.alipay_container,text="",image=img,width=90,height=65,corner_radius=20)
        alipay_btn.grid(row=0,column=0,sticky="w",padx=(20,20),pady=(10,10))
        # we
        self.base_path=os.path.dirname(os.path.abspath(__file__))
        img=os.path.join(self.base_path,"images","wepay.png")
        img=Image.open(img)
        img = ctk.CTkImage(light_image=img, size=(50, 50))
        wepay_btn=ctk.CTkButton(self.alipay_container,text="",image=img,width=90,height=65,corner_radius=20)
        wepay_btn.grid(row=0,column=1,sticky="e",padx=(80,20),pady=(10,10))
        
        # error
        # self.message_label=ctk.CTkLabel(self.add_card_container,text="",text_color="red",font=("Arial",12))
        # self.message_label.grid(row=0, column=0, columnspan=2, pady=(5, 0))

        #cart bill container
        self.cart_bill_container=ctk.CTkFrame(self.content_frame,fg_color="#D6D9FF",corner_radius=20,width=260,height=450)
        self.cart_bill_container.grid(row=2,sticky="nse",padx=(10,30),pady=(2,4))     
        self.cart_bill_container.grid_propagate(False)
        self.cart_bill_container.pack_propagate(False)   
        
        #cart bill
        cart_bill_lbl=ctk.CTkLabel(self.cart_bill_container,text="Cart Bill",font=("Arial",20),text_color="black")
        cart_bill_lbl.grid(row=0,sticky="nw",padx=(90,10),pady=(20,20))
        
        #subtotal lbl
        subtotal_lbl=ctk.CTkLabel(self.cart_bill_container,text="Subtotal",text_color="black",font=("Arial",15))
        subtotal_lbl.grid(row=1,sticky="w",padx=(20,20),pady=(20,20))
        
        #shiipong
        shipping_lbl=ctk.CTkLabel(self.cart_bill_container,text="Shipping fee",font=("Arial",16),text_color="black")
        shipping_lbl.grid(row=2,sticky="w",padx=(20,20),pady=(20,20))
        
        #total
        total_label=ctk.CTkLabel(self.cart_bill_container,text="Total: ",text_color="#975102",font=("Arial",15,"italic","bold"))
        total_label.grid(row=3,sticky="e",padx=(20,80),pady=(20,20))
        
                        # value labels (right side)
        self.sub_total_val = ctk.CTkLabel(self.cart_bill_container, text="$0.00", font=("Arial",15))
        self.sub_total_val.grid(row=1, padx=(0,20), pady=(5,5), sticky="e")

        self.shipping_val = ctk.CTkLabel(self.cart_bill_container, text="$0.00", font=("Arial",15))
        self.shipping_val.grid(row=2, padx=(0,20), pady=(5,5), sticky="e")

        self.total_val = ctk.CTkLabel(self.cart_bill_container, text="$0.00",
                                      font=("Arial",15,"bold"), text_color="#975102")
        self.total_val.grid(row=3, padx=(0,20), pady=(5,5), sticky="e")
        self.update_totals()
        # save and pay
        save_pay_btn=ctk.CTkButton(self.cart_bill_container,text="Save and Pay",text_color="black",fg_color="#727AE0",font=("Arial",18),corner_radius=20,width=80,height=37,hover_color="#9197EB",command=self.on_save_and_pay)
        save_pay_btn.grid(row=4,sticky="s",padx=(60,20),pady=(150,20))
        
        
        
        
    def update_totals(self):
        try:
            rows=get_cart_items(self.customer_id)
        except Exception as e:
            print(f"Error loading cart items in payment: {e}")
            rows=[]
        
        subtotal=0.0
        
        for (_, _, _, price, qty, item_total, _) in rows:
            price=float(price)
            qty=int(qty)
            
            if item_total is None:
                subtotal+=price*qty
            else:
                subtotal+=float(item_total)
                
        shipping=6.10 if subtotal > 0 else 0.00
        total=subtotal+shipping
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
        
        if not re.match(r"^[A-Za-z]+(?: [A-Za-z]+)*$", full_name):
            return False, "Please enter a valid full name (letters and spaces only)"
        
        if not card_no_raw.isdigit() or not (len(card_no_raw)<=16):
            return False, "Please enter a valid card number(13-19 digits)."
        
        card_no_masked="**** **** **** "+ card_no_raw[-4:]
        
        if not re.match(r"^\d{2}/\d{2}$",exp_raw):
            return False, "Expiration date must be in MM/YY Format"
        
        month=int(exp_raw[:2])
        year=2000+ int(exp_raw[3:])
        if not (1<month<=12):
            return False,"Expiration month must be bettween 01 and 12"
        
        now=datetime.now()
        if year <now.year or (year ==now.year and month< now.month):
            return False, "Card is expired"
        
        if not cvv_raw.isdigit() or len(cvv_raw) !=3:
            return False, "CVV must be 3 digits."
        
        if not address:
            return False, "Address is required"
        
        if len(address) > 255:
            return False, "Address is too long"
        
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",email):
            return False, "Please enter a valid email address"
        
        exp_date=datetime(year,month,1)
        data={
            "full_name": full_name,
            "card_type": card_type,
            "card_no_masked": card_no_masked,
            "exp_date": exp_date,
            "cvv_masked":"***",
            "address":address,
            "email":email
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
        
    def show_message(self,msg,color="red"):
        popup=ctk.CTkLabel(self,text=msg,text_color=color,font=("Arial",14,"bold"))
        popup.place(relx=0.5, rely=0.05, anchor="center")
        self.after(2000,popup.destroy) 
        
    def on_save_and_pay(self):
   
        ok, data_or_msg = self.validate_payment_form()
        if not ok:
            self.show_message(data_or_msg, "red")
            return

        data = data_or_msg

  
        rows = get_cart_items(self.customer_id)
        if not rows:
            self.show_message("Your cart is empty.", "red")
            return

        
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

   
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

          
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
            payment_id = cursor.lastrowid  

         
            order_no = random.randint(100000, 999999)

            for (cart_id, product_id, _, price, qty, item_total, _) in rows:
                price = float(price)
                qty = int(qty)
                if item_total is None:
                    item_total = price * qty
                else:
                    item_total = float(item_total)

              
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

              
                cursor.execute(
                    """
                    UPDATE product
                    SET stock_quantity = stock_quantity - %s
                    WHERE product_id = %s
                    """,
                    (qty, product_id)
                )

               
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

        self.update_totals()        
        self.show_message(f"Payment successful! Order #{order_no}", "green")


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

    def load_image(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((30, 30), Image.LANCZOS)  # Resize image for the sidebar button icons
            return ImageTk.PhotoImage(img)
        except FileNotFoundError:
            return None  # Return None if the image is not found
        
        
    def show_dashboard():
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
        self.destroy()  # Close the current dashboard and exit the app
        

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
        AND c.total IS NULL         --  IMPORTANT
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

if __name__ == "__main__":
    app = Payment()
    app.mainloop()

