# admin_dashboard.py
# Admin Dashboard that embeds FinanceApp and ReportsApp using .grid() only

import os
import customtkinter as ctk
from PIL import Image, ImageTk

# import embeddable frames
from finance import FinanceApp
from reports import ReportsApp

IMAGE_BASE_DIR = r"C:\XFiles\CodingFile\Python\Desktop_App\convenientshop\images"

def image_path_join(*parts):
    candidate = os.path.join(*parts)
    if os.path.isabs(candidate):
        return candidate
    candidate2 = os.path.join(IMAGE_BASE_DIR, *parts[1:]) if len(parts) > 1 else os.path.join(IMAGE_BASE_DIR, parts[0])
    if os.path.exists(candidate2):
        return candidate2
    base = os.path.dirname(__file__)
    return os.path.join(base, *parts)

class AdminDashboard(ctk.CTk):
    def __init__(self, customer_id=None, email=None):
        super().__init__()
        self.customer_id = customer_id
        self.email = email

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.title("Admin Dashboard Management")
        self.geometry("1350x850")

        # grid config (no pack)
        self.grid_columnconfigure(0, weight=0)   # sidebar
        self.grid_columnconfigure(1, weight=1)   # main area
        self.grid_rowconfigure(0, weight=1)

        # sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color="#E6DEF6", width=240)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(99, weight=1)

        # profile
        profile_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        profile_frame.grid(row=0, column=0, pady=18, padx=12)
        try:
            p = image_path_join(IMAGE_BASE_DIR, "profile.png")
            img = Image.open(p).resize((72,72), Image.LANCZOS)
            self._profile_photo = ImageTk.PhotoImage(img)
            ctk.CTkLabel(profile_frame, image=self._profile_photo, text="").grid(row=0, column=0)
        except Exception:
            ctk.CTkLabel(profile_frame, text="👤", font=("Arial", 36)).grid(row=0, column=0)
        ctk.CTkLabel(profile_frame, text="Admin Dashboard", font=("Arial", 12, "bold")).grid(row=1, column=0, pady=(8,0))

        # buttons helper
        def add_btn(text, row, cmd, icon=None):
            img = None
            if icon:
                try:
                    p = image_path_join(IMAGE_BASE_DIR, icon)
                    img = Image.open(p).resize((18,18), Image.LANCZOS)
                    img = ImageTk.PhotoImage(img)
                except Exception:
                    img = None
            b = ctk.CTkButton(self.sidebar, text=text, image=img, compound="left",
                              fg_color="transparent", text_color="black",
                              hover_color="#D7D2F4", anchor="w", command=cmd, height=44)
            b.grid(row=row, column=0, sticky="ew", padx=14, pady=6)
            # keep reference so image not GC'd
            if img:
                b._icon = img
            return b

        add_btn("Home", 2, self.show_dashboard, "home.png")
        add_btn("Stock Management", 3, self.show_stock, "stock.png")
        add_btn("Finance", 4, self.show_finance, "finance.png")
        add_btn("Report", 5, self.show_reports, "report.png")
        add_btn("Announcement", 6, self.show_announcement, "announcement.png")
        add_btn("Users", 7, self.show_users, "users.png")
        add_btn("Setting", 8, self.show_settings, "setting.png")
        add_btn("Logout", 100, self.logout, "exit.png")

        # main area
        self.main_area = ctk.CTkFrame(self, fg_color="#F6F6F6")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=18, pady=18)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

        # content frames (blank frames to host embedded UIs)
        self.frames = {
            "dashboard": ctk.CTkFrame(self.main_area, fg_color="transparent"),
            "stock": ctk.CTkFrame(self.main_area, fg_color="transparent"),
            "finance": ctk.CTkFrame(self.main_area, fg_color="transparent"),
            "reports": ctk.CTkFrame(self.main_area, fg_color="transparent"),
            "announcement": ctk.CTkFrame(self.main_area, fg_color="transparent"),
            "users": ctk.CTkFrame(self.main_area, fg_color="transparent"),
            "settings": ctk.CTkFrame(self.main_area, fg_color="transparent"),
        }
        for f in self.frames.values():
            f.grid_columnconfigure(0, weight=1)
            f.grid_rowconfigure(0, weight=1)

        # show default
        self.show_dashboard()

    def _show_frame(self, name):
        for f in self.frames.values():
            f.grid_forget()
        frame = self.frames[name]
        frame.grid(row=0, column=0, sticky="nsew")

    def clear_frame_children(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def show_dashboard(self):
        self._show_frame("dashboard")
        f = self.frames["dashboard"]
        self.clear_frame_children(f)
        ctk.CTkLabel(f, text="Welcome to Admin Dashboard", font=("Arial", 22, "bold")).grid(row=0, column=0, padx=18, pady=18, sticky="nw")

    def show_stock(self):
        self._show_frame("stock")
        f = self.frames["stock"]
        self.clear_frame_children(f)
        ctk.CTkLabel(f, text="Stock Management (placeholder)", font=("Arial", 20)).grid(row=0, column=0, padx=18, pady=18, sticky="nw")

    def show_finance(self):
        self._show_frame("finance")
        f = self.frames["finance"]
        self.clear_frame_children(f)
        # embed FinanceApp frame (CTkFrame)
        finance_frame = FinanceApp(master=f)
        finance_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    def show_reports(self):
        self._show_frame("reports")
        f = self.frames["reports"]
        self.clear_frame_children(f)
        reports_frame = ReportsApp(master=f)
        reports_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    def show_announcement(self):
        self._show_frame("announcement")
        f = self.frames["announcement"]
        self.clear_frame_children(f)
        ctk.CTkLabel(f, text="Announcement (placeholder)", font=("Arial", 20)).grid(row=0, column=0, padx=18, pady=18, sticky="nw")

    def show_users(self):
        self._show_frame("users")
        f = self.frames["users"]
        self.clear_frame_children(f)
        ctk.CTkLabel(f, text="Users (placeholder)", font=("Arial", 20)).grid(row=0, column=0, padx=18, pady=18, sticky="nw")

    def show_settings(self):
        self._show_frame("settings")
        f = self.frames["settings"]
        self.clear_frame_children(f)
        ctk.CTkLabel(f, text="Settings (placeholder)", font=("Arial", 20)).grid(row=0, column=0, padx=18, pady=18, sticky="nw")

    def logout(self):
        self.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = AdminDashboard()
    app.mainloop()
