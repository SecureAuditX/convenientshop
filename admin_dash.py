import customtkinter as ctk
from PIL import Image, ImageTk
import os
import customtkinter as ctk
import os
from PIL import Image,ImageTk
import mysql.connector
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="zxcvbnm",
        port=3306,
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

class Dashboard(ctk.CTkFrame):
    def __init__(self, master, customer_id, email):
        super().__init__(master, fg_color="transparent") # Use transparent background for the container frame
        self.customer_id = customer_id
        self.email = email
        
        # Configure this frame's grid to host the UI elements
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Row 1 for the tabview (main content)
        

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", 
        bg_color="transparent", corner_radius=10)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame._parent_canvas.configure(width=1200, height=850)

        # grid setup
        for i in range(4):
             self.content_frame.grid_columnconfigure(i, weight=1)

        
        for r in range(5):
             self.content_frame.grid_rowconfigure(r, weight=0)
          
        #lbl
        self.dashboard_lbl=ctk.CTkLabel(self.content_frame,text="Dashboard",font=("Arial",22,"bold"),text_color="black")
        self.dashboard_lbl.grid(row=0,padx=(20,20),pady=(20,20),sticky="w",columnspan=4)
        
        self.back_lbl=ctk.CTkLabel(self.content_frame,text="Welcome back! Here's what's happening with your store today.",font=("Arial",17),text_color="grey")
        self.back_lbl.grid(row=0,padx=(30,20),pady=(80,20),sticky="w",columnspan=4)
        
        self.total_Revenue=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=200,height=130,corner_radius=20)
        self.total_Revenue.grid(row=2,column=0,padx=(10,10),pady=(10,10),sticky="ew")
        self.total_Revenue.grid_propagate(False)
        
        self.total_lbl=ctk.CTkLabel(self.total_Revenue,text="Total Revenue           $",text_color="grey",font=("Arial",14,"bold"))
        self.total_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")
        # val lbl idhr ayein gye
        self.total_val=ctk.CTkLabel(self.total_Revenue,text="$0.00",font=("Arial",15))
        self.total_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,10))
                 
        self.total_products=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=200,height=130,corner_radius=20)
        self.total_products.grid(row=2,column=1,padx=(10,10),pady=(10,10),sticky="ew")
        self.total_products.grid_propagate(False)
        
        self.total_lbl=ctk.CTkLabel(self.total_products,text="Total Products          📦",text_color="grey",font=("Arial",14,"bold"))
        self.total_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")
        # val lbl idhr ayein gye
        self.products_val=ctk.CTkLabel(self.total_products,text="0",font=("Arial",15))
        self.products_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,10))
                 
        self.total_sales=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=200,height=130,corner_radius=20)
        self.total_sales.grid(row=2,column=2,padx=(10,10),pady=(10,10),sticky="ew")
        self.total_sales.grid_propagate(False)
        
        self.total_lbl=ctk.CTkLabel(self.total_sales,text="Today's Sales          🛒",text_color="grey",font=("Arial",14,"bold"))
        self.total_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")
        # val lbl idhr ayein gye
        self.sales_val=ctk.CTkLabel(self.total_sales,text="$0.00",font=("Arial",15))
        self.sales_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,10))
                 
        self.active_users=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",width=170,height=130,corner_radius=20)
        self.active_users.grid(row=2,column=3,padx=(10,10),pady=(10,10),sticky="ew")
        self.active_users.grid_propagate(False)
        
        self.users_lbl=ctk.CTkLabel(self.active_users,text="Active Users   👥",text_color="grey",font=("Arial",14,"bold"))
        self.users_lbl.grid(row=0,padx=(20,20),pady=(20,10),sticky="w")         
        # val lbl idhr ayein gye
        self.users_val=ctk.CTkLabel(self.active_users,text="0",font=("Arial",15))
        self.users_val.grid(row=2,sticky="sw",padx=(30,10),pady=(10,10))          
        
        self.Revenue_exp=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",height=370,corner_radius=20)
        self.Revenue_exp.grid(row=3,column=0,padx=(20,10),pady=(10,10),sticky="nsew",columnspan=2)
        self.Revenue_exp.grid_propagate(False)
        self.Revenue_exp.grid_rowconfigure(2, weight=1)
        self.Revenue_exp.grid_columnconfigure(0, weight=1)
        
        self.revenue_exp_lbl=ctk.CTkLabel(self.Revenue_exp,text="Revenue & expenses",text_color="black",font=("Arial",16))
        self.revenue_exp_lbl.grid(row=0,padx=(20,10),pady=(20,10),sticky="nw")
        
        self.meow_lbl=ctk.CTkLabel(self.Revenue_exp,text="Monthly overview of your financial performance",text_color="grey",font=("Arial",16))
        self.meow_lbl.grid(row=0,padx=(30,10),pady=(40,10),sticky="nw")   
        
        self.topselling=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",height=370,corner_radius=20)
        self.topselling.grid(row=3,column=2,padx=(10,20),pady=(10,10),sticky="nsew",columnspan=2)
        self.topselling.grid_propagate(False)
        
        self.topselling_lbl=ctk.CTkLabel(self.topselling,text="Top Selling Products",text_color="black",font=("Arial",16))
        self.topselling_lbl.grid(row=0,padx=(20,10),pady=(20,10),sticky="nw")
        
        self.wao_lbl=ctk.CTkLabel(self.topselling,text="Best performing items this month",text_color="grey",font=("Arial",16))
        self.wao_lbl.grid(row=0,padx=(30,10),pady=(45,10),sticky="nw")      
        
        self.recent_activity=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",height=370,corner_radius=20)
        self.recent_activity.grid(row=4,column=0,padx=(20,10),pady=(10,10),sticky="nsew",columnspan=2)
        self.recent_activity.grid_propagate(False)
        
        self.recent_activity_lbl=ctk.CTkLabel(self.recent_activity,text="Recent Activity",text_color="black",font=("Arial",16))
        self.recent_activity_lbl.grid(row=0,padx=(20,10),pady=(20,10),sticky="nw")
        
        self.jiyo_lbl=ctk.CTkLabel(self.recent_activity,text="Latest updates and actions in your store",text_color="grey",font=("Arial",16))
        self.jiyo_lbl.grid(row=0,padx=(30,10),pady=(45,10),sticky="nw")       
        
        self.alerts=ctk.CTkFrame(self.content_frame,fg_color="white", border_width=2,border_color="lightgrey",height=370,corner_radius=20)
        self.alerts.grid(row=4,column=2,padx=(20,10),pady=(10,10),sticky="nsew",columnspan=2)
        self.alerts.grid_propagate(False)
        
        self.alerts_lbl=ctk.CTkLabel(self.alerts,text="Alerts & Notifications",text_color="black",font=("Arial",16))
        self.alerts_lbl.grid(row=0,padx=(20,10),pady=(20,10),sticky="nw")
        
        self.chl_lbl=ctk.CTkLabel(self.alerts,text="Important items requiring your attention",text_color="grey",font=("Arial",16))
        self.chl_lbl.grid(row=0,padx=(30,10),pady=(45,10),sticky="nw")
        
        self.refresh_dashboard()
        
    def load_summary_cards(self):
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("""
            SELECT COALESCE(SUM(total_sales),0) AS total_revenue
            FROM sales;
            """)
            result =cursor.fetchone()[0] or 0
            self.total_val.configure(text=f"${result:.2f}")
            
            cursor.execute("""SELECT COUNT(*) FROM product;""")
            products=cursor.fetchone()[0] or 0
            self.products_val.configure(text=f"{str(products)}")
            
            cursor.execute("""SELECT COALESCE(SUM(o.total)) AS todays_sales
                           FROM order_history o
                           WHERE DATE(o.time)=CURDATE();""")
            sales=cursor.fetchone()[0] or 0
            self.sales_val.configure(text=f"${sales:.2f}")
            
            cursor.execute("""SELECT COUNT(*) FROM customers WHERE status='active';
                           """)
            users=cursor.fetchone()[0] or 0
            self.users_val.configure(text=str(users))
            cursor.close()
            conn.close()
        except Exception as e:
            print({f"fetch from database error{e}"})
                      
    def revenue_chart(self):
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("""SELECT s.month, s.total_sales, s.expenses
                           FROM sales s
                           ORDER BY id;""")
            months = []
            revenues = [] 
            expenses = []
            data = cursor.fetchall()
            for month, total_sales, exp in data:
                 months.append(month)
                 revenues.append(float(total_sales))
                 expenses.append(float(exp))
              
            fig=Figure(figsize=(4,3),dpi=100)
            ax=fig.add_subplot(111)
            
            ax.plot(months,revenues,marker="o",label="Revenue")
            ax.plot(months,expenses,marker="o",label="Expenses")           
            
            ax.legend()
            ax.grid(True, linestyle="--",alpha=0.3)    
            
            canvas=FigureCanvasTkAgg(fig,master=self.Revenue_exp)
            canvas.draw()
            widget=canvas.get_tk_widget()
            widget.grid(row=2,column=0,columnspan=2,padx=(30,4),pady=(20,80),sticky="nsew")
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Fetching graph error: {e}")
            
    def top_product(self):
        # Clear existing rows before loading
        for w in self.topselling.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0: # Only clear rows below the headers (row 0)
                w.destroy()
        
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("""SELECT product,quantity_sold,revenue
                           FROM product_performance
                           ORDER BY quantity_sold DESC
                           LIMIT 5;""")
            rows=cursor.fetchall()
            
            if not rows:
                ctk.CTkLabel(self.topselling, text="No top products data found.", text_color="grey").grid(row=1, column=0, columnspan=4, padx=20, pady=20, sticky="w")
                return
            
            for i, (name, qty, rev) in enumerate(rows, start=1):
                # Using a sub-frame for better layout control
                product_frame = ctk.CTkFrame(self.topselling, fg_color="transparent")
                product_frame.grid(row=i, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
                product_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

                rank_lbl = ctk.CTkLabel(product_frame, text=str(i), font=("Arial", 15), width=30)
                rank_lbl.grid(row=0, column=0, padx=(10, 0), sticky="w")

                name_lbl = ctk.CTkLabel(product_frame, text=name, font=("Arial", 15), anchor="w")
                name_lbl.grid(row=0, column=1, padx=5, sticky="w")

                sales_lbl = ctk.CTkLabel(product_frame, text=f"{qty} sales", font=("Arial", 14),text_color="grey", anchor="w")
                sales_lbl.grid(row=0, column=2, padx=5, sticky="w")

                revenue_lbl = ctk.CTkLabel(product_frame, text=f"${rev:.2f}", font=("Arial", 15, "bold"), anchor="e")
                revenue_lbl.grid(row=0, column=3, padx=10, sticky="e")
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"DB error: {e}")
    
    def load_recent_activity(self):
        # Clear existing rows before loading
        for w in self.recent_activity.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()
                
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("SELECT products,last_restocked FROM stock_management ORDER BY last_restocked DESC LIMIT 5;")
            rows=cursor.fetchall()
            
            if not rows:
                ctk.CTkLabel(self.recent_activity, text="No recent stock activity found.", text_color="grey").grid(row=1, column=0, padx=20, pady=20, sticky="w")
                return
                
            for i, (name, last_restocked) in enumerate(rows, start=1):
                activity_frame = ctk.CTkFrame(self.recent_activity, fg_color="transparent")
                activity_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
                activity_frame.grid_columnconfigure(0, weight=1)
                activity_frame.grid_columnconfigure(1, weight=1)
                
                name_lbl = ctk.CTkLabel(activity_frame, text=f"Restock: {name}", font=("Arial", 15), anchor="w")
                name_lbl.grid(row=0, column=0, padx=10, pady=(5, 5), sticky="w")

                time_lbl = ctk.CTkLabel(
                activity_frame,
                text=str(last_restocked),
                font=("Arial", 13),
                text_color="grey",
                anchor="e"
                )
                time_lbl.grid(row=0, column=1, padx=10, pady=(5, 5), sticky="e")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"DB error: {e}")
                   
    def load_alerts(self):
        # Clear existing rows before loading
        for w in self.alerts.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()
                
        try:
            conn=get_db_connection()
            cursor=conn.cursor()
            cursor.execute("""SELECT p.product_name, p.stock_quantity
                             FROM product p
                             WHERE p.stock_quantity < 10
                             ORDER BY p.stock_quantity ASC
                             LIMIT 5;
                            """)
            rows=cursor.fetchall()
            
            if not rows:
                ctk.CTkLabel(self.alerts, text="No critical low-stock alerts.", text_color="green").grid(row=1, column=0, padx=20, pady=20, sticky="w")
                return

            for i, (name, st_qty) in enumerate(rows, start=1):
                alert_frame = ctk.CTkFrame(self.alerts, fg_color="#FEE4E3", corner_radius=5)
                alert_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
                alert_frame.grid_columnconfigure(0, weight=1)
                alert_frame.grid_columnconfigure(1, weight=1)
                
                name_lbl = ctk.CTkLabel(alert_frame, text=name, font=("Arial", 15), text_color="#C62828", anchor="w")
                name_lbl.grid(row=0, column=0, padx=10, pady=(5, 5), sticky="w")

                qty_lbl = ctk.CTkLabel(
                alert_frame,
                text=f"Only {st_qty} left!",
                font=("Arial", 13, "bold"),
                text_color="#C62828",
                anchor="e"
                )
                qty_lbl.grid(row=0, column=1, padx=10, pady=(5, 5), sticky="e")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"DB error: {e}")

    
    def load_image(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((100, 100), Image.LANCZOS) 
            return ImageTk.PhotoImage(img)
        except FileNotFoundError:
            return None 
       
    def refresh_dashboard(self):
         self.load_summary_cards()
         self.revenue_chart()
         self.top_product()
         self.load_recent_activity()
         self.load_alerts()