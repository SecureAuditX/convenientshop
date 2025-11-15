from db_file import Database
import customtkinter as ctk
from PIL import Image, ImageTk
import datetime
import traceback
import decimal
import os

# Database Connection
db = Database()
connection = db.DB_Connection()

# Images path
IMAGE_BASE_DIR = r"C:\XFiles\CodingFile\Python\Desktop_App\ConvenientShop\images"

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
    def __init__(self):
        super().__init__()
        
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

        # Content Frames for different sections (Dashboard, Categories, etc.) 
        self.dashboard_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.categories_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
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
        # Accept full paths, too
        # Try multiple likely locations
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
        for frame in [self.dashboard_content_frame, self.categories_content_frame,
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
        self.set_sidebar_button_active(self.categories_button)
        self.categories_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        # Placeholder for categories UI
        label = ctk.CTkLabel(self.categories_content_frame, text="Categories Content (Your team will implement)", font=("Arial", 24))
        label.pack(expand=True, fill="both")

    def show_checkout_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.checkout_button)
        self.checkout_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        # Placeholder for checkout UI
        # We'll show a live preview of cart contents here (simple table)
        self.render_checkout_preview(self.checkout_content_frame)

    def show_payment_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.payment_button)
        self.payment_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        # Placeholder for payment UI
        label = ctk.CTkLabel(self.payment_content_frame, text="Payment Content (Your team will implement)", font=("Arial", 24))
        label.pack(expand=True, fill="both")

    def show_history_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.history_button)
        self.history_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        # Placeholder for history UI
        label = ctk.CTkLabel(self.history_content_frame, text="History Content (Your team will implement)", font=("Arial", 24))
        label.pack(expand=True, fill="both")

    def show_setting_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.setting_button)
        self.setting_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        # Placeholder for settings UI
        label = ctk.CTkLabel(self.setting_content_frame, text="Setting Content (Your team will implement)", font=("Arial", 24))
        label.pack(expand=True, fill="both") 
        
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
        search_frame = ctk.CTkFrame(top_bar_frame)
        search_frame.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=10)  # Place frame with padding

        # Load the search icon
        search_icon = self.load_icon("search.png", 20)

        # Add the icon to the frame using CTkLabel
        self.search_icon_label = ctk.CTkLabel(search_frame, image=search_icon, text="")
        self.search_icon_label.grid(row=0, column=0, padx=(10, 0))  # Place icon in frame

        # Create the entry field and place it next to the icon
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search", width=870, height=40, font=("Arial", 16),
                                 fg_color="#9DA6F9", border_color="#D1D1DF", text_color="white",
                                 placeholder_text_color="white", corner_radius=20, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, padx=(10, 0))  # Place entry next to the icon

        


        #  Announcement Section 
        self.announcement_label = ctk.CTkLabel(parent_frame, text="Announcement", font=("Arial", 22, "bold"), text_color="black")
        self.announcement_label.grid(row=1, column=0, sticky="w", padx=20, pady=(5, 5))

        self.announcement_categories_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.announcement_categories_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        # We will show two rows: first the category cards (static), second the announcement product cards (from DB)
        # Category cards (kept from your original design)
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
            card.grid(row=0, column=i, padx=10, pady=5)
       

        
         # Fetch announcement items from DB and render them
        announcements = self.fetch_announcements_from_db()
        
        # Render announcement items (max 5 to mimic UI)
        for i, ann in enumerate(announcements[:6]):
            # each announcement card shows product image, name, discount price and deadline
            card = ctk.CTkFrame(self.announcement_products_frame, width=280, height=280, fg_color="#F0F4FF", corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=50)
            card.grid_propagate(False)
            # product image
            prod_img = self.load_product_image(ann.get("image_url") or ann.get("image") or "", size=(120,120))
            if prod_img:
                img_lbl = ctk.CTkLabel(card, image=prod_img, text="")
                img_lbl.image = prod_img
                img_lbl.grid(row=0, column=0, pady=(5,2))

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
        self.popular_items_label.grid(row=4, column=0, sticky="w",padx =20, pady=(5, 5))

        self.popular_items_scroll_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent", orientation="horizontal", height=180)
        self.popular_items_scroll_frame.grid(row=5, column=0, sticky="ew", pady=(0, 5))

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
                                  product_id=item.get("product_id")).grid(row=0, column=i, padx=10, pady=5)

        # --- New Items Section ---
        self.new_items_label = ctk.CTkLabel(parent_frame, text="New Items", font=("Arial", 22, "bold"), text_color="black")
        self.new_items_label.grid(row=6, column=0, sticky="w", padx=20, pady=(5, 5))

        self.new_items_scroll_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent", orientation="horizontal", height=180)
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
        """
        Generic fetcher for product flags. flag_column should be 'is_popular' or 'is_new'.
        Returns list of product dicts.
        """
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
            image_path = r[7] or ""
            image_filename = image_path.replace("images/", "").replace("\\", "/").split("/")[-1]
            image_path = os.path.join(IMAGE_BASE_DIR, image_filename)


            
            products.append({
            "product_id": r[0],
            "product_name": r[1],
            "price": str(r[2]) if r[2] is not None else "0.00",
            "weight": "",  
            "image_url": image_path  
        })
        return products
    
    def create_category_card(self, parent, name, icon_filename):
        """Creates a single category card widget."""
        card = ctk.CTkFrame(parent, width=120, height=120, fg_color="#E0DDF0", corner_radius=10)
        card.pack_propagate(False) # Prevent card from resizing to content

        icon = self.load_icon(icon_filename, 60) # Icons for categories
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

        # Main container for weight, price and add button
        # The height of 40 here seems fine for the bottom content.
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

        # Add to cart button on the right side
        # No change needed here, as the button is in the bottom_frame
        add_to_cart_button = ctk.CTkButton(bottom_frame, text="➕", width=34, height=34, corner_radius=17,
                                        fg_color="#FFFFFF", hover_color="#F0FFF0", text_color="black",
                                        font=("Arial", 18, "bold"),
                                        command=lambda pid=product_id, pname=name, pprice=price_val: self.on_add_to_cart(pid, pname, pprice))
        add_to_cart_button.pack(side="right", anchor="e", padx=2)

        return card
    
    
    def on_add_to_cart(self, product_id, product_name, price_text):
        """
        Handler when user clicks + on an item card.
        - Inserts or updates check_out table with quantity increment.
        - Maintains local cart_cache for fast preview.
        """
        # Convert price_text "$12.99" -> decimal
        try:
            price_val = float(str(price_text).replace("$","").replace(",",""))
        except:
            price_val = 0.0

        # If product_id missing, we cannot persist (but still keep in-memory)
        if not product_id:
            # fallback behavior: show a small dialog / print warning
            print("Warning: product_id missing for", product_name)
            # increment in local cache by a synthetic key (name)
            key = f"name:{product_name}"
            self.cart_cache[key] = self.cart_cache.get(key, 0) + 1
            return

        # 1) Update local cache
        self.cart_cache[product_id] = self.cart_cache.get(product_id, 0) + 1
        qty = self.cart_cache[product_id]

        
        try:
            # Look for existing open cart row (we will use customer_id NULL in demo)
            sel_q = """SELECT cart_id, quantity FROM check_out WHERE product_id = %s AND customer_id IS NULL LIMIT 1"""
            existing = db.fetchone(sel_q, (product_id,))
            if existing:
                new_qty = existing.get("quantity", 0) + 1
                # update row
                update_q = """UPDATE check_out SET quantity=%s, item_total=%s WHERE cart_id=%s"""
                item_total = round(price_val * new_qty, 2)
                success = db.execute(update_q, (new_qty, item_total, existing.get("cart_id")))
                if success is False:
                    print("Failed to update cart row for product", product_id)
                else:
                    print(f"Updated cart item (product_id={product_id}) to qty {new_qty}")
            else:
                # insert new row
                insert_q = """INSERT INTO check_out (product_id, customer_id, items, description, price, quantity, item_total, subtotal, shipping_fee, total)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                quantity = 1
                item_total = round(price_val * quantity, 2)
                subtotal = item_total
                shipping_fee = 0.00
                total = subtotal + shipping_fee
                # items and description are optional; we set items as product_name here
                res = db.execute(insert_q, (product_id, None, product_name, product_name, price_val, quantity, item_total, subtotal, shipping_fee, total))
                if res is False:
                    print("Failed to insert cart row for product", product_id)
                else:
                    print(f"Inserted cart item (product_id={product_id})")
        except Exception as e:
            print("Error adding to cart:", e)
            traceback.print_exc()

        # Optionally update a UI badge / cart preview (if present)
        # For immediate feedback, show a tiny toast-like label (transient)
        try:
            self.show_added_to_cart_toast(product_name)
        except:
            pass
        
        
    def show_added_to_cart_toast(self, product_name):
        """
        Quick visual feedback: small temporary label that disappears automatically.
        This is intentionally small and optional; your team can replace with nicer toasts.
        """
        toast = ctk.CTkLabel(self, text=f"Added {product_name} to cart", fg_color="#E8FFF0", text_color="#1F7A2D", corner_radius=8)
        # place bottom-right of main window
        toast.place(relx=0.75, rely=0.88)
        # hide after 1.2s (simple mechanism)
        self.after(1200, toast.destroy)
        
    
    def render_checkout_preview(self, parent):
        """
        Simple preview of the checkout table content (rows that have customer_id IS NULL).
        Team will implement a full checkout UI later; this function provides
        a live view that confirms the add-to-cart integration works.
        """
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
       

    
    

   

if __name__ == "__main__":
    app = UserDashboard()
    app.mainloop()    