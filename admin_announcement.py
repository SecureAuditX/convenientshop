from datetime import date, datetime
import customtkinter as ctk
from PIL import Image, ImageTk
from db_file import db
import os


IMAGE_BASE_DIR = r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop\images" # Re-use the user's defined path

def load_icon_placeholder(icon_name, size, placeholder_text=""):
   
    try_paths = [
        os.path.join(IMAGE_BASE_DIR, icon_name),
    ]
    for path in try_paths:
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception:
                pass # Fallback to placeholder if loading fails
    
    # Placeholder: Create a simple grey square with text (for image column or + icon)
    from PIL import ImageDraw, ImageFont
    img = Image.new('RGBA', (size, size), (200, 200, 255, 255))
    if placeholder_text:
        draw = ImageDraw.Draw(img)
        try:
            # Attempt to use a system font
            font = ImageFont.truetype("arial.ttf", int(size*0.4))
        except IOError:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text position to center it
        text_bbox = draw.textbbox((0, 0), placeholder_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (size - text_width) / 2
        y = (size - text_height) / 2 - 2 # Minor adjustment for better centering
        
        draw.text((x, y), placeholder_text, font=font, fill=(50, 50, 50, 255))
        
    return ImageTk.PhotoImage(img)

# --- New Announcement Pop-up Dialog ---

class NewAnnouncementPopup(ctk.CTkToplevel):
    def __init__(self, master, refresh_callback):
        super().__init__(master)
        self.title("New Announcement")
        self.geometry("400x450")
        self.resizable(False, False)
        self.refresh_callback = refresh_callback
        self.transient(master) # Set to modal
        self.lift()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(self, text="Add New Discount Announcement", font=("Arial", 16, "bold"), text_color="black").grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # Fields definition
        fields = [
            ("Image URL (Link):", "img_url_entry", None),
            ("Name:", "name_entry", None),
            ("Discount Price:", "discount_price_entry", None),
            ("Discount Deadline (YYYY-MM-DD):", "discount_deadline_entry", None),
            ("Status (ACTIVE/PENDING):", "status_entry", ["ACTIVE", "PENDING"])
        ]
        
        self.entries = {}
        for i, (label_text, entry_name, options) in enumerate(fields):
            row = i + 1
            ctk.CTkLabel(self, text=label_text, anchor="w", text_color="black").grid(row=row, column=0, padx=20, pady=5, sticky="w")
            
            if options:
                # Use Combobox for status
                entry = ctk.CTkComboBox(self, values=options, command=None, width=200, corner_radius=8, fg_color="white", text_color="black")
                entry.set(options[0])
            else:
                # Use regular entry for text inputs
                entry = ctk.CTkEntry(self, width=200, corner_radius=8, fg_color="white", text_color="black")
            
            entry.grid(row=row, column=1, padx=20, pady=5, sticky="ew")
            self.entries[entry_name] = entry

        # Add Button #E0DDF0  #333333
        add_button = ctk.CTkButton(self, text="Add Announcement", command=self.add_announcement, 
                                   fg_color="#A4A4EB", hover_color="#333333", text_color="black",
                                   font=("Arial", 14, "bold"), corner_radius=10)
        add_button.grid(row=len(fields) + 1, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # Catch outside clicks
        self.grab_set()

    def add_announcement(self):
        """Validates inputs, saves to DB, and refreshes the main UI."""
        img_url = self.entries["img_url_entry"].get()
        name = self.entries["name_entry"].get()
        discount_price_str = self.entries["discount_price_entry"].get()
        deadline_str = self.entries["discount_deadline_entry"].get()
        status = self.entries["status_entry"].get()
        product_id = self.entries["product_dropdown"].get()

        # Basic Validation
        if not all([img_url, name, discount_price_str, deadline_str, status]):
            print("Validation Error: All fields must be filled.")
            return

        try:
            discount_price = float(discount_price_str)
            # Validate date format and convert to date object
            discount_deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date() 
        except ValueError as e:
            print(f"Input Error: Check discount price (must be number) and deadline format (YYYY-MM-DD). Error: {e}")
            return
        
        # SQL INSERT
        query = """
        INSERT INTO announcement (img_url, name, discount_price, discount_deadline, product_id, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (img_url, name, discount_price, discount_deadline, product_id, status)

        if db.execute_commit(query, params):
            print("Announcement added successfully!")
            self.destroy()
            self.refresh_callback() # Refresh the main UI
        else:
            print("Failed to add announcement to the database.")

# --- Main Announcement Content Frame ---

class AnnouncementUI(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Ensure the table area expands

        # 1. Header and 'New Announcement' Button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)

        # Title and Subtitle (Match Image Design)
        ctk.CTkLabel(header_frame, text="Announcement", font=("Arial", 28, "bold"), text_color="black").grid(row=0, column=0, sticky="w", pady=(15, 0),padx=(20,0))
        ctk.CTkLabel(header_frame, text="Share discount updates to customers", font=("Arial", 14), text_color="gray").grid(row=1, column=0, sticky="w", pady=(0, 10), padx=(20,0))

        # New Announcement Button (Match Image Design)
        self.new_announcement_button = ctk.CTkButton(header_frame, text="New Announcement", 
                                                    command=self.open_new_announcement_popup, 
                                                    fg_color="#A4A4EB", hover_color="#333333", 
                                                    text_color="black", font=("Arial", 16, "bold"),
                                                    image=load_icon_placeholder("plus.png", 20, "+"), 
                                                    compound="left", width=180, height=45, corner_radius=10)
        self.new_announcement_button.grid(row=0, column=1, rowspan=2, sticky="e", padx=(0, 10))
        self.new_announcement_button.image = load_icon_placeholder("plus.png", 20, "+") # Keep reference

        # 2. Stats Cards Frame
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, sticky="ew", pady=(10, 30))
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="stat_col")

        # Create stat cards and store references to their value labels
        self.active_post_card = self.create_stat_card(self.stats_frame, "Active Post", 0)
        self.expired_post_card = self.create_stat_card(self.stats_frame, "Expired Post", 1)
        self.total_claim_card = self.create_stat_card(self.stats_frame, "Total Claim", 2)
        
        # 3. Announcement Table Area
        self.table_container = ctk.CTkFrame(self, fg_color="transparent")
        self.table_container.grid(row=2, column=0, sticky="nsew")
        self.table_container.grid_columnconfigure(0, weight=1)

        # Load data on initialization
        self.load_announcements()

    def create_stat_card(self, parent, title, column):
        """Creates a single stat card matching the image design."""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, height=100)
        card.grid(row=0, column=column, padx=15, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        
        # Title Label
        ctk.CTkLabel(card, text=title, font=("Arial", 16), text_color="gray").grid(row=0, column=0, padx=20, pady=(15, 0), sticky="w")
        
        # Value Label
        value_label = ctk.CTkLabel(card, text="0", font=("Arial", 32, "bold"), text_color="black")
        value_label.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
        card.value_label = value_label # Store reference to update later
        return card

    def update_stats(self, data):
        """Calculates and updates the three stats cards based on current data."""
        today = date.today()
        
        active_count = 0
        expired_count = 0
        
        # Total Claim count is not stored, so we'll use a mock/placeholder
        total_claim = 7 

        for row in data:
            deadline = row.get('discount_deadline')
            
            is_expired = False
            if isinstance(deadline, date):
                is_expired = deadline < today

            if is_expired:
                expired_count += 1
            elif row.get('status', 'N/A').upper() == 'ACTIVE':
                active_count += 1
            
        self.active_post_card.value_label.configure(text=str(active_count))
        self.expired_post_card.value_label.configure(text=str(expired_count))
        self.total_claim_card.value_label.configure(text=str(total_claim))

    def open_new_announcement_popup(self):
        """Opens the pop-up window to add a new announcement."""
        # Ensure only one pop-up is open
        if hasattr(self, 'popup_window') and self.popup_window.winfo_exists():
            self.popup_window.lift()
        else:
            # Pass load_announcements as the refresh callback
            self.popup_window = NewAnnouncementPopup(self.master, self.load_announcements)

    def delete_announcement(self, annou_id):
        """Deletes an announcement from the database and reloads the UI."""
        print(f"Attempting to delete announcement ID: {annou_id}")
        query = "DELETE FROM announcement WHERE annou_id = %s"
        if db.execute_commit(query, (annou_id,)):
            print(f"Successfully deleted ID: {annou_id}")
            self.load_announcements() # Reload the list to update the UI
        else:
            print(f"Failed to delete ID: {annou_id}")

    def load_announcements(self):
        """Fetches data from the DB and draws the announcement table, using delete.png icon."""
        
        # --- 1. Load the Delete Icon (Executed once before the loop) ---
        ICON_SIZE = (18, 18)
        delete_icon = None
        icon_path = ""
        try:
            icon_path = os.path.join(IMAGE_BASE_DIR, "delete.png")
            # Load the image using Pillow and wrap it with CTkImage
            delete_icon = ctk.CTkImage(
                light_image=Image.open(icon_path),
                size=ICON_SIZE
            )
        except Exception as e:
            # If loading fails (file not found, wrong path, etc.), print a warning and fall back to emoji
            print(f"Warning: Could not load delete icon from {icon_path}. Falling back to emoji. Error: {e}")

        # Clear existing table widgets
        for widget in self.table_container.winfo_children():
            widget.destroy()

        # Create the white background frame for the table
        table_background_frame = ctk.CTkFrame(self.table_container, fg_color="white", corner_radius=15)
        table_background_frame.pack(fill="both", expand=True, padx=20, pady=0) 
        table_background_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="table_col") 

        # Table Header (1st Row)
        headers = ["IMAGE", "NAME", "DISCOUNT PRICE", "DISCOUNT DEADLINE", "STATUS"]
        for i, text in enumerate(headers):
            ctk.CTkLabel(table_background_frame, text=text, font=("Arial", 14, "bold"), text_color="#333333", anchor="w").grid(row=0, column=i, padx=(20 if i == 0 else 5), pady=15, sticky="w")
        
        # Add column for Delete button (empty header)
        ctk.CTkLabel(table_background_frame, text="", font=("Arial", 14, "bold"), text_color="#333333").grid(row=0, column=5, padx=5, pady=15, sticky="ew")


        # Fetch data from database
        data = db.fetchall("SELECT * FROM announcement ORDER BY discount_deadline DESC")
        
        # Update statistics based on fetched data
        self.update_stats(data)

        # Scrollable area for rows
        scroll_frame = ctk.CTkScrollableFrame(table_background_frame, fg_color="transparent", height=450) 
        scroll_frame.grid(row=1, column=0, columnspan=6, sticky="ew", padx=0, pady=(0, 10))
        scroll_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="table_col") 


        today = date.today()
        # Populate rows
        for i, row_data in enumerate(data):
            annou_id = row_data['annou_id']
            img_url = row_data['img_url']
            name = row_data['name']
            discount_price = f"${row_data['discount_price']:.2f}"
            deadline = row_data['discount_deadline']
            status = row_data['status'].upper()
            
            # Dynamic Status Check
            status_text = status
            status_color = "#10B981" # Green
            
            # Check for expiration based on deadline
            if isinstance(deadline, date) and deadline < today:
                status_text = "EXPIRED"
                status_color = "#EF4444" # Red

            # Row Frame for separation and spacing
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.grid(row=i, column=0, columnspan=6, sticky="ew", pady=(10 if i == 0 else 5, 5)) 
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="table_col")
            
            # 1. Image (Placeholder)
            img_icon = load_icon_placeholder(os.path.basename(img_url) if img_url else "default.png", 50, placeholder_text="IMG")
            img_label = ctk.CTkLabel(row_frame, image=img_icon, text="", anchor="w")
            img_label.grid(row=0, column=0, padx=(20, 5), pady=5, sticky="w")
            img_label.image = img_icon # Keep reference
            
            # 2. Name
            ctk.CTkLabel(row_frame, text=name, font=("Arial", 14), text_color="black", anchor="w").grid(row=0, column=1, padx=5, sticky="w")

            # 3. Discount Price
            ctk.CTkLabel(row_frame, text=discount_price, font=("Arial", 14), text_color="black", anchor="w").grid(row=0, column=2, padx=5, sticky="w")

            # 4. Discount Deadline
            deadline_str = deadline.strftime("%m/%d/%Y") if isinstance(deadline, date) else "N/A"
            ctk.CTkLabel(row_frame, text=deadline_str, font=("Arial", 14), text_color="black", anchor="w").grid(row=0, column=3, padx=20, sticky="w")

            # 5. Status
            status_label = ctk.CTkLabel(row_frame, text=status_text, font=("Arial", 14, "bold"), text_color=status_color, anchor="w")
            status_label.grid(row=0, column=4, padx=30, sticky="w")
            
            # 6. Delete Icon Button (UPDATED BLOCK)
            if delete_icon:
                # Use the loaded image icon
                delete_button = ctk.CTkButton(
                    row_frame, 
                    text="", 
                    image=delete_icon, # Using the image
                    command=lambda id=annou_id: self.delete_announcement(id),
                    width=30, height=30, 
                    fg_color="transparent", 
                    hover_color="#F0F0F0",
                )
            else:
                # Fallback to emoji if image failed to load
                delete_button = ctk.CTkButton(
                    row_frame, 
                    text="🗑️", 
                    command=lambda id=annou_id: self.delete_announcement(id),
                    width=30, height=30, 
                    fg_color="transparent", hover_color="#F0F0F0", 
                    text_color="#EF4444", font=("Arial", 18)
                )

            delete_button.grid(row=0, column=5, padx=20, sticky="w")
            