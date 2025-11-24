from db_file import Database
import customtkinter as ctk
from PIL import Image, ImageTk
import os

# Database connection 


class AdminDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title("Admin Dashbaord Management")
        self.geometry("1200x800")
        self.resizable(True, True)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Configure Grid Layout for main window
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        
        

        
if __name__ == '__main__':
    app = AdminDashboard()
    app.mainloop()