from db_file import Database
from db_file import db
import customtkinter as ctk
from PIL import Image, ImageTk
import hashlib
import bcrypt
import os
import mysql.connector
import re

# Database connection
db = Database()
connection = db.DB_Connection()

class SignupPage(ctk.CTk):
    
    # --- UI CONSTANTS ---
    ERROR_COLOR = "red"
    SUCCESS_COLOR = "green"
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Brightview Provision Signup")
        self.geometry("900x800")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        
        # Color palette
        self.PRIMARY_COLOR = "#A4A4EB"  
        self.BG_COLOR = "#A4A4EB"  
        self.FRAME_COLOR = "#E0DDF0" # Default placeholder color / Frame background   
        
        # Define default entry colors for easy resetting
        self.DEFAULT_ENTRY_FG_COLOR = self.PRIMARY_COLOR
        self.DEFAULT_ENTRY_BORDER_COLOR = self.PRIMARY_COLOR
        self.DEFAULT_ENTRY_TEXT_COLOR = "white"
        self.DEFAULT_ENTRY_PLACEHOLDER_COLOR = self.FRAME_COLOR

        # Configure Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main Frame
        self.main_frame = ctk.CTkFrame(self, fg_color=self.BG_COLOR, corner_radius=0)
        self.main_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Signup Box Frame
        self.signup_frame = ctk.CTkFrame(self.main_frame, fg_color=self.FRAME_COLOR, corner_radius=20, width=380, height=700)
        self.signup_frame.grid(row=0, column=0, padx=(50, 20))
        self.signup_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.signup_frame.grid_propagate(False)
        
        # Logo frame (Rest of UI Setup remains unchanged)
        self.logo_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.logo_frame.grid(row=0, column=1, sticky="nsew")
        self.logo_frame.grid_columnconfigure(0, weight=1)
        self.logo_frame.grid_rowconfigure(0, weight=1)
        
        # Load and displaying the logo image
        try:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_directory, "logo.png")
            
            original_image = Image.open(image_path)
            resized_image = original_image.resize((250, 250), Image.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_image)
            
            # Left Logo
            self.logo_label = ctk.CTkLabel(self.logo_frame, image=self.logo_image, text="")
            self.logo_label.grid(row=0, column=0, padx=5, pady=(10, 15))
        
        except FileNotFoundError:
            self.logo_label = ctk.CTkLabel(self.logo_frame, text="Logo Not Found", font=("Arial", 18, "bold"), text_color="#4F46E5")
            self.logo_label.grid(row=0, column=0, rowspan=2, padx=20, pady=20)
        
        # Title
        self.signup_title = ctk.CTkLabel(self.signup_frame, text="SIGNUP", font=("Arial", 36, "bold"), text_color="#4F46E5")
        self.signup_title.grid(row=0, column=0, padx=40, pady=(80, 30), sticky="w")
        
        # List of fields
        fields = [
            ("FIRST NAME*", "first_name", "enter first name"),
            ("LAST NAME*", "last_name", "enter last name"),
            ("EMAIL*", "email", "enter email"),
            ("PHONE NO*", "phone_no", "enter phone no"),
            ("ADDRESS*", "address", "enter address"),
            ("PASSWORD*", "password", "enter password")
        ]                                                       
            
        self.input_entries = {}
        self.initial_placeholders = {}

        for idx, (label_text, key, placeholder) in enumerate(fields):
            is_password = key == "password"
            
            # Store initial placeholder for resetting
            self.initial_placeholders[key] = placeholder 
            
            base_text = label_text.rstrip('*')
            has_asterisk = label_text.endswith('*')
            
            # Label setup (unchanged)
            label_container = ctk.CTkFrame(self.signup_frame, fg_color="transparent")
            label_container.grid(row=idx*2+1, column=0, padx=40, pady=(0, 2), sticky="w")
            
            base_label = ctk.CTkLabel(label_container, text=base_text, font=("Arial", 14, "bold"), text_color="#4F46E5", anchor="w")
            base_label.grid(row=0, column=0, sticky="w")
            
            if has_asterisk:
                asterisk_label = ctk.CTkLabel(label_container, text="*", font=("Arial", 14, "bold"), text_color="red", anchor="w")
                asterisk_label.grid(row=0, column=1, sticky="w", padx=(1, 0))
            
            # Entry Setup
            entry = ctk.CTkEntry(self.signup_frame, placeholder_text=placeholder, show="*" if is_password else "", 
                                 width=300, height=40, font=("Arial", 16), 
                                 fg_color=self.DEFAULT_ENTRY_FG_COLOR,
                                 text_color=self.DEFAULT_ENTRY_TEXT_COLOR, 
                                 placeholder_text_color=self.DEFAULT_ENTRY_PLACEHOLDER_COLOR,
                                 border_color=self.DEFAULT_ENTRY_BORDER_COLOR, 
                                 corner_radius=10,
                                 border_width=2) # Ensure border is visible
            
            # --- Bind FocusOut for real-time validation ---
            entry.key = key # Store the field key on the widget instance
            entry.bind("<FocusOut>", self.on_focus_out)
            # --- END Binding ---
            
            entry.grid(row=idx*2+2, column=0, padx=40, pady=(0, 2), sticky="w")
            self.input_entries[key] = entry
            
        # Status Label for global messages (Success/Database Errors)
        self.status_label = ctk.CTkLabel(self.signup_frame, text="", text_color=self.ERROR_COLOR, font=("Arial", 14))
        self.status_label.grid(row=len(fields)*2+3, column=0, padx=40, pady=(10, 5), sticky="w")
        
        # Signup Button
        self.signup_button = ctk.CTkButton(self.signup_frame, text="SIGNUP", font=("Arial", 20, "bold"), 
                                           command=self.handle_signup,
                                           width=300, height=40,
                                           fg_color="#4F46E5", hover_color="#3B34C4",
                                           text_color="white", corner_radius=50)
        self.signup_button.grid(row=len(fields)*2+4, column=0, padx=40, pady=(0, 1))
        self.signup_frame.grid_anchor("center")
        
        # Already have account (Login)
        link_frame = ctk.CTkFrame(self.signup_frame, fg_color="transparent")
        link_frame.grid(row=len(fields)*2+5, column=0, pady=(10, 50), padx=40)

        self.login_label = ctk.CTkLabel(link_frame, text="Already Have an Account?", 
                                             font=("Arial", 14), text_color="#4F46E5")
        self.login_label.grid(row=0, column=0, padx=(0, 5))
        
        self.login_link = ctk.CTkLabel(link_frame, text="Login", font=("Arial", 14, "underline"), text_color="#4F46E5", cursor="hand2")
        self.login_link.grid(row=0, column=1)
        self.login_link.bind("<Button-1>", self.redirect_to_login)     
        
    def on_focus_out(self, event):
        """Handles validation when focus leaves an entry field (Tab or mouse click)."""
        field_key = getattr(event.widget, 'key', None)
        if field_key:
            # Clear global status when checking a single field to avoid confusion
            self.status_label.configure(text="") 
            # Run validation only on this specific field
            self.validate_inputs(key_to_validate=field_key)

    # Helper function to display global (DB) messages in the status label
    def display_message(self, message, is_error=True):
        """Displays a message in the status label with appropriate color."""
        color = self.ERROR_COLOR if is_error else self.SUCCESS_COLOR
        self.status_label.configure(text=message, text_color=color)

    def reset_entry_styles(self, key_to_reset=None):
        """Resets the style and placeholder of specified or all entries to default."""
        if key_to_reset:
            keys = [key_to_reset]
        else:
            self.status_label.configure(text="") # Clear global status only if resetting all
            keys = self.input_entries.keys()

        for key in keys:
            if key in self.input_entries:
                entry = self.input_entries[key]
                entry.configure(
                    border_color=self.DEFAULT_ENTRY_BORDER_COLOR,
                    placeholder_text=self.initial_placeholders[key],
                    placeholder_text_color=self.DEFAULT_ENTRY_PLACEHOLDER_COLOR,
                    text_color=self.DEFAULT_ENTRY_TEXT_COLOR # Ensure input text is white
                )

    def highlight_error(self, key, message):
        """Highlights the specified entry with error styling."""
        entry = self.input_entries[key]
        entry.configure(
            border_color=self.ERROR_COLOR,
            placeholder_text=f"ERROR: {message}",
            placeholder_text_color=self.ERROR_COLOR,
            text_color=self.DEFAULT_ENTRY_TEXT_COLOR # Input text remains white
        )
        entry.delete(0, 'end') # Clear the current input

    # ---------------- ENCRYPTIONS ----------------
    def hash_email(self, email):
        return hashlib.sha256(email.lower().encode('utf-8')).hexdigest()
    
    def hashed_password(self, password):
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_bytes.decode('utf-8') 

    def validate_inputs(self, key_to_validate=None):
        """
        Validate all required fields (if key_to_validate is None) 
        or a single field (if key_to_validate is specified).
        """
        
        # Reset the style of the field being checked, or all fields if clicking SIGNUP
        if key_to_validate:
            self.reset_entry_styles(key_to_validate)
        else:
            self.reset_entry_styles() 

        data = {key: entry.get() for key, entry in self.input_entries.items()}

        # List of all fields to check, ordered by appearance
        fields_to_check = ["first_name", "last_name", "email", "phone_no", "address", "password"]
        
        # Determine the subset of fields to check based on key_to_validate
        if key_to_validate:
            try:
                # If validating a single key, create a list containing only that key
                fields_to_check = [key_to_validate]
            except ValueError:
                return False # Key not found, although this shouldn't happen with the new binding method

        
        # --- Sequential Validation Loop ---
        for key in fields_to_check:
            value = data[key]
            
            # --- 1. EMPTY FIELD CHECK ---
            if not value.strip():
                self.highlight_error(key, f"Please enter your {key.replace('_', ' ')}.")
                # Return False if checking all fields, or False if checking a single field
                return False if not key_to_validate else False
            
            # --- FIELD-SPECIFIC CHECKS ---
            
            if key == "first_name" or key == "last_name":
                # --- NEW: Character Limit Check ---
                if len(value) > 50:
                    self.highlight_error(key, "Cannot exceed 50 characters.")
                    return False

                # --- NAME VALIDATION (Existing Logic) ---
                name_pattern = r"^[A-Za-z]+$"

                if not re.match(name_pattern, value):
                    self.highlight_error(key, "Must contain only letters (A–Z).")
                    return False

                if len(set(value.lower())) == 1:
                    self.highlight_error(key, "Cannot be all the same letter.")
                    return False

            elif key == "email":
                # --- EMAIL VALIDATION (Existing Logic) ---
                email_pattern = (
                    r"^[a-zA-Z0-9._%+-]+"        
                    r"@"                         
                    r"[a-zA-Z0-9.-]+\."          
                    r"[A-Za-z]{2,}$"             
                )

                if not re.match(email_pattern, value.strip()):
                    self.highlight_error("email", "Invalid format (e.g., name@example.com).")
                    return False

            elif key == "phone_no":
                # --- PHONE NUMBER VALIDATION (Existing Logic) ---
                phone = value.strip()
                if not phone.isdigit():
                    self.highlight_error("phone_no", "Must contain only digits (0–9).")
                    return False

                if len(phone) != 11:
                    self.highlight_error("phone_no", "Must be exactly 11 digits.")
                    return False
                    
                if len(set(phone)) == 1:
                    self.highlight_error("phone_no", "Cannot be all the same digit.")
                    return False

            elif key == "address":
                # --- NEW: Character Limit Check ---
                if len(value) > 50:
                    self.highlight_error("address", "Cannot exceed 50 characters.")
                    return False
                
                # --- NEW: Repetitive Character Check ---
                if len(set(value)) == 1:
                    self.highlight_error("address", "Cannot use all the same characters.")
                    return False


            elif key == "password":
                # --- PASSWORD VALIDATION (Existing Logic) ---
                if " " in value:
                    self.highlight_error("password", "Password cannot contain spaces.")
                    return False

                def is_secure_password(password):
                    return (
                        len(password) >= 8 and
                        re.search(r"[A-Z]", password) and
                        re.search(r"[a-z]", password) and
                        re.search(r"[0-9]", password) and
                        re.search(r"[@$!%*#?&]", password)
                    )

                if not is_secure_password(value):
                    # Condense multi-line error into a single placeholder message
                    error_msg = "Must be ≥ 8 chars and include: Uppercase, Lowercase, Number, and Symbol (@$!%*#?&)"
                    self.highlight_error("password", error_msg)
                    return False
            
            # If we are only validating a single key and we reach here, it passed.
            if key_to_validate:
                # The style was already reset at the start if it was a single validation check
                return True

        # If key_to_validate is None (SIGNUP button was pressed), and the loop finished, all checks passed.
        if not key_to_validate:
            return data # Return validated data dictionary
        
        # Fallback if single validation somehow didn't return above (shouldn't happen)
        return True 

    def register_user(self, data):
        cursor = connection.cursor()
        if not connection or not connection.is_connected():
            # Use global status label for DB connection error
            self.display_message("Connection not active, Registration Failed, try again")
            return False
        
        hashed_email = self.hash_email(data['email'])
        hashed_password = self.hashed_password(data['password'])
        input_email = data['email'].lower()
        assigned_role = "admin" if input_email == "admin@gmail.com" else "customer"
        
        try:
            cursor.execute("""
                INSERT INTO customers(first_name, last_name, email, phone_no, address)
                VALUES(%s, %s, %s, %s, %s)
            """, (data['first_name'], data['last_name'], hashed_email, data['phone_no'], data['address']))
            
            customer_id = cursor.lastrowid
            if not customer_id:
                raise mysql.connector.Error("Failed to retrieve new customer Id")

            cursor.execute("""
                INSERT INTO login(customer_id, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, (customer_id, hashed_email, hashed_password, assigned_role))
            
            connection.commit()
            self.display_message("Registration Successful!", is_error=False) 
            return True
        
        except mysql.connector.IntegrityError as e:
            if "Duplicate entry" in str(e) and "'email'" in str(e):
                # Highlight the email field specifically for duplicate email error
                self.highlight_error("email", "This email is already registered, Try Logging in.")
            else:
                self.display_message(f"Database Integrity Error: {e}")
            return False
        
        except mysql.connector.Error as err:
            self.display_message(f"Database error: {err}")
            return False
        
        finally:
            cursor.close()
    
    # ---------------- SIGNUP BUTTON ----------------
    def handle_signup(self):
        # validate_inputs now returns the data dictionary if successful, or False otherwise
        validated_data = self.validate_inputs() 
        
        if not validated_data:
            return
        
        success = self.register_user(validated_data)
        if success:
            self.after(1000, self.redirect_to_login)

    # ---------------- REDIRECT TO LOGIN ----------------
    def redirect_to_login(self, event=None):
        self.destroy()
        # Ensure login.py exists if you run this
        try:
            from login import LoginPage
            login_app = LoginPage()
            login_app.mainloop()
        except ImportError:
            print("Note: To redirect, you need a 'login.py' file containing a 'LoginPage' class.")

if __name__ == "__main__":
    app = SignupPage()
    app.mainloop()