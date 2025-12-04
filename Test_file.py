from db_file import Database
from db_file import db
import customtkinter as ctk
from PIL import Image, ImageTk
import hashlib
import bcrypt
import os
import mysql.connector
from CTkMessagebox import CTkMessagebox

# Database connection
db = Database()
connection = db.DB_Connection()

class SignupPage(ctk.CTk):
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
        self.FRAME_COLOR = "#E0DDF0"        
        
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
        
        # Logo frame
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
        for idx, (label_text, key, placeholder) in enumerate(fields):
            is_password = key == "password"
            
            base_text = label_text.rstrip('*') # Get the text part (e.g., "FIRST NAME")
            has_asterisk = label_text.endswith('*')
            
            # Create a transparent frame to hold the label and asterisk side-by-side
            label_container = ctk.CTkFrame(self.signup_frame, fg_color="transparent")
            label_container.grid(row=idx*2+1, column=0, padx=40, pady=(0, 2), sticky="w")
            
            # Label for the main text (Original color: #4F46E5)
            base_label = ctk.CTkLabel(label_container, text=base_text, font=("Arial", 14, "bold"), text_color="#4F46E5", anchor="w")
            base_label.grid(row=0, column=0, sticky="w")
            
            # Label for the asterisk (RED color)
            if has_asterisk:
                asterisk_label = ctk.CTkLabel(label_container, text="*", font=("Arial", 14, "bold"), text_color="red", anchor="w")
                # Add a small pad to keep it close to the text
                asterisk_label.grid(row=0, column=1, sticky="w", padx=(1, 0))
            
            # Entries
            entry = ctk.CTkEntry(self.signup_frame, placeholder_text=placeholder, show="*" if is_password else "", 
                                 width=300, height=40, font=("Arial", 16), fg_color=self.PRIMARY_COLOR,
                                 text_color="white", placeholder_text_color=self.FRAME_COLOR,
                                 border_color=self.PRIMARY_COLOR, corner_radius=10)
            entry.grid(row=idx*2+2, column=0, padx=40, pady=(0, 2), sticky="w")
            self.input_entries[key] = entry
            
        # Status Label for messages
        self.status_label = ctk.CTkLabel(self.signup_frame, text="", text_color="red", font=("Arial", 14))
        self.status_label.grid(row=len(fields)*2+1, column=0, padx=40, pady=(10, 20), sticky="w")
        
        # Signup Button
        self.signup_button = ctk.CTkButton(self.signup_frame, text="SIGNUP", font=("Arial", 20, "bold"), 
                                           command=self.handle_signup,
                                           width=300, height=40,
                                           fg_color="#4F46E5", hover_color="#3B34C4",
                                           text_color="white", corner_radius=50)
        self.signup_button.grid(row=len(fields)*2+2, column=0, padx=40, pady=(0, 1))
        self.signup_frame.grid_anchor("center")
        
        # Already have account (Login)
        link_frame = ctk.CTkFrame(self.signup_frame, fg_color="transparent")
        link_frame.grid(row=len(fields)*2+3, column=0, pady=(10, 50), padx=40)

        self.login_label = ctk.CTkLabel(link_frame, text="Already Have an Account?", 
                                             font=("Arial", 14), text_color="#4F46E5")
        self.login_label.grid(row=0, column=0, padx=(0, 5))
        
        self.login_link = ctk.CTkLabel(link_frame, text="Login", font=("Arial", 14, "underline"), text_color="#4F46E5", cursor="hand2")
        self.login_link.grid(row=0, column=1)
        self.login_link.bind("<Button-1>", self.redirect_to_login)     
        
    # ---------------- ENCRYPTIONS ----------------
    def hash_email(self, email):
        return hashlib.sha256(email.lower().encode('utf-8')).hexdigest()
    
    def hashed_password(self, password):
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_bytes.decode('utf-8') 

    def validate_inputs(self, data):
        """Validate all required fields and input formats"""

        import re
        from CTkMessagebox import CTkMessagebox

        #  EMPTY FIELDS CHECK
        for key, value in data.items():
            if not value.strip():
                CTkMessagebox(title="Error", 
                              message=f"Please enter your {key.replace('_', ' ')}.", 
                              icon="cancel")
                return False

        #  FIRST & LAST NAME VALIDATION
        name_pattern = r"^[A-Za-z]+$"

        # Check letters only
        if not re.match(name_pattern, data["first_name"]):
            CTkMessagebox(title="Error", 
                          message="First name must contain only letters (A–Z).", 
                          icon="cancel")
            return False

        if not re.match(name_pattern, data["last_name"]):
            CTkMessagebox(title="Error", 
                          message="Last name must contain only letters (A–Z).", 
                          icon="cancel")
            return False

        # Prevent repeated characters (aaa, bbbbb, zzzzzz)
        if len(set(data["first_name"].lower())) == 1:
            CTkMessagebox(title="Error", 
                          message="First name cannot be all the same letter.", 
                          icon="cancel")
            return False

        if len(set(data["last_name"].lower())) == 1:
            CTkMessagebox(title="Error", 
                          message="Last name cannot be all the same letter.", 
                          icon="cancel")
            return False
        
        email = data["email"].strip()

        # EMAIL VALIDATION
        email_pattern = (
            r"^[a-zA-Z0-9._%+-]+"       # Name part
            r"@"                        
            r"[a-zA-Z0-9.-]+\."         # Domain name (gmail, yahoo, school emails, etc.)
            r"[A-Za-z]{2,}$"            # TLD (.com, .org, .edu, .cn, .jp)
        )

        if not re.match(email_pattern, email):
            CTkMessagebox(
                title="Error",
                message="Invalid email format. Example: name@example.com",
                icon="cancel"
            )
            return False

        phone = data["phone_no"].strip()

        # PHONE NUMBER VALIDATION
        # Digits only
        if not phone.isdigit():
            CTkMessagebox(title="Error",
                          message="Phone number must contain only digits (0–9).",
                          icon="cancel")
            return False

        # Must be 11 digits
        if len(phone) != 11:
            CTkMessagebox(title="Error",
                          message="Phone number must be exactly 11 digits.",
                          icon="cancel")
            return False
        # Cannot be repeating digits (e.g., 11111111111)
        if len(set(phone)) == 1:
            CTkMessagebox(title="Error",
                          message="Phone number cannot be all the same digit.",
                          icon="cancel")
            return False

        password = data["password"]

        # PASSWORD VALIDATION
        if " " in password:
            CTkMessagebox(title="Error",
                          message="Password cannot contain spaces.",
                          icon="cancel")
            return False

        def is_secure_password(password):
            return (
                len(password) >= 8 and
                re.search(r"[A-Z]", password) and
                re.search(r"[a-z]", password) and
                re.search(r"[0-9]", password) and
                re.search(r"[@$!%*#?&]", password)
            )

        if not is_secure_password(password):
            CTkMessagebox(
                title="Error",
                message="Password must be ≥ 8 characters and include:\n"
                        "- Uppercase letter\n"
                        "- Lowercase letter\n"
                        "- Number\n"
                        "- Special symbol (@$!%*#?&)",
                icon="cancel"
            )
            return False
        return True

    def register_user(self, data):
        cursor = connection.cursor()
        if not connection or not connection.is_connected():
            CTkMessagebox(title="Error", message="Connection not active, Registration Failed, try again", icon="cancel")
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
            CTkMessagebox(title="Success", message="Registration Successful!", icon="check")
            return True
        
        except mysql.connector.IntegrityError as e:
            if "Duplicate entry" in str(e) and "'email'" in str(e):
                CTkMessagebox(title="Error", message="This email is already registered, Try Logging in.", icon="cancel")
            else:
                CTkMessagebox(title="Error", message=f"Database Integrity Error: {e}", icon="cancel")
            return False
        
        except mysql.connector.Error as err:
            CTkMessagebox(title="Error", message=f"Database error: {err}", icon="cancel")
            return False
        
        finally:
            cursor.close()
    
    # ---------------- SIGNUP BUTTON ----------------
    def handle_signup(self):
        data = {key: entry.get() for key, entry in self.input_entries.items()}
        if not self.validate_inputs(data):
            return
        
        success = self.register_user(data)
        if success:
            self.after(1000, self.redirect_to_login)

    # ---------------- REDIRECT TO LOGIN ----------------
    def redirect_to_login(self, event=None):
        self.destroy()
        from login import LoginPage
        login_app = LoginPage()
        login_app.mainloop()

if __name__ == "__main__":
    app = SignupPage()
    app.mainloop()