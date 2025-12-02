from db_file import db
import requests
from io import BytesIO
import customtkinter as ctk
import tkinter as tk
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
        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)   
        
        # Product_id -> quantity
        self.cart_cache = {}
 
        #sidebar frame (left panel)
        self.sidebar_frame = ctk.CTkFrame(self, fg_color="#E0DDF0", corner_radius=10) #D8DBF7
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1) 
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
        self.main_content_area.grid_rowconfigure(0, weight=1)
        
        self.cart_icon_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent", width=40, height=40)
        self.cart_icon_frame.grid(row=0, column=1, sticky="ne", padx=30, pady=(40, 0))  # Top-right corner
  
        # Load cart icon
        self.cart_icon = Image.open(r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop\images\shopping-cart.png").resize((30, 30), Image.LANCZOS)
        self.cart_image = ImageTk.PhotoImage(self.cart_icon)

        self.cart_label = ctk.CTkLabel(self.cart_icon_frame, image=self.cart_image, text="")
        self.cart_label.grid(row=0, column=0)

        # Add item count text to the cart icon
        self.item_count_label = ctk.CTkLabel(self.cart_icon_frame, text="0", font=("Arial", 12, "bold"), text_color="black")
        self.item_count_label.grid(row=0, column=1, padx=5)

        # Bind the cart icon to redirect to checkout
        self.cart_label.bind("<Button-1>", self.redirect_to_checkout)

        # Update the cart item count
        self.update_cart_item_count()
        
        # Content Frames for different sections (Dashboard, Categories, etc.) 
        self.dashboard_content_frame = ctk.CTkScrollableFrame(self.main_content_area, fg_color="transparent")
        self.category_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.checkout_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.payment_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.history_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.setting_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        
        self.search_var = ctk.StringVar() 
        # initially show the dashboard content
        #self.load_customer_name()
        self.load_customer_name()
        self.show_dashboard_content()
        
    def load_image_from_url(self, url, size=(80, 80)):
        """Downloads an image from a URL and returns a CTkImage object."""
        if not url or not url.strip().startswith(('http://', 'https://')):
            return None
        try:
            # 1. Download the image
            response = requests.get(url.strip(), timeout=10)
            response.raise_for_status() # Raise exception for bad status codes
            
            # 2. Convert to PIL Image
            image_data = BytesIO(response.content)
            img = Image.open(image_data)
            
            # 3. Resize and convert to CTkImage
            img = img.resize(size)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            
        except requests.exceptions.RequestException as e:
            # Handle common network/download errors (e.g., 404, timeout)
            print(f"Error downloading image from URL {url}: {e}")
            return None
        except Exception as e:
            # Handle image processing errors
            print(f"Error processing image: {e}")
            return None
    
        
    def update_cart_item_count(self):
        """
        Updates the number of items in the cart by checking the check_out table.
        """
        try:
            conn = db.DB_Connection()
            cursor = conn.cursor()

            # Query the number of items in the active cart for the customer
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
       
    def redirect_to_checkout(self, event=None):
        """Redirect to the checkout page when the cart icon is clicked."""
        print("Redirecting to checkout...")
        self.show_checkout_content()
    
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
        self.after(0, self.load_customer_name)
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
            email=self.logged_in_email,
            cart_update_callback=self.update_cart_item_count
        )
        category_ui.pack(expand=True, fill="both", padx=0, pady=0)
    
    def show_checkout_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.checkout_button)
        
        # Clear old widgets
        for w in self.checkout_content_frame.winfo_children():
            w.destroy()
            
        self.checkout_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        checkout_ui = Checkout(self.checkout_content_frame, customer_id=self.customer_id, email=self.logged_in_email, cart_update_callback=self.update_cart_item_count)
        checkout_ui.pack(expand=True, fill="both", padx=0, pady=0) 
        
    def show_payment_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.payment_button)

        # Clear old widgets
        for w in self.payment_content_frame.winfo_children():
            w.destroy()
            
        self.payment_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Instantiate and place the Payment UI
        payment_ui = Payment(self.payment_content_frame, customer_id=self.customer_id, email=self.logged_in_email, cart_update_callback=self.update_cart_item_count)
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
        
    # Start of dashboard content implementationn
    def render_dashboard_ui(self, parent_frame):

        for widget in parent_frame.winfo_children():
            widget.destroy()

        top_bar_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        top_bar_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        top_bar_frame.grid_columnconfigure(0, weight=1)
        top_bar_frame.grid_columnconfigure(1, weight=0) 

        search_frame = ctk.CTkFrame(top_bar_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=5)

        search_text_label = ctk.CTkLabel(search_frame, text="Search ", font=("Arial", 16, "bold"), text_color="black")
        search_text_label.grid(row=0, column=0, padx=(0, 5))

        # NOTE: load_icon must exist as a method
        search_icon = self.load_icon("search.png", 20)
        self.search_icon_label = ctk.CTkLabel(search_frame, image=search_icon, text="")
        self.search_icon_label.grid(row=0, column=1, padx=(0, 0))

        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Search", width=700, height=40, font=("Arial", 16),fg_color="#B4BAFF", 
            border_color="#D1D1DF", text_color="white",placeholder_text_color="white", corner_radius=20, 
            textvariable=self.search_var )
        self.search_entry.grid(row=0, column=2, padx=(10, 0))

        # --- ANNOUNCEMENTS SECTION ---
        self.announcement_label = ctk.CTkLabel(parent_frame, text="Announcement", font=("Arial", 22, "bold"), text_color="black")
        self.announcement_label.grid(row=1, column=0, sticky="w", padx=20, pady=(2, 2))
        
        self.product_announcements_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.product_announcements_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        announcement_cards_container = ctk.CTkFrame(self.product_announcements_frame, fg_color="transparent")
        announcement_cards_container.pack(fill="x", expand=True) 

        # Fetch data
        announcements = self.fetch_announcements_from_db()
        
        # Define properties for the announcement cards (for visual styling/discount percentage)
        CARD_PROPS = [ 
            {"color": "#E0DDF0", "discount": "12%", "discount_color": "#D4AC9F", "claim_color": "#7D97CE"}, 
            {"color": "#D7EAF0", "discount": "16%", "discount_color": "#EF8787", "claim_color": "#94DB95"}, 
            {"color": "#D9F0D9", "discount": "20%", "discount_color": "#A0B58D", "claim_color": "#81C2DC"}, 
            {"color": "#F0DDE8", "discount": "5%", "discount_color": "#E0B7D6", "claim_color": "#7D5D9E"}, 
        ]

        # Announcement rendering logic
        if not announcements:
            # Fallback for missing/expired announcements
            no_announcement_frame = ctk.CTkFrame(announcement_cards_container, width=250, height=260, fg_color="#F7F7F7", corner_radius=15, border_color="#A0A0A0", border_width=1)
            no_announcement_frame.pack_propagate(False)
            no_announcement_frame.pack(side="left", padx=10, pady=10)
            
            ctk.CTkLabel(no_announcement_frame, text="⏳", font=("Arial", 60)).pack(pady=(50, 10))
            ctk.CTkLabel(no_announcement_frame, text="New Announcement\nComing Soon", font=("Arial", 16, "bold"), text_color="#555555", justify="center").pack()
            
        else:
            for i, ann in enumerate(announcements[:5]): 
                # Defensive check is good practice, keep it.
                if ann.get("product_id") is None:
                    # This should print if product_id is NULL/None
                    print(f"Skipping announcement {ann.get('annou_id')}: Missing product_id.")
                    continue

                props = CARD_PROPS[i % len(CARD_PROPS)]
                
                # Convert date to string for display
                deadline = ann.get("discount_deadline")
                if isinstance(deadline, (datetime.date, datetime.datetime)):
                    deadline_text = deadline.strftime("%m/%d/%Y")
                else:
                    deadline_text = "N/A"
                    
                # Use the custom small card UI
                # ann.get("name") holds the 'ann_name' from the fetch function
                card = self.create_announcement_card_ui(
                    parent=announcement_cards_container,
                    product_id=ann.get("product_id"), 
                    product_name=ann.get("product_name", ann.get("name", "Discount Item")), # Prefer product_name, fall back to ann_name, then generic name
                    discount_price=ann.get('discount_price', '0.00'),
                    expiration_date=deadline_text,
                    image_filename=ann.get("image_url") or "", 
                    card_color=props["color"],
                    discount_text=props["discount"],
                    discount_bg_color=props["discount_color"],
                    claim_color=props["claim_color"],
                )
                card.pack(side="left", padx=10, pady=10)

        # --- POPULAR ITEMS SECTION ---
        self.popular_items_label = ctk.CTkLabel(parent_frame, text="Popular Items", font=("Arial", 22, "bold"), text_color="black")
        self.popular_items_label.grid(row=3, column=0, sticky="w",padx =20, pady=(2, 2))
        
        self.popular_items_scroll_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent", orientation="horizontal", height=175)
        self.popular_items_scroll_frame.grid(row=4, column=0, sticky="ew", pady=(10, 2))
        
        popular_items = self.fetch_products_by_flag(flag_column="is_popular", limit=12)

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
            self.create_item_card(self.popular_items_scroll_frame,
                                name=item.get("product_name"),
                                weight=item.get("weight", ""),
                                price=item.get("price"),
                                image_filename=item.get("image_url") or item.get("product_image"), 
                                product_id=item.get("product_id")).grid(row=0, column=i, padx=10, pady=2)

        # --- NEW ITEMS SECTION ---
        self.new_items_label = ctk.CTkLabel(parent_frame, text="New Items", font=("Arial", 22, "bold"), text_color="black")
        self.new_items_label.grid(row=5, column=0, sticky="w", padx=20, pady=(2, 2))
        
        self.new_items_scroll_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent", orientation="horizontal", height=175)
        self.new_items_scroll_frame.grid(row=6, column=0, sticky="ew", pady=(10, 2))
        
        new_items = self.fetch_products_by_flag(flag_column="is_new", limit=12)
        
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
                
            

  
    # This method assumes the existence of self.load_image_from_url
    def create_announcement_card_ui(self, parent, product_name, discount_price, expiration_date, 
                                    image_filename, card_color, discount_text, 
                                    discount_bg_color, claim_color, product_id):
        """Creates a single announcement card widget with the product name displayed."""
        
        # 1. Main Card Frame: Fixed size
        card = ctk.CTkFrame(parent, width=160, height=260, fg_color=card_color, corner_radius=15, border_width=0)
        card.pack_propagate(False) 
        card.grid_columnconfigure(0, weight=1)

        text_color = "black" if card_color.lower() in ("#d9f0d9", "#d7eaf0") else "white"

        # 2. Special Offer Label
        special_offer_label = ctk.CTkLabel(
            card, 
            text=f"Special Offer\n{discount_text}", 
            fg_color=discount_bg_color, 
            text_color=text_color, 
            font=("Arial", 10, "bold"), 
            corner_radius=8,
            width=100, 
            height=30 
        )
        special_offer_label.place(x=-20, y=10, anchor="nw", relwidth=0.6) 

        # 3. Product Image: 
        prod_img = self.load_image_from_url(image_filename, size=(80, 80)) 
        
        if prod_img:
            img_lbl = ctk.CTkLabel(card, image=prod_img, text="")
            img_lbl.image = prod_img
            img_lbl.grid(row=0, column=0, pady=(45, 5), sticky="n") 
        else:
            ctk.CTkLabel(card, text="🛍️", font=("Arial", 30)).grid(row=0, column=0, pady=(45, 5), sticky="n")

        # 4. NEW: Product Name Label (Inserted at Row 1)
        ctk.CTkLabel(
            card, 
            text=product_name.strip(), 
            font=("Arial", 13, "bold"),
            wraplength=140
        ).grid(row=1, column=0, pady=(0, 5), padx=5) 
            
        # 5. Discount Price (Now at Row 2)
        try:
            price_text = f"Price: ${float(discount_price):,.2f}"
        except:
            price_text = f"Price: {discount_price}"
            
        ctk.CTkLabel(card, text=price_text, font=("Arial", 11)).grid(row=2, column=0, pady=(0, 2)) 
        
        # 6. Expiration Date (Now at Row 3)
        ctk.CTkLabel(card, text=f"Expires: {expiration_date}", 
                    font=("Arial", 9), text_color="#555555").grid(row=3, column=0, pady=(0, 5))
                        
        # 7. Claim Offer Button (Now at Row 4)
        claim_btn = ctk.CTkButton(
            card, 
            text="CLAIM OFFER",
            fg_color=claim_color,
            hover_color=claim_color,
            text_color="white",
            font=("Arial", 12, "bold"),
            width=140, 
            height=30,
            corner_radius=8,
            # Command uses the passed product_id and cleaned product name
            command=lambda: self.add_to_cart_from_announcement(
                product_id=product_id,
                item_name=product_name.strip(),
                discount_price=discount_price
            )
        )
        claim_btn.grid(row=4, column=0, pady=(5, 10))
        
        return card

    def fetch_announcements_from_db(self):
        """
        Fetch announcement rows joined with product info with debug prints.
        """
        try:
            q = """
                SELECT a.annou_id, a.name AS ann_name, a.discount_price, a.discount_deadline,
                    a.img_url AS announcement_image_url,
                    a.product_id, 
                    p.product_name, p.image_url AS product_image_url
                FROM announcement a
                LEFT JOIN product p ON a.product_id = p.product_id
                WHERE a.status = 'active' OR a.status IS NULL
                ORDER BY a.annou_id DESC
                LIMIT 10
            """
            print("\n--- DEBUG: Executing Announcement Fetch Query ---")
            
            # Assuming 'db' is available and has a working fetchall method
            # This is the critical line to check.
            rows = db.fetchall(q) 
            
            print(f"--- DEBUG: Raw Rows Returned: {len(rows)} ---")
            
            if rows:
                print("--- DEBUG: First Row Example ---")
                print(rows[0])
            else:
                print("--- DEBUG: Query returned 0 rows. Check data/query conditions. ---")
                
            results = []
            for r in rows:
                # Map SQL results to expected dictionary keys
                results.append({
                    "annou_id": r.get("annou_id"),
                    "name": r.get("ann_name"), 
                    "product_name": r.get("product_name"),
                    "discount_price": r.get("discount_price"),
                    "discount_deadline": r.get("discount_deadline"),
                    "image_url": r.get("announcement_image_url"),
                    "product_id": r.get("product_id"), 
                })
            
            print(f"--- DEBUG: Formatted Results Count: {len(results)} ---\n")
            return results

        except Exception as e:
            import traceback 
            print("\n--- DEBUG: EXCEPTION IN fetch_announcements_from_db ---")
            print(traceback.format_exc())
            return []
    
    
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

        card = ctk.CTkFrame(parent, width=160, height=230, fg_color="white",
                            corner_radius=10, border_color="#E0DDF0", border_width=1)
        card.pack_propagate(False)

        item_image = self.load_product_image(image_filename or "", size=(100, 100))
        if item_image:
            image_label = ctk.CTkLabel(card, image=item_image, text="")
            image_label.image = item_image
            image_label.pack(pady=5)
        else:
            image_label = ctk.CTkLabel(card, text="🛒", font=("Arial", 40))
            image_label.pack(pady=5)

        name_label = ctk.CTkLabel(card, text=name, font=("Arial", 14, "bold"),
                                text_color="black", anchor="w")
        name_label.pack(fill="x", padx=10)

        qty_var = ctk.IntVar(value=1)

        try:
            price_val = float(price)
            price_text = f"${price_val:,.2f}"
        except:
            price_val = price
            price_text = str(price)

        add_row = ctk.CTkFrame(card, fg_color="transparent")
        add_row.pack(fill="x", padx=5, pady=(0, 0))

        add_btn = ctk.CTkButton(
            add_row,
            text="Add",
            width=60,
            height=30,
            corner_radius=8,
            fg_color="#FFFFFF",
            hover_color="#F0FFF0",
            text_color="black",
            font=("Arial", 14, "bold"),
            command=lambda pid=product_id, pname=name,
                        pprice=price_val, qv=qty_var:
                self.on_add_to_cart(pid, pname, pprice, qv.get())
        )
        add_btn.pack(side="right", pady=(0, 0))

        price_qty_row = ctk.CTkFrame(card, fg_color="transparent")
        price_qty_row.pack(fill="x", padx=5, pady=(0, 20))

        price_label = ctk.CTkLabel(
            price_qty_row, text=price_text,
            font=("Arial", 15, "bold"),
            text_color="black"
        )
        price_label.pack(side="left", pady=(0,10))

        qty_frame = ctk.CTkFrame(price_qty_row, fg_color="#E0DDF0", corner_radius=8)
        qty_frame.pack(side="right", pady=(0,10))

        minus_btn = ctk.CTkButton(
            qty_frame, text="-",
            width=20, height=20,         # SMALLER SIZE
            fg_color="white",
            text_color="black",
            corner_radius=6,
            command=lambda qv=qty_var: self.decrease(qv)
        )
        minus_btn.pack(side="left", padx=(4, 2))

        qty_lbl = ctk.CTkLabel(qty_frame, textvariable=qty_var, width=25)
        qty_lbl.pack(side="left")
        plus_btn = ctk.CTkButton(
            qty_frame, text="+",
            width=20, height=20,         # SMALLER SIZE
            fg_color="white",
            text_color="black",
            corner_radius=6,
            command=lambda qv=qty_var: self.increase(qv, 9999)
        )
        plus_btn.pack(side="left", padx=(2, 4))

        return card

    def on_add_to_cart(self, product_id, product_name, price_text, quantity):
        print(f"Quantity being added: {quantity}")  # Debugging line

        try:
            price_val = float(str(price_text).replace("$", "").replace(",", ""))
        except:
            print("Invalid price:", price_text)
            return

        if not self.customer_id:
            print("ERROR: No customer_id assigned")
            return

        try:
            conn = db.DB_Connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cart_id, quantity
                FROM check_out
                WHERE product_id = %s
                AND customer_id = %s
                AND total IS NULL
            """, (product_id, self.customer_id))

            row = cursor.fetchone()

            if row is None:
                cursor.execute("""
                    INSERT INTO check_out 
                    (product_id, customer_id, items, price, quantity, item_total)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (product_id, self.customer_id,
                    product_name, price_val, quantity, price_val * quantity))

                print(f"Inserted {quantity} x {product_name} into cart.")  # Debugging line

            else:
                cart_id, qty = row
                new_qty = qty + quantity
                new_total = new_qty * price_val

                cursor.execute("""
                    UPDATE check_out
                    SET quantity = %s,
                        item_total = %s
                    WHERE cart_id = %s
                    AND customer_id = %s
                    AND total IS NULL
                """, (new_qty, new_total, cart_id, self.customer_id))

                print(f"Updated quantity in cart: {product_name} (New Quantity: {new_qty})")  # Debugging line

            conn.commit()

            # After adding the item, update the cart icon count
            self.update_cart_item_count()

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

    def increase(self, qv, limit):
        if qv.get() < limit:
            qv.set(qv.get() + 1)
        else:
            print("Stock limit reached")

    def decrease(self, qv):
        if qv.get() > 1:
            qv.set(qv.get() - 1)
                  
    def show_added_to_cart_toast(self, product_name):
        
        toast = ctk.CTkLabel(self, text=f"Added {product_name} to cart", fg_color="#E8FFF0", text_color="#1F7A2D", corner_radius=8)
        
        x = self.search_entry.winfo_rootx() - self.winfo_rootx()
        y = self.search_entry.winfo_rooty() - self.winfo_rooty() + self.search_entry.winfo_height() + 5

        # place top middle
        toast.place(x=x, y=y)
        # hide after 1.2s (simple mechanism)
        self.after(1000, toast.destroy)
        

    # Assuming 'db' is imported from db_file
    def add_to_cart_from_announcement(self, product_id, item_name, discount_price):
        """
        Adds a discounted announcement item to the customer's active cart.
        """
        if not self.customer_id:
            print("Error: Customer not logged in. Cannot add to cart.")
            return
        
        # Ensures a valid product_id is used for the mandatory foreign key constraint
        if not product_id:
            print("Error: Cannot add to cart, product_id is missing/invalid.")
            return

        # We assume discount_price is the final price and quantity is 1
        query = """
        INSERT INTO check_out (customer_id, product_id, items, price, quantity)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        params = (self.customer_id, product_id, item_name, discount_price, 1)

        if db.execute_commit(query, params):
            print(f"Successfully claimed offer: {item_name} added to cart.")
            # Call a method to refresh the cart count on the dashboard if one exists
            if hasattr(self, 'refresh_cart_count'):
                self.refresh_cart_count() 
        else:
            print(f"Failed to add offer for {item_name} to cart.")
            
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