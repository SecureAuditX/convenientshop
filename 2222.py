import customtkinter as ctk

appWidth, appHeight = 950, 600

class App(ctk.CTk):
    def __init__(self, *args ,**kwargs):
        super().__init__(*args, **kwargs)
        self.title("Order History")
        self.geometry(f"{appWidth}x{appHeight}")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Main Frame 
        frame = ctk.CTkFrame(self, fg_color="#f8f9ff", corner_radius=15)
        frame.pack(padx=40, pady=(10,20), fill="both", expand=True)
        frame.grid_columnconfigure(0, weight=1)

        # Search Bar
        self.search_bar = ctk.CTkEntry(
            frame,
            placeholder_text="Search",
            height=35,
            width=900,
            corner_radius=15,
            fg_color="#d8d4f4",
            text_color="black",
            justify="center"
        )
        self.search_bar.grid(row=0, column=0, pady=(20,10))

        # Content Wrapper
        content_frame = ctk.CTkFrame(frame, fg_color="#f8f9ff")
        content_frame.grid(row=1, column=0, sticky="n")
        content_frame.grid_columnconfigure(0, weight=1)

        # Title
        subtitle = ctk.CTkLabel(content_frame, text="Order History", font=("Arial", 18, "bold"))
        subtitle.grid(row=0, column=0, pady=(10, 10), sticky="w")

        # Orders Container
        self.orders_frame = ctk.CTkFrame(content_frame, fg_color="#e1e2fa", corner_radius=15)
        self.orders_frame.grid(row=1, column=0, pady=(0,20), sticky="nsew")
        content_frame.grid_rowconfigure(1, weight=1)

        # Define consistent column widths
        self.column_widths = [100, 200, 50, 150, 180, 80]
        self.headers = ["ORDER NO", "ADDRESS", "Qty", "DELIVERY STATUS", "TIME", "TOTAL"]

        # Header 
        header_frame = ctk.CTkFrame(self.orders_frame, fg_color="#d4d5f7", corner_radius=10)
        header_frame.pack(fill="x", pady=(10, 0), padx=10)

        for i, (h, w) in enumerate(zip(self.headers, self.column_widths)):
            lbl = ctk.CTkLabel(header_frame, text=h, font=("Arial", 12, "bold"), anchor="w", width=w)
            lbl.grid(row=0, column=i, padx=(10 if i == 0 else 5, 5), pady=8, sticky="w")

        #  Example Orders
        self.orders = [
            ["#892842", "543 Main St", "x3", "Pending", "2025-09-21 20:34", "$25.49"],
            ["#892842", "468 Main St", "x6", "Delivered", "2025-09-21 20:34", "$32.55"],
            ["#892842", "543 Main St", "x6", "Delivered", "2025-09-21 20:34", "$32.55"],
            ["#555555", "New Address", "x4", "Pending", "2025-10-12 18:20", "$28.90"]
        ]

        self.display_orders()

    def display_orders(self):
        # Remove previous order cards (keep header)
        for widget in self.orders_frame.winfo_children()[1:]:
            widget.destroy()

        for order in self.orders:
            order_card = ctk.CTkFrame(self.orders_frame, fg_color="#f4f4ff", corner_radius=10)
            order_card.pack(fill="x", padx=10, pady=8)

            for i, (val, w) in enumerate(zip(order, self.column_widths)):
                color = "orange" if val == "Pending" else ("#2f7a2f" if val == "Delivered" else "black")
                lbl = ctk.CTkLabel(order_card, text=val, font=("Arial", 12), text_color=color, anchor="w", width=w)
                lbl.grid(row=0, column=i, padx=(10 if i == 0 else 5, 5), pady=8, sticky="w")

    def add_order(self, order_data):
        self.orders.append(order_data)
        self.display_orders()


if __name__ == "__main__":
    app = App()
    app.mainloop()
