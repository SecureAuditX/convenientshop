from db_file import db
import customtkinter as ctk
import re
import hashlib
import bcrypt
import mysql.connector

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG_COLOR = "#F7F7F7" 
CARD_COLOR = "white" 
INPUT_BG_COLOR = "#E0DDF0"
INPUT_BORDER_COLOR = "#D7D2F4" 
INPUT_ERROR_COLOR = "red"
DEFAULT_BORDER_WIDTH = 2 
BUTTON_FG_COLOR = "#A9A1E0" 
BUTTON_HOVER_COLOR = "#8F87C4"
INPUT_HEIGHT = 50
INPUT_CORNER_RADIUS = 10
FORM_PADDING = 50 # Horizontal padding for input fields

class HashingMixin:
    """Provides hashing utilities using SHA-256 for email and bcrypt for passwords."""
    
    def hash_email(self, email):
        """Hashes the email address using SHA-256."""
        # This hash is used for the 'cryptographic_status' column and the 'login' table.
        return hashlib.sha256(email.lower().encode('utf-8')).hexdigest()
    
    def hashed_password(self, password):
        """Hashes the password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_bytes.decode('utf-8')


class AdminSettingsApp(ctk.CTkFrame, HashingMixin):

    def __init__(self, parent_frame, customer_id, email, **kwargs):
        # Initialize the main frame with the correct background color
        super().__init__(parent_frame, fg_color=BG_COLOR, corner_radius=0, **kwargs)

        # Store the current logged-in user info (customer_id will be the Admin's ID)
        self.logged_in_customer_id = customer_id
        self.email = email
        
        # Storage for input/error widgets
        self.input_entries = {}
        self.error_labels = {}
        
        # --- Configure Grid for this frame ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Main Form Card

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="nw", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Settings", font=("Arial", 30, "bold"), text_color="black").pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Manage your store configuration and preferences", font=("Arial", 14), text_color="#555").pack(anchor="w")

        self.form_container = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=15)
        self.form_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Configure the grid inside the form container for two-column layout
        self.form_container.grid_columnconfigure(0, weight=1, uniform="group1")
        self.form_container.grid_columnconfigure(1, weight=1, uniform="group1")
        
        # Rows 0-5 for Inputs, Row 6 for status, Row 7 is spacer, Row 8 for button
        self.form_container.grid_rowconfigure(6, weight=0) 
        self.form_container.grid_rowconfigure(7, weight=1) 
        self.form_container.grid_rowconfigure(8, weight=0) 

        def create_input_field(parent, label_text, entry_key, grid_row, grid_col, placeholder_text, show_char=None):
            
            label_frame = ctk.CTkFrame(parent, fg_color="transparent")
            label_frame.grid(row=grid_row, column=grid_col, sticky="w", 
                             padx=(FORM_PADDING if grid_col == 0 else 20, 20), 
                             pady=(40 if grid_row == 0 else 30, 5)) 

            # Determine if the field is required (ends with *)
            is_required = label_text.endswith(" *")
            base_label_text = label_text.replace(" *", "")

            # Main Label (e.g., "Store Name")
            main_label = ctk.CTkLabel(label_frame, text=base_label_text, 
                                     font=("Arial", 16, "bold"), text_color="black")
            main_label.pack(side="left", padx=(0, 2)) # Pack left, small gap to asterisk

            # Red Asterisk Label (if required)
            if is_required:
                asterisk = ctk.CTkLabel(label_frame, text="*", 
                                         font=("Arial", 16, "bold"), text_color="red")
                asterisk.pack(side="left")

            entry = ctk.CTkEntry(
                parent,
                placeholder_text=placeholder_text,
                show=show_char,
                height=INPUT_HEIGHT,
                corner_radius=INPUT_CORNER_RADIUS,
                fg_color=INPUT_BG_COLOR,
                border_color=INPUT_BORDER_COLOR, 
                border_width=DEFAULT_BORDER_WIDTH, # Always use border_width=2
                text_color="black",
                font=("Arial", 16)
            )
            # Entry position directly below the label frame
            entry.grid(row=grid_row + 1, column=grid_col, sticky="ew", 
                         padx=(FORM_PADDING if grid_col == 0 else 20, 20),
                         pady=(0, 0)) # Reduced padding here to manage space 

            self.input_entries[entry_key] = entry

            error_lbl = ctk.CTkLabel(parent, text="", text_color=INPUT_ERROR_COLOR, font=("Arial", 10), anchor="w")
            error_lbl.grid(row=grid_row + 2, column=grid_col, sticky="w", 
                             padx=(FORM_PADDING if grid_col == 0 else 20, 20),
                             pady=(0, 10)) 
            self.error_labels[entry_key] = error_lbl
            
            return entry

        self.store_name_entry = create_input_field(self.form_container, "Store Name *", "first_name", 0, 0, "Enter store name")
        self.email_entry = create_input_field(self.form_container, "Email *", "email", 0, 1, "Enter Email Address")
        
        # Row 2 & 3 (Phone Number and Address)
        self.phone_number_entry = create_input_field(self.form_container, "Phone Number *", "phone_no", 2, 0, "Enter phone number")
        self.address_entry = create_input_field(self.form_container, "Address *", "address", 2, 1, "Enter Address")
        
        # Row 4 & 5 (New Password and Confirm Password)
        self.password_entry = create_input_field(self.form_container, "New Password *", "password", 4, 0, "Enter new password", show_char="*")
        self.confirm_password_entry = create_input_field(self.form_container, "Confirm Password *", "confirm_password", 4, 1, "Confirm Password", show_char="*")
        
        self.status_label = ctk.CTkLabel(self.form_container, text="", font=("Arial", 12, "bold"), text_color="red")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(10, 0))

        update_btn = ctk.CTkButton(
            self.form_container,
            text="Update Info",
            fg_color=BUTTON_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            width=200,
            height=55,
            corner_radius=10,
            font=("Arial", 18, "bold"),
            command=self.handle_update
        )
        update_btn.grid(row=8, column=0, columnspan=2, pady=(30, 50)) 

        # Load user info from database
        self.load_current_data()


    def load_current_data(self):
        """Load the Admin's data from DB based on self.logged_in_customer_id."""
        # Clear existing data before loading
        for key in self.input_entries:
            self.input_entries[key].delete(0, ctk.END)
            # Ensure borders are the default color when loading data
            self.input_entries[key].configure(border_color=INPUT_BORDER_COLOR) 

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="zxcvbnm",
                database="convenient_shop"
            )
            cursor = conn.cursor(dictionary=True)

            # Query for the specific Admin record, using the logged-in ID
            cursor.execute(""" 
                SELECT first_name, phone_no, address 
                FROM customers 
                WHERE customer_id = %s
            """, (self.logged_in_customer_id,)) 

            row = cursor.fetchone()

            if row:
                self.input_entries["first_name"].insert(0, row["first_name"])
                #self.input_entries["email"].insert(0, row["email"]) 
                self.input_entries["phone_no"].insert(0, row["phone_no"])
                self.input_entries["address"].insert(0, row["address"])
                
        except mysql.connector.Error as err:
            self.status_label.configure(text=f"DB Load Error: {err}", text_color=INPUT_ERROR_COLOR)

        finally:
            if cursor: cursor.close()
            if conn: conn.close()


    def _clear_errors(self):
        """Clears all error messages and resets input borders to default color."""
        for k in self.error_labels:
            self.error_labels[k].configure(text="")
        
        # Reset border color to the default UI color (purple/blue)
        for k in self.input_entries:
            self.input_entries[k].configure(border_color=INPUT_BORDER_COLOR)
            
        self.status_label.configure(text="") 


    def _display_error(self, key, msg):
        """Displays an error message for a specific input field and highlights its border in red."""
        self.error_labels[key].configure(text=msg)
        # Set border color to red to highlight the error field
        self.input_entries[key].configure(border_color=INPUT_ERROR_COLOR) 
        self.status_label.configure(text="Fix errors above.", text_color=INPUT_ERROR_COLOR)


    def validate_inputs(self, data):
        """Validates input data for the Admin settings."""
        self._clear_errors()
        has_error = False

        # Store Name (using first_name key)
        if not data["first_name"].strip():
            self._display_error("first_name", "Store Name required.")
            has_error = True
            
        # Email
        email = data["email"].strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
            self._display_error("email", "Invalid email format.")
            has_error = True

        # Phone Number
        phone = data["phone_no"].strip()
        if not phone.isdigit() or len(phone) != 11: 
            self._display_error("phone_no", "Phone must be 11 digits.")
            has_error = True

        # Address
        if not data["address"].strip():
            self._display_error("address", "Address required.")
            has_error = True
            
        # Password Validation
        pwd = data["password"]
        confirm_pwd = data["confirm_password"]
        
        is_password_change_attempt = bool(pwd or confirm_pwd)
        
        if is_password_change_attempt:
            
            # Check for mismatch
            if pwd != confirm_pwd:
                error_msg = "Passwords must match."
                self._display_error("confirm_password", error_msg)
                self._display_error("password", error_msg)
                has_error = True
            
            # Check for partial entry if they match or if we haven't hit the mismatch error yet
            elif (pwd and not confirm_pwd) or (confirm_pwd and not pwd):
                 error_msg = "Both new password fields must be filled."
                 self._display_error("password", error_msg)
                 self._display_error("confirm_password", error_msg)
                 has_error = True
                 
            # Check complexity only if we have a full, matching password attempt
            elif pwd and confirm_pwd and pwd == confirm_pwd:
                if not (
                    len(pwd) >= 8
                    and re.search(r"[A-Z]", pwd)
                    and re.search(r"[a-z]", pwd)
                    and re.search(r"[0-9]", pwd)
                    and re.search(r"[@$!%*#?&]", pwd)
                ):
                    self._display_error("password", "Password too weak (8+ chars, upper, lower, digit, symbol).")
                    has_error = True
                    if not has_error: 
                         self.input_entries["confirm_password"].configure(border_color=INPUT_BORDER_COLOR)

        return not has_error
    
    def handle_update(self):
        """Processes the update of the Admin/Store information."""
        self._clear_errors()
        self.status_label.configure(text="Processing...", text_color="blue")

        data = {k: self.input_entries[k].get() for k in self.input_entries}

        if not self.validate_inputs(data):
            return

        # Prepare data for DB update
        new_hash_email = self.hash_email(data["email"]) 
        
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="zxcvbnm",
                database="convenient_shop"
            )
            cursor = conn.cursor()

            cursor.execute(""" 
                UPDATE customers 
                SET first_name=%s, last_name=%s, email=%s, phone_no=%s, address=%s, cryptographic_status=%s
                WHERE customer_id=%s
            """, (
                data["first_name"], 
                "Admin", 
                data["email"], 
                data["phone_no"],
                data["address"],
                new_hash_email, 
                self.logged_in_customer_id 
            ))

            if data["password"]:
                new_hash_pwd = self.hashed_password(data["password"]) 
                cursor.execute("""
                    UPDATE login 
                    SET email=%s, password=%s
                    WHERE customer_id=%s
                """, (new_hash_email, new_hash_pwd, self.logged_in_customer_id)) 

            conn.commit()
            
            # Since the email might change, we should reload the data to see the latest values (except passwords)
            self.load_current_data() 

            self.status_label.configure(text="Store configuration updated successfully!", text_color="green")
            
            # Final reset of borders
            for key in self.input_entries:
                self.input_entries[key].configure(border_color=INPUT_BORDER_COLOR)

        except mysql.connector.IntegrityError as e:
            conn.rollback()
            self.status_label.configure(text="Error: Email or Hash already exists for another user.", text_color=INPUT_ERROR_COLOR)
            
        except mysql.connector.Error as err:
            conn.rollback()
            self.status_label.configure(text=f"DB ERROR: {err}", text_color=INPUT_ERROR_COLOR)

        finally:
            if cursor: cursor.close()
            if conn: conn.close()