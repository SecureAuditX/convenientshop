import customtkinter as ctk
from PIL import Image, ImageTk
from admin_announcement import AnnouncementUI
from admin_setting import AdminSettingsApp 
import os

# Database connection is handled by the global 'db' instance from db_file

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

IMAGE_BASE_DIR = r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop\images"

class AdminDashboard(ctk.CTk):
    def __init__(self, customer_id, email):
        super().__init__()
        self.customer_id = customer_id
        self.email = email
        
        # Window Configuration
        self.title("Admin Dashbaord Management")
        self.geometry("1200x800")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Configure Grid Layout for main window
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar_frame = ctk.CTkFrame(self, fg_color="#E0DDF0", corner_radius=10) #D8DBF7
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
            
        self.username_label = ctk.CTkLabel(self.profile_frame, text="Admin Dashboard", font=("Arial", 14, "bold"), text_color="black")
        self.username_label.grid(row=1, column=0, padx=10, pady=5)
        
        self.dashboard_button = ctk.CTkButton(self.sidebar_frame, text="Home",
                                              fg_color="transparent", text_color="black",
                                              hover_color="#D7D2F4", font=("Arial", 16, "bold"),
                                              anchor="w", image=self.load_icon("home.png", 20),
                                              compound="left", command=self.show_dashboard_content,
                                              width=150, height=50) 
        self.dashboard_button.grid(row=2, column=0, padx=10, pady=8, sticky="ew") 
        
        self.stock_button = ctk.CTkButton(self.sidebar_frame, text="Stock", 
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
        self.finance_button.grid(row=4, column=0, sticky="ew", pady=8, padx=10) # Adjusted row to 4
        
        self.report_button = ctk.CTkButton(self.sidebar_frame, text="Report", 
                                        fg_color="transparent", text_color="black", 
                                        hover_color="#D7D2F4", font=("Arial", 16), 
                                        anchor="w", image=self.load_icon("report.png", 20),
                                        compound="left", command=self.show_report_content,
                                        width=150, height=50)
        self.report_button.grid(row=5, column=0, sticky="ew", pady=8, padx=10) # Adjusted row to 5
        
        self.announcement_button = ctk.CTkButton(self.sidebar_frame, text="Announcement", 
                                             fg_color="transparent", text_color="black",
                                             hover_color="#D7D2F4", font=("Arial", 16), 
                                             anchor="w", image=self.load_icon("announcement.png", 20), 
                                             compound="left", command=self.show_announcement_content,
                                             width=150, height=50)
        self.announcement_button.grid(row=6, column=0, sticky="ew", pady=8, padx=10) # Adjusted row to 6

        self.user_button = ctk.CTkButton(self.sidebar_frame, text="Users", 
                                             fg_color="transparent", text_color="black",
                                             hover_color="#D7D2F4", font=("Arial", 16), 
                                             anchor="w", image=self.load_icon("users.png", 20), 
                                             compound="left", command=self.show_users_content,
                                             width=150, height=50)
        self.user_button.grid(row=7, column=0, sticky="ew", pady=8, padx=10) # Adjusted row to 7

        self.setting_button = ctk.CTkButton(self.sidebar_frame, text="Setting", 
                                             fg_color="transparent", text_color="black",
                                             hover_color="#D7D2F4", font=("Arial", 16), 
                                             anchor="w", image=self.load_icon("setting.png", 20), 
                                             compound="left", command=self.show_setting_content,
                                             width=150, height=50)
        self.setting_button.grid(row=8, column=0, sticky="ew", pady=8, padx=10) # Adjusted row to 8
        
        #  Logout Button 
        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Logout", 
                                         fg_color="transparent", text_color="black",
                                         hover_color="#D7D2F4", font=("Arial", 16), 
                                         anchor="w", image=self.load_icon("exit.png", 20), 
                                         compound="left", command=self.logout,
                                         width=150, height=50)
        self.logout_button.grid(row=15, column=0, sticky="ew", pady=(10, 20), padx=10)
        
        
        # Main Content Area (Right panel)
        self.main_content_area = ctk.CTkFrame(self, fg_color="#F7F7F7", corner_radius=0)
        self.main_content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content_area.grid_columnconfigure(0, weight=1) # Center content horizontally
        self.main_content_area.grid_rowconfigure(0, weight=1)
        
        
        # Content Frames for different sections (These must be persistent and are never destroyed)
        self.dashboard_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.stock_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.finance_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.report_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.announcement_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.users_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.setting_content_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        
        self.show_dashboard_content()
        
    def load_icon(self, icon_name, size):
        # Re-using the user's robust icon loading logic
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
        return None # Return None if not found
        
    def hide_all_content_frames(self):
        """Hides all persistent content frames from the main content area using grid_forget()."""
        frames = [
            self.dashboard_content_frame, self.stock_content_frame, self.finance_content_frame,
            self.report_content_frame, self.announcement_content_frame, self.users_content_frame,
            self.setting_content_frame
        ]
        for frame in frames:
            # We only use grid_forget() to ensure the frames themselves are never destroyed.
            frame.grid_forget()

    def set_sidebar_button_active(self, active_button):
        # Sets the active state for sidebar buttons.
        buttons = [self.dashboard_button, self.stock_button, self.finance_button,
                   self.report_button, self.announcement_button, self.user_button,
                   self.setting_button]
        for button in buttons:
            if button == active_button:
                button.configure(fg_color="#F7F7F9")
            else:
                button.configure(fg_color="transparent")
                
    # Content Display Functions 
    
    def show_dashboard_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.dashboard_button)
        for w in self.dashboard_content_frame.winfo_children(): w.destroy()
        self.dashboard_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        ctk.CTkLabel(self.dashboard_content_frame, text="Admin Home Dashboard Content", font=("Arial", 24, "bold"), text_color="black").pack(padx=10, pady=10)
        
    def show_stock_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.stock_button) 
        for w in self.stock_content_frame.winfo_children(): w.destroy() 
        self.stock_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        ctk.CTkLabel(self.stock_content_frame, text="Stock Management Content", font=("Arial", 24, "bold"), text_color="black").pack(padx=10, pady=10)
        
    def show_finance_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.finance_button)
        for w in self.finance_content_frame.winfo_children(): w.destroy()
        self.finance_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        ctk.CTkLabel(self.finance_content_frame, text="Finance Content", font=("Arial", 24, "bold"), text_color="black").pack(padx=10, pady=10)
        
    def show_report_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.report_button)
        for w in self.report_content_frame.winfo_children(): w.destroy() 
        self.report_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        ctk.CTkLabel(self.report_content_frame, text="Report Content", font=("Arial", 24, "bold"), text_color="black").pack(padx=10, pady=10)
        
    def show_announcement_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.announcement_button)
        
        # Clear children of the dedicated frame
        for w in self.announcement_content_frame.winfo_children():
            w.destroy()

        # Grid the dedicated frame into the main content area
        self.announcement_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Instantiate and display the new AnnouncementUI inside the dedicated frame
        # NOTE: If AnnouncementUI is a CTkFrame, we use pack/grid inside the parent frame.
        announcement_ui = AnnouncementUI(self.announcement_content_frame) 
        announcement_ui.pack(fill="both", expand=True) 
        
    def show_users_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.user_button)
        for w in self.users_content_frame.winfo_children(): w.destroy() 
        self.users_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        ctk.CTkLabel(self.users_content_frame, text="Users Management Content", font=("Arial", 24, "bold"), text_color="black").pack(padx=10, pady=10)
        
    def show_setting_content(self):
        self.hide_all_content_frames()
        self.set_sidebar_button_active(self.setting_button)
        
        # 1. Clear existing content in the dedicated frame
        for w in self.setting_content_frame.winfo_children(): 
            w.destroy()
            
        # 2. Grid the dedicated frame into the main content area
        self.setting_content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # 3. Instantiate and pack the AdminSettingsApp into the dedicated frame
        settings_app = AdminSettingsApp(
            parent_frame=self.setting_content_frame, 
            customer_id=self.customer_id, 
            email=self.email 
        )
        settings_app.pack(fill="both", expand=True) # Use pack for AdminSettingsApp
        
    def logout(self):
        #Handles user logout.
        self.destroy()
        import login
        login_app = login.LoginPage()
        login_app.mainloop() 
    
if __name__ == '__main__':
    # Placeholder values for demonstration
    app = AdminDashboard(customer_id=None, email="admin@shop.com") 
    app.mainloop()