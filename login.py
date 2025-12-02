from db_file import db
import customtkinter as ctk
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
import bcrypt
import hashlib
import subprocess
import sys
import os

connection = db.DB_Connection()
MAX_LOGIN_ATTEMPTS = 3

class LoginPage(ctk.CTk):

    def __init__(self):
        super().__init__()
    
        # Login Window Configuration
        self.title("Login Page")
        self.geometry("900x800")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        
        self.main_frame = ctk.CTkFrame(self, fg_color = "#A4A4EB", corner_radius = 10)
        self.main_frame.pack(expand=True, fill="both", pady=50, padx=50)
        
        # this create two conceptual columns (left for logo, right for login form)
        self.main_frame.grid_columnconfigure(0, weight=1) # left side
        self.main_frame.grid_columnconfigure(1, weight=1) # right side
        self.main_frame.grid_rowconfigure(0, weight=1) # center vertically
        
        # Left branding frame
        self.left_branding_frame = ctk.CTkFrame(self.main_frame, fg_color="#A4A4EB")
        self.left_branding_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.left_branding_frame.grid_columnconfigure(0, weight=1)
        self.left_branding_frame.grid_rowconfigure(0, weight=1)
        
        # Load and displaying the logo image
        try:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_directory, "logo.png")
            
            original_image = Image.open(image_path)
            resized_image = original_image.resize((230, 230), Image.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_image)
        
            # Left Logo
            self.logo_label = ctk.CTkLabel(self.left_branding_frame, image=self.logo_image, text="")
            self.logo_label.grid(row=0, column=0, pady=(10, 10))
        
        except FileNotFoundError:
            self.logo_label = ctk.CTkLabel(self.left_branding_frame, text="Logo Not Found", font=("Arial", 18, "bold"), text_color ="#4F46E5")
            self.logo_label.grid(row=0, column=0, rowspan=2, padx=20, pady=20)
            
        
        # Login Form
        self.login_frame = ctk.CTkFrame(self.main_frame, fg_color="#E0DDF0", corner_radius =20, width=380, height=520)
        self.login_frame.grid(row=0, column=1, sticky="nsew", padx=80, pady=80)
        # centering the login form
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.pack_propagate(False)
        
        # Login Title
        self.login_title = ctk.CTkLabel(self.login_frame, text="LOGIN", font=("Arial", 36, "bold"), text_color="#4F46E5")
        self.login_title.pack(pady=(40, 40))
        
        # Email Label and Entry
        self.email_label = ctk.CTkLabel(self.login_frame, text="EMAIL", font=("Arial", 14, "bold"), text_color="#4F46E5", anchor ="w")
        self.email_label.pack(fill="x", padx=76, pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(self.login_frame, 
                                        placeholder_text="example@gmail.com",
                                        font=("Arial", 16), width=250, 
                                        height=45, fg_color="#4F46E5", 
                                        text_color="white", 
                                        placeholder_text_color="#E0DDF0", 
                                        border_color="#4F46E5", 
                                        corner_radius=10)
        self.email_entry.pack(padx=40, pady=(0, 10))
        
        # Password Label and Entry
        self.password_label = ctk.CTkLabel(self.login_frame, text="PASSWORD", font=("Arial", 14, "bold"), text_color="#4F46E5", anchor="w")
        self.password_label.pack(fill="x", padx=76, pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(self.login_frame,
                                           placeholder_text="enter password",
                                           font=("Arial", 16), width =250,
                                           height=45, fg_color="#4F46E5",
                                           text_color="white", show="*",
                                           placeholder_text_color="#E0DDF0",
                                           border_color="#4F46E5",
                                           corner_radius=10)
        self.password_entry.pack(padx=40, pady=(0, 2))
        
        # Forgot Password Link
        self.forget_label = ctk.CTkLabel(self.login_frame, text="Forget Password?",
                                         font=("Arial", 12, "underline"), text_color="#4F46E5", cursor="hand2")
        self.forget_label.pack(padx=(0, 80), pady=(0, 10), anchor="e")
        
        # Login Button
        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.handle_login,
                                          width=250, height=45, font=("Arial", 20, "bold"),
                                          fg_color="#4F46E5", hover_color="#4338CA",
                                          text_color="white", corner_radius=50)
        self.login_button.pack(padx=40, pady=(0, 5))
        
        # Create new account link (Register)
        link_frame = ctk.CTkFrame(self.login_frame,  fg_color="transparent")
        link_frame.pack(pady=(0, 10))
        
        self.register_label = ctk.CTkLabel(link_frame, text="Don't have an account?", 
                                           font=("Arial", 14), text_color="#4F46E5")
        self.register_label.pack(side="left", padx=(0, 5))
        
        self.register_link = ctk.CTkLabel(link_frame, text ="Register", font=("Arial", 14, "underline"), text_color="#4F46E5", cursor="hand2")
        self.register_link.pack(side="left")
        
        # Bind click event
        self.register_link.bind("<Button-1>", self.open_signup)
        
        # Status label for message
        self.status_label = ctk.CTkLabel(self.login_frame, text="", text_color="red", font=("Arial", 14))
        self.status_label.pack(pady=(0, 10))
        
    # Email Encryption
    def hash_email(self, email):
        """ Hashing email with SHA-256 """
        return hashlib.sha256(email.lower().encode('utf-8')).hexdigest()

    #  Recording Error Login Attempt
    def update_login_attempts(self, hashed_email, attempts, is_locked):
        """Uodates the error login attempt count and lock user account"""
        cursor = connection.cursor()
        cursor.execute("""
                   UPDATE login SET error_login_attempt = %s, is_locked = %s WHERE email = %s
                   """,(attempts, is_locked, hashed_email))
        connection.commit()
        cursor.close()
    
    # Role based access control
    def open_admin_dashboard(self, customer_id, email):
       """Placeholder for opening the Admin dashboard"""
       self.status_label.configure(text="Redirecting to Admin Dashboard...", text_color="green")
       
       self.destroy()
       import admin_dashboard
       admin_app = admin_dashboard.AdminDashboard(customer_id=customer_id, email=email)
       admin_app.mainloop()
    
    def open_user_dashboard(self, customer_id, email):
        """Open customer dashboard with correct customer_id"""
        self.destroy()
        import user_dashboard
        user_dashboard.UserDashboard(customer_id=customer_id, email=email).mainloop()

    
    # User Authentication & Authorization
    def handle_login(self):
        """Process login with security check and RBAC"""
        input_email = self.email_entry.get()
        input_password = self.password_entry.get()
        
        if not input_email or not input_password:
            CTkMessagebox(title="Error", message="Email and Password cannot be empty", icon="cancel")
            return

        hashed_input_email = self.hash_email(input_email)

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT customer_id, password, error_login_attempt, is_locked, role
            FROM login
            WHERE email = %s
        """, (hashed_input_email,))
        
        user_record = cursor.fetchone()
        cursor.close()

        if not user_record:
            CTkMessagebox(title="Error", message="Invalid Credentials", icon="cancel")
            return

        stored_password_hash = user_record["password"]
        customer_id = user_record["customer_id"]   # IMPORTANT FIX
        current_attempts = user_record["error_login_attempt"]
        is_locked = user_record["is_locked"]
        user_role = user_record["role"]

        # Account locked
        if is_locked == 1:
            CTkMessagebox(title="Error", message="Account is locked, contact admin.", icon="cancel")
            return

        # Password verification
        try:
            password_matches = bcrypt.checkpw(input_password.encode('utf-8'), stored_password_hash.encode('utf-8'))
        except ValueError:
            CTkMessagebox(title="Error", message="System error, contact support.", icon="cancel")
            return

        # LOGIN SUCCESS
        if password_matches:
            # reset attempts
            if current_attempts > 0:
                self.update_login_attempts(hashed_input_email, 0, 0)

            if user_role.lower() == "admin":
                self.open_admin_dashboard(customer_id=customer_id, email=input_email )
            else:
                #  pass customer_id to dashboard
                self.logged_in_email = input_email    # REAL EMAIL
                self.logged_in_customer_id = customer_id

                self.open_user_dashboard(customer_id, self.logged_in_email)
            return

        # LOGIN FAILED
        new_attempts = current_attempts + 1
        new_is_locked = 1 if new_attempts >= MAX_LOGIN_ATTEMPTS else 0

        self.update_login_attempts(hashed_input_email, new_attempts, new_is_locked)

        if new_is_locked:
            self.status_label.configure(
                text=f"Maximum login attempts reached. Account LOCKED.",
                text_color="red"
            )
        else:
            remaining = MAX_LOGIN_ATTEMPTS - new_attempts
            self.status_label.configure(
                text=f"Invalid Credentials. {remaining} attempts remaining."
            )

    # Sign up page 
    def open_signup(self, event = None):
        """Close login page and open sign up when "Register" link is clicked"""
        self.destroy()
        python = sys.executable
        script_path = os.path.join(os.path.dirname(__file__), "signup.py") 
        subprocess.Popen([python, script_path])        

if __name__ == "__main__":
    
    app = LoginPage()
    app.mainloop()