from db_file import db
import customtkinter as ctk
from PIL import Image, ImageTk
import hashlib
import bcrypt
import re
import os
import customtkinter as ctk
import os
from PIL import Image,ImageTk
import mysql.connector
from mysql.connector import Error


def get_db_connection():
    return mysql.connector.connect(
        host="mysql-convenientshop-conveniencestore01.b.aivencloud.com",
        user="avnadmin",
        password="AVNS_2jwXFZ6i4VHBaoWwW6u",
        port=24122,
        database="conv_shop_db"
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

IMAGE_BASE_DIR = r"C:\Users\Mubashra Nouman\Documents\phyton programs\ConvenientShop\images"

class UserDashboard(ctk.CTk):
    def __init__(self, customer_id, email):
        super().__init__()
        self.customer_id = customer_id
        self.email = email
        
      
        self.title("Admin Dashbaord Management")
        self.geometry("1200x800")
        self.resizable(True, True)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar_frame = ctk.CTkFrame(self, fg_color="#E0DDF0", corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
       
        for i in range(0, 12):
            self.sidebar_frame.grid_rowconfigure(i, weight=0)  
        self.sidebar_frame.grid_rowconfigure(11, weight=1)
       
        self.profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.profile_frame.grid(row=0, column=0, padx=10, pady=20, sticky="ew")
        
        
        try:
            profile_icon_path = image_path_join(os.path.dirname(__file__), "profile.png")
            if not os.path.exists(profile_icon_path):
                profile_icon_path = os.path.join(IMAGE_BASE_DIR, "profile.png")
            profile_image = Image.open(profile_icon_path).resize((80, 80), Image.LANCZOS)
            self.profile_ctk_image = ImageTk.PhotoImage(profile_image)
            
            self.profile_label = ctk.CTkLabel(self.profile_frame, image=self.profile_ctk_image, text="")
            self.profile_label.grid(row=0, column=0, padx=10, pady=5)
        
        except Exception:
            
            self.profile_label = ctk.CTkLabel(self.profile_frame, text="👤", font=("Arial", 40))
            self.profile_label.grid(row=0, column=0, padx=10, pady=5)
            
        self.username_label = ctk.CTkLabel(self.profile_frame, text="Admin Dashboard", font=("Arial", 14, "bold"), text_color="black")
        self.username_label.grid(row=1, column=0, padx=10, pady=5)
        
        self.dashboard_button = ctk.CTkButton(self.sidebar_frame, text="Home",
                                              fg_color="transparent", text_color="black",
                                              hover_color="#D7D2F4", font=("Arial", 16, "bold"),
                                              anchor="w", image=self.load_icon("home.png", 20),
                                              compound="left", command=self.show_dashboard_content,
                                              width=150, height=50) 
        self.dashboard_button.grid(row=2, column=0, padx=10, pady=8, sticky="ew")   
    
        self.stock_button = ctk.CTkButton(self.sidebar_frame, text="Stock Management", 
                                               fg_color="transparent", text_color="black",
                                               hover_color="#D7D2F4", font=("Arial", 16), 
                                               anchor="w", image=self.load_icon("stock.png", 20), 
                                               compound="left", command=self.show_stock_content,
                                               width=150, height=50)
        self.stock_button.grid(row=3, column=0, sticky="ew", pady=8, padx=10) 
        
        self.finance_button = ctk.CTkButton(self.sidebar_frame, text="Finance", 
                                               fg_color="transparent", text_color="black",
                                               hover_color="#D7D2F4", font=("Arial", 16), 
                                               anchor="w", image=self.load_icon("finance.png", 20), 
                                               compound="left", command=self.show_finance_content,
                                               width=150, height=50)
        self.finance_button.grid(row=3, column=0, sticky="ew", pady=8, padx=10)
        
        self.report_button = ctk.CTkButton(self.sidebar_frame, text="Report", 
                                             fg_color="transparent", text_color="black", 
                                             hover_color="#D7D2F4", font=("Arial", 16), 
                                             anchor="w", image=self.load_icon("report.png", 20),
                                             compound="left", command=self.show_report_content,
                                             width=150, height=50)
        self.report_button.grid(row =4, column=0, sticky="ew", pady=8, padx=10)
        
        self.announcement_button = ctk.CTkButton(self.sidebar_frame, text="Announcement", 
                                            fg_color="transparent", text_color="black",
                                            hover_color="#D7D2F4", font=("Arial", 16), 
                                            anchor="w", image=self.load_icon("announcement.png", 20), 
                                            compound="left", command=self.show_announcement_content,
                                            width=150, height=50)
        self.announcement_button.grid(row=5, column=0, sticky="ew", pady=8, padx=10)

        self.user_button = ctk.CTkButton(self.sidebar_frame, text="Users", 
                                            fg_color="transparent", text_color="black",
                                            hover_color="#D7D2F4", font=("Arial", 16), 
                                            anchor="w", image=self.load_icon("users.png", 20), 
                                            compound="left", command=self.show_users_content,
                                            width=150, height=50)
        self.user_button.grid(row=6, column=0, sticky="ew", pady=8, padx=10)

        self.setting_button = ctk.CTkButton(self.sidebar_frame, text="Setting", 
                                            fg_color="transparent", text_color="black",
                                            hover_color="#D7D2F4", font=("Arial", 16), 
                                            anchor="w", image=self.load_icon("setting.png", 20), 
                                            compound="left", command=self.show_setting_content,
                                            width=150, height=50)
        self.setting_button.grid(row=7, column=0, sticky="ew", pady=8, padx=10)   
        
       
        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Logout", 
                                           fg_color="transparent", text_color="black",
                                           hover_color="#D7D2F4", font=("Arial", 16), 
                                           anchor="w", image=self.load_icon("exit.png", 20), 
                                           compound="left", command=self.logout,
                                           width=150, height=50)
        self.logout_button.grid(row=15, column=0, sticky="ew", pady=(10, 20), padx=10)
        
        self.main_frame=ctk.CTkFrame(self,fg_color="#F5F5F5",corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0,weight=1)
        self.main_frame.grid_rowconfigure(0,weight=1)    
        # Main Content Area (Right panel)
        # self.main_content_area = ctk.CTkFrame(self, fg_color="#F7F7F7", corner_radius=0)
        # self.main_content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        # self.main_content_area.grid_columnconfigure(0, weight=1) # Center content horizontally
        # self.main_content_area.grid_rowconfigure(0, weight=1)
        
        # # Content Frames for different sections (Dashboard, Categories, etc.) 
        # # self.dashboard_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        # self.stock_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        # self.finance_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        # self.report_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        # self.announcement_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        # self.users_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        # self.setting_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        
        # admin user dashboard starts here
                # content_frame
        self.content_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent",  
        bg_color="transparent", corner_radius=10)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame._parent_canvas.configure(width=1200)
        self.content_frame.pack_propagate(False)


       # grid setup
        for i in range(4):
              self.content_frame.grid_columnconfigure(i, weight=1)

        
        for r in range(5):
            self.content_frame.grid_rowconfigure(r, weight=0)
        
        ### user start from here##
        #lbl
        self.user_lbl=ctk.CTkLabel(self.content_frame,text="Users",font=("Arial",22,"bold"),text_color="black")
        self.user_lbl.grid(row=0,padx=(20,20),pady=(20,20),sticky="w",columnspan=4)
        
        self.back_lbl=ctk.CTkLabel(self.content_frame,text="Manage your team members and their access",font=("Arial",17),text_color="grey")
        self.back_lbl.grid(row=0,padx=(30,20),pady=(80,20),sticky="w",columnspan=4)
        
        #additem btn
        self.add_user=ctk.CTkButton(self.content_frame,text="+    Add User",fg_color="#D4D4D4",text_color="black",width=80,height=40,corner_radius=20,command=self.open_add_dialog)
        self.add_user.grid(row=0,sticky="e",padx=(20,20),pady=(20,20),columnspan=4)
        
        self.total_users=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=200,height=130,corner_radius=20)
        self.total_users.grid(row=2,column=0,padx=(10,10),pady=(10,10),sticky="w")
        self.total_users.grid_propagate(False)
        
        self.total_lbl=ctk.CTkLabel(self.total_users,text="Total Users",text_color="grey",font=("Arial",14,"bold"))
        self.total_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")
        # val lbl idhr ayein gye
        self.users_val=ctk.CTkLabel(self.total_users,text="0",font=("Arial",15))
        self.users_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,10))
              
        self.total_active=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=200,height=130,corner_radius=20)
        self.total_active.grid(row=2,column=1,padx=(10,10),pady=(10,10),sticky="w")
        self.total_active.grid_propagate(False)
        
        self.total_lbl=ctk.CTkLabel(self.total_active,text="Active",text_color="grey",font=("Arial",14,"bold"))
        self.total_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")
        # val lbl idhr ayein gye
        self.active_val=ctk.CTkLabel(self.total_active,text="0",font=("Arial",15))
        self.active_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,10))
              
        self.total_admins=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=200,height=130,corner_radius=20)
        self.total_admins.grid(row=2,column=2,padx=(10,10),pady=(10,10),sticky="e")
        self.total_admins.grid_propagate(False)
        
        self.total_lbl=ctk.CTkLabel(self.total_admins,text="Admins",text_color="grey",font=("Arial",14,"bold"))
        self.total_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")
        # val lbl idhr ayein gye
        self.admins_val=ctk.CTkLabel(self.total_admins,text="0",font=("Arial",15))
        self.admins_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,10))
              
        self.staff=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=170,height=130,corner_radius=20)
        self.staff.grid(row=2,column=3,padx=(10,10),pady=(10,10),sticky="e")
        self.staff.grid_propagate(False)
        
        self.users_lbl=ctk.CTkLabel(self.staff,text="staff",text_color="grey",font=("Arial",14,"bold"))
        self.users_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")        
        # val lbl idhr ayein gye
        self.staff_val=ctk.CTkLabel(self.staff,text="0",font=("Arial",15))
        self.staff_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,10))
        
        self.search_bar=ctk.CTkEntry(self.content_frame,placeholder_text="🔍Search",
                                     font=("Arial",16,"bold"),fg_color="#D4D4D4",corner_radius=20,
                                     width=920,height=40,
                                     justify="center",text_color="#F5F5F5")
        self.search_bar.grid(padx=(20,20),pady=(20,20),column=0,row=3,sticky="w",columnspan=4)
        self.search_bar.bind("<KeyRelease>", lambda e: self.refresh_table())
        
        self.header_table(start_row=4)
        self.update_summary_cards()
        self.load_user_table()
        # self.show_dashboard_content()
        
        
    
    def update_summary_cards(self):
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers;")
            items=cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM customers WHERE status = 'active';")
            value=cursor.fetchone()[0] or 0
            cursor.execute("""
            SELECT COUNT(l.customer_id) FROM login l
            JOIN customers c ON l.customer_id = c.customer_id
            WHERE l.role='admin';
            """)
            qty=cursor.fetchone()[0] or 0
            cursor.execute("""
            SELECT COUNT(l.customer_id) FROM login l
            JOIN customers c ON l.customer_id = c.customer_id
            WHERE l.role='staff';
            """)
            staff=cursor.fetchone()[0] or 0
            conn.close()
            cursor.close()
            self.users_val.configure(text=str(items))
            self.active_val.configure(text=str(value))
            self.admins_val.configure(text=str(qty))
            self.staff_val.configure(text=str(f"{staff}"))
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
                    columnspan=4,
                    )
        
       
        header.grid_columnconfigure(0, weight=2, uniform="a") 
        header.grid_columnconfigure(1, weight=1, uniform="a") 
        header.grid_columnconfigure(2, weight=1, uniform="a") 
        header.grid_columnconfigure(3, weight=1, uniform="a") 
        # header.grid_columnconfigure(4, weight=2, uniform="a") 
        # header.grid_columnconfigure(5, weight=2, uniform="a") 
        # header.grid_columnconfigure(6, weight=2, uniform="a") 
        # header.grid_columnconfigure(7, weight=3, uniform="a") 
        # header.grid_columnconfigure(8, weight=2, uniform="a") 
       
        header.grid_propagate(False)
        
        labels=[
            ("User",0,"w"),
            ("Role",1,"w"),
            ("Status",2,""),
            ("Actions",3,"e"),
            # ("Actions",5),
            # ("Supplier",6),
            # ("Last Restocked",7),
            # ("Actions",8),
        ]
        
        for text, col, anchor in labels:
            lbl = ctk.CTkLabel(header, text=text, font=("Arial", 13, "bold"))
           
            pad_x = (20, 10) if anchor == "w" else (10, 20)
            lbl.grid(row=0, column=col, padx=pad_x, pady=5, sticky=anchor)\
                
    def load_user_table(self):
     
        for widget in self.content_frame.winfo_children():
         
             grid_info = widget.grid_info()
             if int(grid_info['row']) >= 5: 
                 widget.destroy()

        search_text = self.search_bar.get().strip()
        rows = self.get_filtered_user(search_text) if search_text else get_users()
        
        start_row = 5   
        for r_idx, (customer_id, first_name, last_name, role, status, is_locked) in enumerate(rows):
            
            row_bg = "#F6F7FF"
            
            if is_locked:
                row_bg = "#FFEBEB"

            row = ctk.CTkFrame(self.content_frame, fg_color=row_bg, corner_radius=10, height=40)
            row.grid(row=start_row + r_idx, column=0, sticky="ew", padx=(10,10), pady=(5, 5), columnspan=4)
            
            
            row.grid_columnconfigure(0, weight=2, uniform="a") 
            row.grid_columnconfigure(1, weight=1, uniform="a") 
            row.grid_columnconfigure(2, weight=1, uniform="a") 
            row.grid_columnconfigure(3, weight=1, uniform="a") 
               
            
            full_name = f"{first_name} {last_name}"
            
           
            ctk.CTkLabel(row, text=full_name, font=("Arial",13)).grid(row=0, column=0, sticky="w", padx=10)
                        
            
            ctk.CTkLabel(row, text=role, font=("Arial",13)).grid(row=0, column=1, sticky="w", padx=10)
            
            
            status_text = "LOCKED" if is_locked else status
            status_color = "#DC2626" if is_locked else ("#10B981" if status.lower() == 'active' else "grey")
            
            ctk.CTkLabel(row, text=status_text, text_color="white", fg_color=status_color, corner_radius=5, padx=5).grid(row=0, column=2, padx=10)
            
            
            actions_frame = ctk.CTkFrame(row, fg_color="transparent")
            actions_frame.grid(row=0, column=3, sticky="e", padx=10)
            
        
            ctk.CTkButton(actions_frame, text="✏️", width=30, fg_color="white", text_color="black",
                          command=lambda cid=customer_id: self.open_edit_dialog(cid)).pack(side="left", padx=5)
            
        
            ctk.CTkButton(actions_frame, text="🗑️", width=30, fg_color="white", text_color="red",
                          command=lambda cid=customer_id: self.delete_user(cid)).pack(side="left")
    
    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New User")
        dialog.geometry("500x550")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Add New User", font=("Arial", 18, "bold")).pack(pady=20)


        name_entry = ctk.CTkEntry(dialog, placeholder_text="Full Name", width=300)
        name_entry.pack(pady=10)
        email_entry = ctk.CTkEntry(dialog, placeholder_text="Email", width=300)
        email_entry.pack(pady=10)
        password_entry = ctk.CTkEntry(dialog, placeholder_text="password", width=300)
        password_entry.pack(pady=10)
        role_combo = ctk.CTkComboBox(dialog, values=["Staff", "Manager", "Admin"], width=300)
        role_combo.pack(pady=10)
        status_combo = ctk.CTkComboBox(dialog, values=["Active", "Inactive"], width=300)
        status_combo.pack(pady=10)

        def save_user():
            full_name = name_entry.get().strip()
            email = email_entry.get().strip()
            password = password_entry.get().strip() 
            role = role_combo.get().lower()
            status = status_combo.get().lower()
            
            
            if not self.is_secure_password(self,password):
                self.show_message(
                    title="Error",
                    message="Password must be ≥ 8 characters and include:\n"
                            "- Uppercase letter\n"
                            "- Lowercase letter\n"
                            "- Number\n"
                            "- Special symbol (@$!%*#?&)",
                    icon="cancel"
                )
                return 

            
            salt = bcrypt.gensalt()
            
            hashed_password_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
            
         
            hashed_password_str = hashed_password_bytes.decode('utf-8')
            
            
            hashed_email = hashlib.sha256(email.lower().encode('utf-8')).hexdigest()
            
           

            if not full_name or not email:
                print("Error: Name and Email required")
                return

            parts = full_name.split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                
                sql_cust = "INSERT INTO customers (first_name, last_name, email, phone_no, address, status) VALUES (%s, %s, %s, 'N/A', 'N/A', %s)"
                cursor.execute(sql_cust, (first_name, last_name, hashed_email, status))
                new_id = cursor.lastrowid
                
               
                sql_login = "INSERT INTO login (customer_id, email, password, role, is_locked) VALUES (%s, %s, %s, %s, 0)"
                cursor.execute(sql_login, (new_id, email, hashed_password_str, role)) 
                
                conn.commit()
                cursor.close()
                conn.close()
                self.show_message("User Added!", "green")
                dialog.destroy()
                self.refresh_table()
                self.update_summary_cards()
            except Error as e:
                print(f"Add Error: {e}")
                self.show_message("Database Error", "red")

        ctk.CTkButton(dialog, text="Save User", command=save_user, fg_color="black").pack(pady=20)
    
    def is_secure_password(password):
            return (
                len(password) >= 8 and
                re.search(r"[A-Z]", password) and
                re.search(r"[a-z]", password) and
                re.search(r"[0-9]", password) and
                re.search(r"[@$!%*#?&]", password)
            )
    
    def open_edit_dialog(self, customer_id):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Manage User")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Manage User Account", font=("Arial", 18, "bold")).pack(pady=20)

        
        def unblock_user(customer_id):
            
            try:
                conn=get_db_connection()
                cursor=conn.cursor()
                sql_unlock = "UPDATE login SET is_locked=0, error_login_attempt=0 WHERE customer_id=%s"
                cursor.execute(sql_unlock, (customer_id,))
                sql_active = "UPDATE customers SET status='active' WHERE customer_id=%s"
                cursor.execute(sql_active, (customer_id,))
                conn.commit()
                cursor.close()
                conn.close()
                self.show_message("User Unblocked Successfully", "green")
                self.refresh_table()
                dialog.destroy()
            except Exception as e:
                print(f"Unblock error: {e}") 
                self.show_message("Database Error", "red")         
        # button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        # button_frame.pack(fill="both", pady=(10, 20), padx=20,expand=True)
        # button_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(dialog, text="🔓 Unblock User", fg_color="green", command=lambda: unblock_user(customer_id)).pack(pady=20)
        ctk.CTkButton(dialog, text="Cancel", fg_color="transparent", border_width=1, text_color="black", command=dialog.destroy).pack()


    def validate_fields(self,dialog,vals):
        required=["first_name","last_name","email"]
        
        for field in required:
            if not vals[field]:
                return False,"nothing found error"
        
        
        if not re.match(r"^[A-Za-z].*$", vals["first_name"]):
            return False, "Please enter valid first name"
        
        if not re.match(r"^[A-Za-z].*$", vals["last_name"]):
            return False, "Please enter a valid last name "
        
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",vals['email']):
            return False, "Please enter a valid email address"
        
        if not vals["first_name"].strip():
            return False, "Product name cannot be blank."
        
        
        return True, vals
    
    def show_message(self,msg,color="red"):
        popup=ctk.CTkLabel(self,text=msg,text_color=color,font=("Arial",14,"bold"))
        popup.place(relx=0.5, rely=0.05, anchor="center")
        self.after(2000,popup.destroy) 
    

    def delete_user(self,customer_id:int):
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            
            
            cursor.execute("DELETE FROM login WHERE customer_id=%s",(customer_id,))
            
        
            cursor.execute("DELETE FROM customers WHERE customer_id=%s",(customer_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            self.show_message("User deleted successfully!", "green") 
            self.update_summary_cards() 
            self.refresh_table()
        except Exception as e:
            print(f"Delete error: {e}")
            self.show_message(f"Delete error: {e}", "red") 
            
    def refresh_table(self):
            for widget in self.content_frame.winfo_children():
                if isinstance(widget,ctk.CTkFrame) and widget not in (self.total_users,self.total_active,self.total_admins,self.staff):
                    widget.destroy()
            self.header_table(start_row=4)
            self.load_user_table()
        
    def get_filtered_user(self, search_text):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        SELECT 
            c.customer_id, c.first_name, c.last_name, 
            l.role, c.status, l.is_locked
        FROM customers c 
        JOIN login l ON c.customer_id = l.customer_id
        WHERE 1=1 
        """
        params = []
        
        if search_text:
        
            search_pattern = f"%{search_text}%"
            
            query += """
            AND (
                c.first_name LIKE %s OR 
                c.last_name LIKE %s OR 
                l.role LIKE %s OR 
                c.status LIKE %s
            )
            """
            params += [search_pattern, search_pattern, search_pattern, search_pattern]
        
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
        except Exception as e:
            print(f"DB filtered user fetching error: {e}")
            rows = []

        cursor.close()
        conn.close()
        return rows
        
    
    
    def load_icon(self, icon_name, size):
        
        try_paths = [
            os.path.join(IMAGE_BASE_DIR, icon_name),
            os.path.join(os.path.dirname(__file__), "icons", icon_name),
            os.path.join(os.path.dirname(__file__), icon_name),
        ]
        for path in try_paths:
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
                    return ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Error loading icon {path}: {e}")
        print(f"Icon {icon_name} not found. Returning default icon.")
        return None
        
        
    # def hide_all_content_frames(self):
        
    #     for frame in [self.dashboard_content_frame, self.stock_content_frame,
    #                  self.finance_content_frame, self.report_content_frame,
    #                  self.announcement_content_frame, self.users_content_frame,
    #                  self.setting_content_frame]:
    #         frame.grid_forget()
            
    def set_sidebar_button_active(self, active_button):
        
        buttons = [self.dashboard_content_frame, self.stock_content_frame,
                     self.finance_content_frame, self.report_content_frame,
                     self.announcement_content_frame, self.users_content_frame,
                     self.setting_content_frame]
        for button in buttons:
            if button == active_button:
                button.configure(fg_color="#F7F7F9", text_color="black", font=("Arial", 16, "bold"))
            else:
                button.configure(fg_color="transparent", text_color="black", font=("Arial", 16))
    
                
    
    def show_dashboard_content(self):
        # self.hide_all_content_frames()
        
        self.dashboard_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        
    def show_stock_content(self):
        # self.hide_all_content_frames()
        self.set_sidebar_button_active(self.stock_button) 
        for w in self.stock_content_frame.winfo_children():
            w.destroy()   
        self.stock_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
       
        
    def show_finance_content(self):
        # self.hide_all_content_frames()
        self.set_sidebar_button_active(self.finance_button)
        for w in self.finance_content_frame.winfo_children():
            w.destroy()
        self.finance_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        
    def show_report_content(self):
        # self.hide_all_content_frames()
        self.set_sidebar_button_active(self.report_button)
        
        for w in self.report_content_frame.winfo_children():
            w.destroy()
            
        self.report_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
          
        
    def show_announcement_content(self):
        # self.hide_all_content_frames()
        self.set_sidebar_button_active(self.announcement_button)
       
        for w in self.announcement_content_frame.winfo_children():
            w.destroy()
        
        self.announcement_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
     
    def show_users_content(self):
        # self.hide_all_content_frames()
        self.set_sidebar_button_active(self.user_button)
       
        for w in self.users_content_frame.winfo_children():
            w.destroy()   
        
        self.users_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        
    def show_setting_content(self):
        # self.hide_all_content_frames()
        self.set_sidebar_button_active(self.setting_button)
        
        for w in self.setting_content_frame.winfo_children():
            w.destroy()
       
        self.setting_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        
    def logout(self):
       
        import login
        login_app = login.LoginPage()
        login_app.mainloop()       
            
    
            
        

          
    
    
    
   
         
    def load_image(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((100, 100), Image.LANCZOS) 
            return ImageTk.PhotoImage(img)
        except FileNotFoundError:
            return None  
    
 
    
    def refresh_dashboard(self):
         self.update_summary_cards()
         
def get_users():
    try:
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute("""
            SELECT c.customer_id,c.first_name, c.last_name , l.role, c.status, l.is_locked
            FROM customers c
            JOIN login l ON c.customer_id=l.customer_id
        """)
        result=cursor.fetchall()
        conn.close()
        cursor.close()
        return result
    except Exception as e:
        print(f"DB  fetching stock error: {e}")
        return []
            


if __name__=="__main__":
    app=UserDashboard(customer_id=None, email=None)
    app.mainloop()
    