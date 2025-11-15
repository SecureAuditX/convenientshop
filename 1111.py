import customtkinter as ctk

appWidth, appHeight = 950, 600

class App(ctk.CTk):
    def __init__(self, *args ,**kwargs):
        super().__init__(*args, **kwargs)
        self.title("Settings - Update Profile")
        self.geometry(f"{appWidth}x{appHeight}")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Title
        title = ctk.CTkLabel(self, text="Settings", font=("Arial", 18, "bold"))
        title.pack(pady=(25,5))

        # Main Frame 
        frame = ctk.CTkFrame(self, fg_color="#f8f9ff", corner_radius=15)
        frame.pack(padx=40, pady=(5,20), fill="both", expand=True)

        subtitle = ctk.CTkLabel(frame, text="Update Profile", font=("Arial", 15, "bold"))
        subtitle.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # Common settings
        label_font = ("Arial", 12)
        entry_width = 250
        entry_height = 35

        # ---------- First Row --------------
        # First Name
        ctk.CTkLabel(frame, text="First Name *", font=label_font, anchor="w").grid(
            row=1, column=0, padx=40, pady=(10, 5), sticky="w")
        ctk.CTkEntry(frame, placeholder_text="First Name", width=entry_width, height=entry_height).grid(
            row=2, column=0, padx=40, pady=(0, 10), sticky="w")

        # Last Name
        ctk.CTkLabel(frame, text="Last Name *", font=label_font, anchor="w").grid(
            row=1, column=1, padx=40, pady=(10, 5), sticky="w")
        ctk.CTkEntry(frame, placeholder_text="Last Name", width=entry_width, height=entry_height).grid(
            row=2, column=1, padx=40, pady=(0, 10), sticky="w")

        # ---------- Second Row --------------
        # Email
        ctk.CTkLabel(frame, text="Email *", font=label_font, anchor="w").grid(
            row=3, column=0, padx=40, pady=(10, 5), sticky="w")
        ctk.CTkEntry(frame, placeholder_text="Email", width=entry_width, height=entry_height).grid(
            row=4, column=0, padx=40, pady=(0, 10), sticky="w")

        # Phone
        ctk.CTkLabel(frame, text="Phone No *", font=label_font, anchor="w").grid(
            row=3, column=1, padx=40, pady=(10, 5), sticky="w")
        ctk.CTkEntry(frame, placeholder_text="Phone No", width=entry_width, height=entry_height).grid(
            row=4, column=1, padx=40, pady=(0, 10), sticky="w")

        # ---------- Second Row --------------
        # Address
        ctk.CTkLabel(frame, text="Address *", font=label_font, anchor="w").grid(
            row=5, column=0, padx=40, pady=(10, 5), sticky="w")
        ctk.CTkEntry(frame, placeholder_text="Address", width=entry_width, height=entry_height).grid(
            row=6, column=0, padx=40, pady=(0, 10), sticky="w")

        # Password
        ctk.CTkLabel(frame, text="Password *", font=label_font, anchor="w").grid(
            row=5, column=1, padx=40, pady=(10, 5), sticky="w")
        ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=entry_width, height=entry_height).grid(
            row=6, column=1, padx=40, pady=(0, 10), sticky="w")







        # Button 
        update_btn = ctk.CTkButton(
            frame,
            text="Update",
            fg_color="#1a4dff",
            hover_color="#0036c4",
            width=150,
            height=40,
            corner_radius=20
        )
        update_btn.grid(row=7, column=0, columnspan=2, pady=(25, 20))
        # Expand columns
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)


if __name__ == "__main__":
    app = App()
    app.mainloop()
