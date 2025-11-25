import customtkinter as ctk
from db_file import db  # Import the existing database connection

# Set global appearance settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class App(ctk.CTkFrame):
  
    def __init__(self, parent_frame, customer_id, email):
        # The main App frame will now have the light background and rounded corners
        # that the old inner 'frame' had.
        super().__init__(parent_frame, fg_color="#f8f9ff", corner_radius=15)
        
        # Store customer_id for database queries
        self.customer_id = customer_id
        self.email = email
        
        # Configure this frame (App) to allow content expansion
        self.grid_rowconfigure(2, weight=1) # Row 2 (Orders Container) is configured to expand vertically
        self.grid_columnconfigure(0, weight=1)

        # Note: All widgets are now children of 'self', not 'frame'

        # ----------------------------------------------------
        # 1. Search Bar (Row 0)
        # ----------------------------------------------------
        self.search_bar = ctk.CTkEntry(
            self,  # Direct child of App(self)
            placeholder_text="Search",
            height=35,
            corner_radius=15,
            fg_color="#d8d4f4",
            text_color="black",
            justify="center",
            font=("Arial", 14)
        )
        self.search_bar.grid(row=0, column=0, padx=20, pady=(20,10), sticky="ew")

        # ----------------------------------------------------
        # 2. Title (Row 1)
        # ----------------------------------------------------
        subtitle = ctk.CTkLabel(self, # Direct child of App(self)
                                 text="Order History", 
                                 font=("Arial", 18, "bold"),
                                 text_color="black")
        subtitle.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="w")

        # ----------------------------------------------------
        # 3. Orders Container (Scrollable) (Row 2)
        # ----------------------------------------------------
        self.orders_frame = ctk.CTkScrollableFrame(self, # Direct child of App(self)
                                                     fg_color="#e1e2fa", 
                                                     corner_radius=15)
        self.orders_frame.grid(row=2, column=0, padx=20, pady=(0,20), sticky="nsew")
        
        # Configure internal grid of the scrollable frame
        self.orders_frame.grid_columnconfigure(0, weight=1)

        # Define consistent column widths and headers
        self.column_widths = [100, 250, 50, 150, 180, 80]
        self.headers = ["ORDER NO", "ADDRESS", "QTY", "DELIVERY STATUS", "TIME", "TOTAL"]

        # ----------------------------------------------------
        # 4. Header Labels (Directly in orders_frame at Row 0)
        # ----------------------------------------------------
        # Create a light frame just for the header background
        header_bg = ctk.CTkFrame(self.orders_frame, fg_color="#d4d5f7", corner_radius=10)
        header_bg.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        # Configure columns inside the temporary background frame to match the data columns
        for i, w in enumerate(self.column_widths):
            header_bg.grid_columnconfigure(i, weight=0, minsize=w)

        for i, h in enumerate(self.headers):
            # Place the header labels inside the header_bg frame
            lbl = ctk.CTkLabel(header_bg, text=h, font=("Arial", 12, "bold"), anchor="w", text_color="#1a1a1a")
            lbl.grid(row=0, column=i, padx=(15 if i == 0 else 5, 5), pady=8, sticky="w")

        # Initialize orders from database
        self.orders = []
        self.load_orders_from_db()

        # Display orders
        self.display_orders()

    def load_orders_from_db(self):
        """Load orders from the order_history table in the database for the specific customer"""
        try:
            if self.customer_id:
                print(f"[DEBUG] self.customer_id = {self.customer_id} ({type(self.customer_id)})")
                # SQL query to fetch order history data for specific customer
                query = """
                SELECT 
                    order_no, 
                    address, 
                    quantity, 
                    delivery_status, 
                    time, 
                    total 
                FROM order_history 
                WHERE customer_id = %s
                ORDER BY time DESC
                """
                
                # Execute query with customer_id parameter
                results = db.fetchall(query, (self.customer_id,))
                print(f"[DEBUG] Fetched results: {results}")  # Debugging query result
            else:
                # SQL query to fetch all order history data
                query = """
                SELECT 
                    order_no, 
                    address, 
                    quantity, 
                    delivery_status, 
                    time, 
                    total 
                FROM order_history 
                ORDER BY time DESC
                """
                
                # Execute query without parameters
                results = db.fetchall(query)
                print(f"Fetched results: {results}")  # Debugging query result
            
            # Check if results are empty
            if not results:
                print(f"No orders found for customer_id {self.customer_id}")
                return
                
            # Clear existing orders
            self.orders = []
            
            # Process each row from the database
            for row in results:
                print(f"Processing row: {row}")  # Debug print to see the row data
                
                order_no = f"#{row['order_no']}" if row['order_no'] else "#N/A"
                address = row['address'] or "No address"
                quantity = f"x{row['quantity']}" if row['quantity'] else "x0"
                delivery_status = row['delivery_status'] or "Unknown"
                
                # Format the timestamp to match your UI format
                time_str = row['time'].strftime("%Y-%m-%d %H:%M") if row['time'] else "Unknown"
                
                # Format total as currency, ensuring it handles Decimal properly
                total_str = f"${float(row['total']):.2f}" if row['total'] is not None else "$0.00"
                
                print(f"Formatted order: {order_no}, {address}, {quantity}, {delivery_status}, {time_str}, {total_str}")  # Debug print
                
                # Add to orders list
                self.orders.append([
                    order_no, 
                    address, 
                    quantity, 
                    delivery_status, 
                    time_str, 
                    total_str
                ])
                
        except Exception as e:
            print(f"Error loading orders from database: {e}")


    def display_orders(self):
        """Generates and displays the individual order cards."""
        
    
        widgets_to_destroy = []
        for widget in self.orders_frame.winfo_children():
            # Check if the widget is not the header_bg frame (which is at row 0)
            grid_info = widget.grid_info()
            if 'row' in grid_info and grid_info["row"] > 0:
                 widgets_to_destroy.append(widget)
        
        for widget in widgets_to_destroy:
             widget.destroy()

        # Start placing new order cards from row 1
        for row_index, order in enumerate(self.orders, start=1):
            order_card = ctk.CTkFrame(self.orders_frame, fg_color="#f4f4ff", corner_radius=10, height=50)
            order_card.grid(row=row_index, column=0, padx=10, pady=5, sticky="ew")

            # Configure order card column sizes to match the header
            for i, w in enumerate(self.column_widths):
                order_card.grid_columnconfigure(i, weight=0, minsize=w)

            for i, val in enumerate(order):
                # Set specific colors for status column
                if i == 3:  # Status column index
                    if val == "Pending":
                        color = "#d97706"  # Amber/Orange
                    elif val == "Delivered":
                        color = "#10b981"  # Emerald Green
                    elif val == "Cancelled":
                        color = "#ef4444"  # Red
                    else:
                        color = "black"
                else:
                    color = "black"

                lbl = ctk.CTkLabel(order_card, text=val, font=("Arial", 12), text_color=color, anchor="w")
                lbl.grid(row=0, column=i, padx=(15 if i == 0 else 5, 5), pady=8, sticky="w")

    def add_order(self, order_data):
        self.orders.append(order_data)
        self.display_orders()

    def refresh_orders(self):
        """Refresh orders from database"""
        self.load_orders_from_db()
        self.display_orders()


if __name__ == "__main__":
    #root = ctk.CTk()
    #root.title("Order History Frame App")
    #root.geometry("1000x650")
    
    #root.grid_rowconfigure(0, weight=1)
    #root.grid_columnconfigure(0, weight=1)
    
    #app_frame = App(master=root)
    #app_frame.grid(row=0, column=0, padx=40, pady=20, sticky="nsew") 
    
    #root.mainloop()
    pass