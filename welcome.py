# Welcome page
import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk #for error message display 
import os # for dir lookup

class WelcomePage(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # setup main window
        self.title("Welcome to Brightview Provision")
        self.geometry("800x700") # size of the window
        self.resizable(False, False) # window not resizable
        ctk.set_appearance_mode("light") #set theme to light mode
        ctk.set_default_color_theme("green")
        
        # Main frame for content
        self.main_frame = ctk.CTkFrame(self, fg_color="#A4A4EB", corner_radius = 10)
        self.main_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Welcome text
        self.welcome_label = ctk.CTkLabel(self.main_frame, text = "Welcome to", font=("Arial", 36, "bold"), text_color = "#4F46E5")
        self.welcome_label.pack(pady=(80, 5))
        
        # Load and display the logo image
        try:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_directory, "logo.png")
            
            original_image = Image.open(image_path)
            resized_image = original_image.resize((250, 250), Image.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_image)

            self.logo_label = ctk.CTkLabel(self.main_frame, image =self.logo_image, text ="")
            self.logo_label.pack(pady =(20))        
        
        except FileNotFoundError:
            print("Error: Logo not found")
            self.logo_label = ctk.CTkLabel(self.main_frame, text="Logo Not Found", font=("Arial", 24, "bold"), text_color="red")
            self.logo_label.pack(pady=(50, 20))
            
        # "Get Started" Button
        self.get_started_btn = ctk.CTkButton(self.main_frame, text="Get Started",
                                             font=("Arial", 20, "bold"), 
                                             text_color ="black",
                                             command=self.open_login_page,
                                             width=150, height=50,
                                             fg_color = "#4CAF50",
                                             hover_color = "#45A049",
                                             corner_radius = 50 
                                             )
        self.get_started_btn.pack(pady=(20, 50))
        
       
    def open_login_page(self):
        """function to called when the "Get Started" button is clicked"""
        self.destroy() # close the current welcome window
    
        try:
            import login
            login_app = login.LoginPage()
            login_app.mainloop()
        except ImportError:
            print("Error: 'Login.py' Not Found")
            tk.messagebox.showerror("Error", "Cloud not load the login page")        

if __name__ == "__main__":            

    app = WelcomePage()
    app.mainloop()