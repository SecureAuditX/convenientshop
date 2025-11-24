from db_file import db
import customtkinter as ctk
from PIL import Image, ImageTk
import datetime
import traceback
import decimal
import os
from setting import App as SettingsApp
from history import App as HistoryApp
from checkout import Checkout as Checkout
from Payment import Payment as Payment
from category import (
    Category, 
    get_all_categories, 
    category_load_image, 
    Get_products_by_category 
)

# Images path
IMAGE_BASE_DIR = r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop\images"

CARD_COLORS = [
    "#7DABDE",  # Blue
    "#87D7E0",  # Cyan
    "#EA7BBE",  # Pink
    "#BCEAA5",  # Light Green
    "#B9A5EA",  # Purple
    "#EAA5A6"   # Light Red
    ]


def image_path_join(*parts):
    """Return normalize absolute path for images"""
    candidate = os.path.join(*parts)
    if os.path.isabs(candidate):
        return os.path.normpath(candidate)
    # Trying IMAGE_BASE_DIR
    candidate2 = os.path.join(IMAGE_BASE_DIR, *parts[1:]) if len(parts) > 1 else os.path.join(IMAGE_BASE_DIR, parts[0])
    if os.path.exists(candidate2):
        return os.path.normpath(candidate2)
    base = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(base, *parts))


class UserDashboard(ctk.CTk):
    def __init__(self, customer_id, email):
        super().__init__()
        self.customer_id = customer_id
        self.logged_in_email = email
        
        
        # Window Configure
        self.title("Customer Dashbaord")
        self.geometry("1200x800")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        
         # Configure Grid Layout for Main Window (Sidebar + Main Content)
        self.grid_columnconfigure(0, weight=0) # Sidebar column - fixed width
        self.grid_columnconfigure(1, weight=1) # Main content column - expands
        self.grid_rowconfigure(0, weight=1)    # Full height
        
        # Product_id -> quantity
        self.cart_cache = {}
        
        # --- Sidebar Panel ---
        
        #sidebar frame (left panel)
        self.sidebar_frame = ctk.CTkFrame(self, fg_color="#D8DBF7", corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        # increase number of rows
        for i in range(0, 12):
            self.sidebar_frame.grid_rowconfigure(i, weight=0)  # give padding rows near bottom
        self.sidebar_frame.grid_rowconfigure(11, weight=1) # space before logout
        
        # User Profile
        self.profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.profile_frame.grid(row=0, column=0, padx=10, pady=20, sticky="ew")
        
        # Load profile icon
        try:
            profile_icon_path = image_path_join(os.path.dirname(__file__), "profile.png")
            if not os.path.exists(profile_icon_path):
                profile_icon_path = os.path.join(IMAGE_BASE_DIR, "profile.png")
            profile_image = Image.open(profile_icon_path).resize((80, 80), Image.LANCZOS)
            self.profile_ctk_image = ImageTk.PhotoImage(profile_image)
            
            self.profile_label = ctk.CTkLabel(self.profile_frame, image=self.profile_ctk_image, text="")
            self.profile_label.grid(row=0, column=0, padx=10, pady=5)
        
        except Exception:
            # Gracefull fallback
            self.profile_label = ctk.CTkLabel(self.profile_frame, text="👤", font=("Arial", 40))
            self.profile_label.grid(row=0, column=0, padx=10, pady=5)
            
        self.username_label = ctk.CTkLabel(self.profile_frame, text="Username", font=("Arial", 18, "bold"), text_color="black")
        self.username_label.grid(row=1, column=0, padx=30, pady=5)
        
        self.load_customer_name()
            
        # Navigation Buttons
        self.dashboard_button = ctk.CTkButton(self.sidebar_frame, text="Home",
                                              fg_color="transparent", text_color="black",
                                              hover_color="#D7D2F4", font=("Arial", 16, "bold"),
                                              anchor="w", image=self.load_icon("home.png", 20),
                                              compound="left", command=self.show_dashboard_content,
                                              width=150, height=50) 
        self.dashboard_button.grid(row=2, column=0, padx=10, pady=8, sticky="ew")   
    
        self.categories_button = ctk.CTkButton(self.sidebar_frame, text="Categories", 
                                               fg_color="transparent", text_color="black",
                                               hover_color="#D7D2F4", font=("Arial", 16), 
                                               anchor="w", image=self.load_icon("category.png", 20), 
                                               compound="left", command=self.show_categories_content,
                                               width=150, height=50)
        self.categories_button.grid(row=3, column=0, sticky="ew", pady=8, padx=10) 
        
        self.checkout_button = ctk.CTkButton(self.sidebar_frame, text="Checkout", 
                                             fg_color="transparent", text_color="black", 
                                             hover_color="#D7D2F4", font=("Arial", 16), 
                                             anchor="w", image=self.load_icon("checkout.png", 20),
                                             compound="left", command=self.show_checkout_content,
                                             width=150, height=50)
        self.checkout_button.grid(row =4, column=0, sticky="ew", pady=8, padx=10)
        
        self.payment_button = ctk.CTkButton(self.sidebar_frame, text="Payment", 
                                            fg_color="transparent", text_color="black",
                                            hover_color="#D7D2F4", font=("Arial", 16), 
                                            anchor="w", image=self.load_icon("payment.png", 20), 
                                            compound="left", command=self.show_payment_content,
                                            width=150, height=50)
        self.payment_button.grid(row=5, column=0, sticky="ew", pady=8, padx=10)

        self.history_button = ctk.CTkButton(self.sidebar_frame, text="History", 
                                            fg_color="transparent", text_color="black",
                                            hover_color="#D7D2F4", font=("Arial", 16), 
                                            anchor="w", image=self.load_icon("history.png", 20), 
                                            compound="left", command=self.show_history_content,
                                            width=150, height=50)
        self.history_button.grid(row=6, column=0, sticky="ew", pady=8, padx=10)

        self.setting_button = ctk.CTkButton(self.sidebar_frame, text="Setting", 
                                            fg_color="transparent", text_color="black",
                                            hover_color="#D7D2F4", font=("Arial", 16), 
                                            anchor="w", image=self.load_icon("setting.png", 20), 
                                            compound="left", command=self.show_setting_content,
                                            width=150, height=50)
        self.setting_button.grid(row=7, column=0, sticky="ew", pady=8, padx=10)   
        
        #  Logout Button 
        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Logout", 
                                           fg_color="transparent", text_color="black",
                                           hover_color="#D7D2F4", font=("Arial", 16), 
                                           anchor="w", image=self.load_icon("exit.png", 20), 
                                           compound="left", command=self.logout,
                                           width=150, height=50)
        self.logout_button.grid(row=15, column=0, sticky="ew", pady=(10, 20), padx=10)

        # Sidebar ends
        
        # Main Content Area (Right panel)
        self.main_content_area = ctk.CTkFrame(self, fg_color="#F7F7F7", corner_radius=0)
        self.main_content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content_area.grid_columnconfigure(0, weight=1) # Center content horizontally
        self.main_content_area.grid_rowconfigure(0, weight=1)

        # Content Frames for different sections (Dashboard, Categories, etc.) 
        self.dashboard_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.category_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.checkout_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.payment_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.history_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.setting_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        
        self.search_var = ctk.StringVar() 
        # initially show the dashboard content
        self.show_dashboard_content()
    
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


    def load_product_image(self, filename, size=(100, 100)):
        """
        Load product images from IMAGE_BASE_DIR 
        """
       
        candidates = []
        if os.path.isabs(filename):
            candidates.append(filename)
        else:
            candidates.append(os.path.join(IMAGE_BASE_DIR, filename))
            candidates.append(os.path.join(os.path.dirname(__file__), "images", filename))
            candidates.append(os.path.join(os.path.dirname(__file__), filename))

        for path in candidates:
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
                    return ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Error loading product image {path}: {e}")
        return None


    # Ui helpers - Hide/show frames
    def hide_all_content_frames(self):
        """Hides all content frames."""
        for frame in [self.dashboard_content_frame, self.category_content_frame,
                     self.checkout_content_frame, self.payment_content_frame,
                     self.history_content_frame, self.setting_content_frame]:
            frame.grid_forget()
            
    
    def set_sidebar_button_active(self, active_button):
        """Sets the active state for sidebar buttons."""
        buttons = [self.dashboard_button, self.categories_button, self.checkout_button,
                   self.payment_button, self.history_button, self.setting_button]
        for button in buttons:
            if button == active_button:
                button.configure(fg_color="#F7F7F9", text_color="black", font=("Arial", 16, "bold"))
            else:
                button.configure(fg_color="transparent", text_color="black", font=("Arial", 16))
        
    
    # Content Display Functions
    def show_dashboard_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.dashboard_button)
        self.dashboard_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.render_dashboard_ui(self.dashboard_content_frame)

    
    def show_categories_content(self):
        self.hide_all_content_frames()
        # Assuming your Categories sidebar button is named self.categories_button
        self.set_sidebar_button_active(self.categories_button) 

        for w in self.category_content_frame.winfo_children():
            w.destroy()
            
        # 2. Make the category content frame visible
        self.category_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        category_ui = Category(
            parent_frame=self.category_content_frame,
            card_colors=CARD_COLORS, # CARD_COLORS is already defined in user_dashboard.py
            get_all_categories_func=get_all_categories, 
            category_load_image_func=category_load_image, 
            get_products_by_category_func=Get_products_by_category,
            customer_id=self.customer_id,
            email=self.logged_in_email
        )
        category_ui.pack(expand=True, fill="both", padx=0, pady=0)
    
    def show_checkout_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.checkout_button)
        
        # Clear old widgets
        for w in self.checkout_content_frame.winfo_children():
            w.destroy()
            
        self.checkout_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Instantiate and place the Checkout UI
        checkout_ui = Checkout(self.checkout_content_frame, customer_id=self.customer_id, email=self.logged_in_email)
        checkout_ui.pack(expand=True, fill="both", padx=0, pady=0) 
        
    def show_payment_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.payment_button)

        # Clear old widgets
        for w in self.payment_content_frame.winfo_children():
            w.destroy()
            
        self.payment_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Instantiate and place the Payment UI
        payment_ui = Payment(self.payment_content_frame, customer_id=self.customer_id, email=self.logged_in_email)
        payment_ui.pack(expand=True, fill="both", padx=0, pady=0)

    def show_history_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.history_button)
        
        # Clear old widgets first
        for w in self.history_content_frame.winfo_children():
            w.destroy()

        # Ensure history_content_frame is visible
        self.history_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Instantiate and place the History UI
        history_ui = HistoryApp(self.history_content_frame, customer_id=self.customer_id, email=self.logged_in_email) 
        history_ui.pack(expand=True, fill="both", padx=0, pady=0) 

    def show_setting_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.setting_button)
        
        # Clear old widgets first
        for w in self.setting_content_frame.winfo_children():
            w.destroy()
            
        # Ensure setting_content_frame is visible
        self.setting_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Instantiate and place the Settings UI
        settings_ui = SettingsApp(self.setting_content_frame, customer_id=self.customer_id, email=self.logged_in_email)
        settings_ui.pack(expand=True, fill="both", padx=0, pady=0) 
        
    def logout(self):
        """Handles user logout."""
        # Close the current dashboard window
        self.destroy()
        import login
        login_app = login.LoginPage()
        login_app.mainloop()       
        
        
    # Start of dashboard content implementation
    def render_dashboard_ui(self, parent_frame):
        """
        Renders the specific UI elements for the main dashboard content.
        """
        # Clear existing widgets from the dashboard content frame
        for widget in parent_frame.winfo_children():
            widget.destroy()

        #  Top Search Bar and User Icon 
        top_bar_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        top_bar_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        top_bar_frame.grid_columnconfigure(0, weight=1) # Search bar expands
        top_bar_frame.grid_columnconfigure(1, weight=0) # User icon fixed size

        
        # Create a frame to hold both the icon and the entry
        search_frame = ctk.CTkFrame(top_bar_frame, fg_color="transparent") # Use transparent for better look
        search_frame.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=5) 

        # 1. Add the "Search" label
        search_text_label = ctk.CTkLabel(search_frame, text="Search ", font=("Arial", 16, "bold"), text_color="black")
        search_text_label.grid(row=0, column=0, padx=(0, 5)) 

        # Load the search icon
        search_icon = self.load_icon("search.png", 20)

        # Add the icon to the frame using CTkLabel
        self.search_icon_label = ctk.CTkLabel(search_frame, image=search_icon, text="")
        self.search_icon_label.grid(row=0, column=1, padx=(0, 0)) 

        # Create the entry field and place it next to the icon
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search", width=800, height=40, font=("Arial", 16),
                             fg_color="#9DA6F9", border_color="#D1D1DF", text_color="white",
                             placeholder_text_color="white", corner_radius=20, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=2, padx=(10, 0)) 
        


        #  Announcement Section 
        self.announcement_label = ctk.CTkLabel(parent_frame, text="Announcement", font=("Arial", 22, "bold"), text_color="black")
        self.announcement_label.grid(row=1, column=0, sticky="w", padx=20, pady=(2, 2))

        self.announcement_categories_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.announcement_categories_frame.grid(row=2, column=0, sticky="ew", pady=(0, 2))

        categories = [
            {"name": "Bakeries", "icon": "bakeries.png"},
            {"name": "Drinks", "icon": "drinks.png"},
            {"name": "Vegetables", "icon": "vegetables.png"},
            {"name": "Fruits", "icon": "fruits.png"},
            {"name": "Snacks", "icon": "snacks.png"},
        ]
         
        # Category cards container (horizontal)
        cat_row_frame = ctk.CTkFrame(self.announcement_categories_frame, fg_color="transparent")
        cat_row_frame.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        for i, category in enumerate(categories):
            card = self.create_category_card(cat_row_frame, category["name"], category["icon"])
            card.grid(row=0, column=i, padx=10, pady=2)
       

        
         # Fetch announcement items from DB and render them
        announcements = self.fetch_announcements_from_db()
        
        # Render announcement items (max 5 to mimic UI)
        for i, ann in enumerate(announcements[:6]):
            # each announcement card shows product image, name, discount price and deadline
            card = ctk.CTkFrame(self.announcement_products_frame, width=280, height=280, fg_color="#F0F4FF", corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=40)
            card.grid_propagate(False)
            # product image
            prod_img = self.load_product_image(ann.get("image_url") or ann.get("image") or "", size=(200,200))
            if prod_img:
                img_lbl = ctk.CTkLabel(card, image=prod_img, text="")
                img_lbl.image = prod_img
                img_lbl.grid(row=0, column=0, pady=(2,2))

            else:
                ctk.CTkLabel(card, text="🛍️", font=("Arial", 30)).grid(row=0, column=0, pady=(5,2))
            # name / discount
            ctk.CTkLabel(card, text=ann.get("product_name", "Item"), 
                         font=("Arial", 12, "bold"), text_color="#4F46E5").grid(row=1, column=0)
            ctk.CTkLabel(card, text=f"Now: {ann.get('discount_price', '0.00')}", font=("Arial", 12)).grid(row=2, column=0)
            
            deadline = ann.get("discount_deadline")
            if isinstance(deadline, (datetime.date, datetime.datetime)):
                deadline_text = deadline.strftime("%Y-%m-%d")
            else:
                deadline_text = str(deadline)
            ctk.CTkLabel(card, text=f"Until: {deadline_text}", font=("Arial", 10), text_color="#888888").grid(row=3, column=0)
       
            
         # --- Popular Items Section ---
        self.popular_items_label = ctk.CTkLabel(parent_frame, text="Popular Items", font=("Arial", 22, "bold"), text_color="black")
        self.popular_items_label.grid(row=4, column=0, sticky="w",padx =20, pady=(2, 2))

        self.popular_items_scroll_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent", orientation="horizontal", height=175)
        self.popular_items_scroll_frame.grid(row=5, column=0, sticky="ew", pady=(0, 2))

        # Query DB for popular items (product.is_popular = 1)
        popular_items = self.fetch_products_by_flag(flag_column="is_popular", limit=12)
        
        # fallback sample from your original code if DB empty
        if not popular_items:
            popular_items = [
                {"product_id": 1, "product_name": "Bread", "price":"6.99", "weight":"2.5kg", "product_image":"bread.png"},
                {"product_id": 2, "product_name": "Egg", "price":"12.99", "weight":"4kg", "product_image":"egg.png"},
                {"product_id": 3, "product_name": "Coke", "price":"2.90", "weight":"0.3kg", "product_image":"coke.png"},
                {"product_id": 4, "product_name": "Meat", "price":"128.98", "weight":"9kg", "product_image":"meat.png"},
                {"product_id": 5, "product_name": "Oil", "price":"94.98", "weight":"12kg", "product_image":"oil.png"},
                {"product_id": 6, "product_name": "Chips", "price":"0.98", "weight":"0.1kg", "product_image":"chips.png"},
            ]

        for i, item in enumerate(popular_items[:12]):
            # item must supply product_id for cart insertion
            self.create_item_card(self.popular_items_scroll_frame,
                                  name=item.get("product_name"),
                                  weight=item.get("weight", ""),
                                  price=item.get("price"),
                                  image_filename=item.get("image_url"),
                                  product_id=item.get("product_id")).grid(row=0, column=i, padx=10, pady=2)

        # --- New Items Section ---
        self.new_items_label = ctk.CTkLabel(parent_frame, text="New Items", font=("Arial", 22, "bold"), text_color="black")
        self.new_items_label.grid(row=6, column=0, sticky="w", padx=20, pady=(2, 2))

        self.new_items_scroll_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent", orientation="horizontal", height=175)
        self.new_items_scroll_frame.grid(row=7, column=0, sticky="ew")

        new_items = self.fetch_products_by_flag(flag_column="is_new", limit=12)
        
        # Fallback
        if not new_items:
            new_items = [
                {"product_id": 7, "product_name":"Indomie", "price":"1.56", "weight":"0.9kg", "image_url":"indomie.png"},
                {"product_id": 8, "product_name":"Monster", "price":"3.99", "weight":"1kg", "image_url":"monster.png"},
                {"product_id": 9, "product_name":"Yogurt", "price":"39.99", "weight":"6kg", "image_url":"yogurt.png"},
                {"product_id": 1, "product_name":"Bread", "price":"6.99", "weight":"2.5kg", "image_url":"bread.png"},
            ]

        for i, item in enumerate(new_items[:12]):
            self.create_item_card(self.new_items_scroll_frame,
                                  name=item.get("product_name"),
                                  weight=item.get("weight", ""),
                                  price=item.get("price"),
                                  image_filename=item.get("image_url"),
                                  product_id=item.get("product_id")).grid(row=0, column=i, padx=10, pady=5)

            
    # DB Query Functions
    def fetch_announcements_from_db(self):
        """
        Fetch announcement rows joined with product info.
        """
        q = """
            SELECT a.annou_id, a.name as ann_name, a.discount_price, a.discount_deadline,
                   p.product_id, p.product_name, p.sku, p.price, p.image_url
            FROM announcement a
            LEFT JOIN product p ON a.product_id = p.product_id
            ORDER BY a.annou_id DESC
            LIMIT 10
        """
        rows = db.fetchall(q)
        results = []
        for r in rows:
            results.append({
                "annou_id": r.get("annou_id"),
                "name": r.get("ann_name"),
                "discount_price": r.get("discount_price"),
                "discount_deadline": r.get("discount_deadline"),
                "product_id": r.get("product_id"),
                "product_name": r.get("product_name"),
                "image_url": r.get("image_url")
            })
        return results

    def fetch_products_by_flag(self, flag_column="is_popular", limit=12):
        # Validate flag_column to avoid SQL injection (only allow certain columns)
        if flag_column not in ("is_popular", "is_new"):
            flag_column = "is_popular"
            
        q = f"""
            SELECT product_id, product_name, price, stock_quantity, sku, discount, {flag_column}, image_url
            FROM product
            WHERE {flag_column} = 1
            ORDER BY product_id DESC
            LIMIT %s
        """
        rows = db.fetchall(q, (limit,))
        products = []
        
        for r in rows:
            # Use the correct column names to access the dictionary
            image_path = r['image_url'] or ""  # Ensure correct key usage (image_url instead of index-based access)
            image_filename = image_path.replace("images/", "").replace("\\", "/").split("/")[-1]
            image_path = os.path.join(IMAGE_BASE_DIR, image_filename)

            products.append({
                "product_id": r['product_id'],  # Access product_id by column name
                "product_name": r['product_name'],  # Access product_name by column name
                "price": str(r['price']) if r['price'] is not None else "0.00",  # Price formatting
                "weight": "",  # Empty weight for now
                "image_url": image_path  # Correct image URL path
            })
        return products


    
    def create_category_card(self, parent, name, icon_filename):
        """Creates a single category card widget."""
        card = ctk.CTkFrame(parent, width=150, height=150, fg_color="#E0DDF0", corner_radius=10)
        card.pack_propagate(False) # Prevent card from resizing to content

        icon = self.load_icon(icon_filename, 80) # Icons for categories
        if icon:
            icon_label = ctk.CTkLabel(card, image=icon, text="")
            icon_label.image = icon
            icon_label.pack(pady=(10, 5))
        else:
            icon_label = ctk.CTkLabel(card, text="📦", font=("Arial", 30))
            icon_label.pack(pady=(10, 5))

        name_label = ctk.CTkLabel(card, text=name, font=("Arial", 14, "bold"), text_color="black")
        name_label.pack()
        return card
    
    
    def create_item_card(self, parent, name, weight, price, image_filename, product_id=None):
        """
        Creates a single item card widget.
        """
        # 1. FIX: Increase card height (e.g., from 160 to 200) to allow space for all text.
        card = ctk.CTkFrame(parent, width=160, height=200, fg_color="white", corner_radius=10, border_color="#E0DDF0", border_width=1)
        card.pack_propagate(False)

        # Item image (use load_product_image which searches IMAGE_BASE_DIR)
        item_image = self.load_product_image(image_filename or "", size=(100,100))
        if item_image:
            image_label = ctk.CTkLabel(card, image=item_image, text="")
            image_label.image = item_image
            # Consider reducing pady to save vertical space
            image_label.pack(pady=(5, 5)) 
        else:
            image_label = ctk.CTkLabel(card, text="🛒", font=("Arial", 40))
            image_label.pack(pady=(5, 5))

        # Name aligned to the left
        name_label = ctk.CTkLabel(card, text=name, font=("Arial", 14, "bold"), text_color="black", anchor="w")
        # 2. FIX: Reduce vertical padding (pady) around the name label
        name_label.pack(fill="x", padx=10, pady=(0, 0)) 

        bottom_frame = ctk.CTkFrame(card, fg_color="transparent", height=40)
        bottom_frame.pack(fill="x", padx=2, pady=(2, 2)) # Added a small pady at the bottom to ensure it's not glued to the edge
        bottom_frame.pack_propagate(False)

        # Left side: weight and price in vertical layout
        left_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        left_frame.pack(side="left", anchor="w", padx=5) # Added padx to align better with the name label

        weight_label = ctk.CTkLabel(left_frame, text=weight, font=("Arial", 12), text_color="#888888", anchor="w")
        weight_label.pack(fill="x", padx=2, pady=(0, 0)) # Reduced vertical padding

        # Ensure price is always displayed with 2 decimals
        try:
            price_val = float(price)
            price_text = f"${price_val:,.2f}"
        except Exception:
            price_val = price
            price_text = str(price)

        price_label = ctk.CTkLabel(left_frame, text=price_text, font=("Arial", 14, "bold"), text_color="black", anchor="w")
        price_label.pack(side="left", anchor="e")

        add_to_cart_button = ctk.CTkButton(bottom_frame, text="➕", width=34, height=34, corner_radius=17,
                                        fg_color="#FFFFFF", hover_color="#F0FFF0", text_color="black",
                                        font=("Arial", 18, "bold"),
                                        command=lambda pid=product_id, pname=name, pprice=price_val: self.on_add_to_cart(pid, pname, pprice))
        add_to_cart_button.pack(side="right", anchor="e", padx=2)

        return card
    
    
    def on_add_to_cart(self, product_id, product_name, price_text):

        # Convert price
        try:
            price_val = float(str(price_text).replace("$", "").replace(",", ""))
        except:
            print("Invalid price:", price_text)
            return

        # Ensure customer_id exists
        if not self.customer_id:
            print("ERROR: No customer_id assigned")
            return

        try:
            conn = db.DB_Connection()
            cursor = conn.cursor()

            #  Check if item already exists in active cart
            cursor.execute("""
                SELECT cart_id, quantity
                FROM check_out
                WHERE product_id = %s
                AND customer_id = %s
                AND total IS NULL
            """, (product_id, self.customer_id))

            row = cursor.fetchone()

            #  INSERT new row if item not found
            if row is None:
                cursor.execute("""
                    INSERT INTO check_out 
                    (product_id, customer_id, items, price, quantity, item_total)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (product_id, self.customer_id,
                    product_name, price_val, 1, price_val))

                print("Inserted into cart:", product_name)

            #  UPDATE existing row
            else:
                cart_id, qty = row
                new_qty = qty + 1
                new_total = new_qty * price_val

                cursor.execute("""
                    UPDATE check_out
                    SET quantity = %s,
                        item_total = %s
                    WHERE cart_id = %s
                    AND customer_id = %s
                    AND total IS NULL
                """, (new_qty, new_total, cart_id, self.customer_id))

                print("Updated quantity in cart:", product_name)

            conn.commit()

        except Exception as e:
            print("Dashboard cart insert error:", e)

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass

        # Show small popup (optional)
        try:
            self.show_added_to_cart_toast(product_name)
        except:
            pass
     
        
    def show_added_to_cart_toast(self, product_name):
        
        toast = ctk.CTkLabel(self, text=f"Added {product_name} to cart", fg_color="#E8FFF0", text_color="#1F7A2D", corner_radius=8)
        
        x = self.search_entry.winfo_rootx() - self.winfo_rootx()
        y = self.search_entry.winfo_rooty() - self.winfo_rooty() + self.search_entry.winfo_height() + 5

        # place top middle
        toast.place(x=x, y=y)
        # hide after 1.2s (simple mechanism)
        self.after(1200, toast.destroy)
        
    
    def render_checkout_preview(self, parent):
       
        for w in parent.winfo_children():
            w.destroy()

        heading = ctk.CTkLabel(parent, text="Checkout (Cart) Preview", font=("Arial", 22, "bold"))
        heading.pack(pady=10, anchor="w")

        # Table header
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=10)
        ctk.CTkLabel(header_frame, text="Item", width=30, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Qty", width=10).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Price", width=10).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Total", width=10).pack(side="left", padx=5)

        # fetch current cart rows (customer_id IS NULL)
        q = """SELECT c.cart_id, c.product_id, c.items, c.quantity, c.price, c.item_total
               FROM check_out c
               WHERE c.customer_id IS NULL
               ORDER BY c.date DESC
               LIMIT 50"""
        rows = db.fetchall(q)

        # If DB fetch fails or empty, show local cache items
        if not rows:
            # fallback local cache representation; show product_id keys
            if self.cart_cache:
                for pid, qty in self.cart_cache.items():
                    row_frame = ctk.CTkFrame(parent, fg_color="transparent")
                    row_frame.pack(fill="x", padx=10, pady=5)
                    ctk.CTkLabel(row_frame, text=str(pid), width=30, anchor="w").pack(side="left", padx=5)
                    ctk.CTkLabel(row_frame, text=str(qty), width=10).pack(side="left", padx=5)
                    ctk.CTkLabel(row_frame, text="-", width=10).pack(side="left", padx=5)
                    ctk.CTkLabel(row_frame, text="-", width=10).pack(side="left", padx=5)
            else:
                ctk.CTkLabel(parent, text="Cart is empty", font=("Arial", 14)).pack(pady=20)
            return

        for r in rows:
            row_frame = ctk.CTkFrame(parent, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row_frame, text=str(r.get("items") or r.get("product_id")), width=30, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row_frame, text=str(r.get("quantity") or "-"), width=10).pack(side="left", padx=5)
            price_display = f"${float(r.get('price') or 0.0):,.2f}"
            ctk.CTkLabel(row_frame, text=price_display, width=10).pack(side="left", padx=5)
            total_display = f"${float(r.get('item_total') or 0.0):,.2f}"
            ctk.CTkLabel(row_frame, text=total_display, width=10).pack(side="left", padx=5)
       
     # Get username from the database
    def load_customer_name(self):
        try:
            if not self.customer_id:
                self.username_label.configure(text="Guest")
                return
            
            q = "SELECT first_name, last_name FROM customers WHERE customer_id = %s"
            result = db.fetchone(q, (self.customer_id,))
            
            if result:
                full_name = f"{result['first_name']} {result['last_name']}"
                self.username_label.configure(text=full_name)
                
            else:
                self.username_label.configure(text="User")
                
        except Exception as e:
            print("Error loading customer name: ", e)
            self.username_label.configure(text="User")
    

if __name__ == "__main__":
    app = UserDashboard(customer_id=None, email=None)
    app.mainloop()    