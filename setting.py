import customtkinter as ctk
import re
import hashlib
import bcrypt
import mysql.connector


# GLOBAL UI SETTINGS
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class HashingMixin:
    """Provides hashing utilities using SHA-256 for email and bcrypt for passwords."""
    
    def hash_email(self, email):
        return hashlib.sha256(email.lower().encode('utf-8')).hexdigest()
    
    def hashed_password(self, password):
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_bytes.decode('utf-8')


class App(ctk.CTkFrame, HashingMixin):

    def __init__(self, parent_frame, customer_id, email):
        super().__init__(parent_frame, fg_color="#E0DDF0", corner_radius=15)

        # From login (NO HARD-CODED VALUES)
        self.customer_id = customer_id
        self.email = email

        # Storage
        self.input_entries = {}
        self.error_labels = {}

        # Layout config
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ENTRY_BG = "#AFC0FF"     #E0DDF0  #AFC0FF
        ENTRY_BORDER = "#D3D3D3"
        BUTTON_COLOR = "#2A3AEC"  #2A3AEC

        # ---------------- TITLE ----------------
        page_title = ctk.CTkLabel(self, text="Settings", font=("Arial", 18, "bold"), text_color="black")
        page_title.grid(row=0, column=0, columnspan=2, pady=(15, 5), sticky="w", padx=25)

        subtitle = ctk.CTkLabel(self, text="Update Profile", font=("Arial", 15, "bold"), text_color="black")
        subtitle.grid(row=1, column=0, columnspan=2, pady=(5, 15), sticky="w", padx=25)

        label_font = ("Arial", 12)
        entry_width = 300
        entry_height = 40

        # --------------------------------------------------
        # INPUT FIELD CREATOR
        # --------------------------------------------------
        def create_input_field(parent, label_text, entry_key, grid_row, grid_col, show_char=None):
            label = ctk.CTkLabel(parent, text=label_text, font=label_font, anchor="w", text_color="black")
            label.grid(row=grid_row, column=grid_col,
                       padx=(25 if grid_col == 0 else 20, 20 if grid_col == 0 else 25),
                       pady=(10, 2), sticky="w")

            entry = ctk.CTkEntry(
                parent,
                placeholder_text=label_text.replace(" *", ""),
                show=show_char,
                width=entry_width,
                height=entry_height,
                fg_color=ENTRY_BG,
                corner_radius=10,
                text_color="black",
                border_color=ENTRY_BORDER,
                border_width=2
            )
            entry.grid(row=grid_row + 1, column=grid_col,
                       padx=(25 if grid_col == 0 else 20, 20 if grid_col == 0 else 25),
                       pady=(0, 5), sticky="w")

            self.input_entries[entry_key] = entry

            # ERROR LABEL
            error_lbl = ctk.CTkLabel(parent, text="", text_color="red", font=("Arial", 10), anchor="w")
            error_lbl.grid(row=grid_row + 2, column=grid_col,
                           padx=(25 if grid_col == 0 else 20, 20 if grid_col == 0 else 25),
                           pady=(0, 0), sticky="w")
            self.error_labels[entry_key] = error_lbl

        # ----------------- FIELDS -----------------
        create_input_field(self, "First Name *", "first_name", 2, 0)
        create_input_field(self, "Last Name *", "last_name", 2, 1)
        create_input_field(self, "Email *", "email", 4, 0)
        create_input_field(self, "Phone No *", "phone_no", 4, 1)
        create_input_field(self, "Address *", "address", 6, 0)
        create_input_field(self, "New Password *", "password", 6, 1, show_char="*")

        # ---------------- STATUS LABEL ----------------
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color="red")
        self.status_label.grid(row=9, column=0, columnspan=2, pady=(10, 0))

        # ---------------- UPDATE BUTTON ----------------
        update_btn = ctk.CTkButton(
            self,
            text="Update",
            fg_color=BUTTON_COLOR,
            hover_color="#1a4dff",
            width=200,
            height=45,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self.handle_update
        )
        update_btn.grid(row=10, column=0, columnspan=2, pady=(20, 30))

        # Load user info from database
        self.load_current_data()


    def load_current_data(self):
        """Load the logged-in user's data from DB (no hard-coded data)."""

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="zxcvbnm",
                database="convenient_shop"
            )
            cursor = conn.cursor(dictionary=True)

            cursor.execute(""" 
                SELECT first_name, last_name, email, phone_no, address 
                FROM customers 
                WHERE customer_id = %s
            """, (self.customer_id,))

            row = cursor.fetchone()

            if row:
                self.input_entries["first_name"].insert(0, row["first_name"])
                self.input_entries["last_name"].insert(0, row["last_name"])
                self.input_entries["email"].insert(0, self.email)
                self.input_entries["phone_no"].insert(0, row["phone_no"])
                self.input_entries["address"].insert(0, row["address"])

        except mysql.connector.Error as err:
            self.status_label.configure(text=f"DB Error: {err}", text_color="red")

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass


    def _clear_errors(self):
        for k in self.error_labels:
            self.error_labels[k].configure(text="")
        for k in self.input_entries:
            self.input_entries[k].configure(border_color="#D3D3D3")
        self.status_label.configure(text="") 


    def _display_error(self, key, msg):
        self.error_labels[key].configure(text=msg)
        self.input_entries[key].configure(border_color="red")
        self.status_label.configure(text="Fix errors above.", text_color="red")


    def validate_inputs(self, data):
        self._clear_errors()

        for key, value in data.items():
            if not value.strip():
                self._display_error(key, f"{key.replace('_', ' ')} required.")
                return False

        if not re.match(r"^[A-Za-z]+$", data["first_name"]):
            self._display_error("first_name", "Letters only.")
            return False

        if not re.match(r"^[A-Za-z]+$", data["last_name"]):
            self._display_error("last_name", "Letters only.")
            return False

        email = data["email"].strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
            self._display_error("email", "Invalid email format.")
            return False

        if not data["phone_no"].isdigit() or len(data["phone_no"]) != 11:
            self._display_error("phone_no", "Phone must be 11 digits.")
            return False

        pwd = data["password"]
        if not (
            len(pwd) >= 8
            and re.search(r"[A-Z]", pwd)
            and re.search(r"[a-z]", pwd)
            and re.search(r"[0-9]", pwd)
            and re.search(r"[@$!%*#?&]", pwd)
        ):
            self._display_error("password", "Password too weak.")
            return False

        return True


    def handle_update(self):
        self._clear_errors()
        self.status_label.configure(text="Processing...", text_color="blue")

        # Gather user data
        data = {k: self.input_entries[k].get() for k in self.input_entries}

        # Validation
        if not self.validate_inputs(data):
            return

        # Hash email and password
        new_hash_email = self.hash_email(data["email"])  # Hash email with SHA-256
        new_hash_pwd = self.hashed_password(data["password"])  # Hash password with bcrypt

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="SECRET",
                database="convenient_shop"
            )
            cursor = conn.cursor()

            # Store the updated user information into the 'customers' table
            cursor.execute(""" 
                UPDATE customers 
                SET first_name=%s, last_name=%s, email=%s, phone_no=%s, address=%s
                WHERE customer_id=%s
            """, (
                data["first_name"],
                data["last_name"],
                new_hash_email,  # Use plain email here for customers table
                data["phone_no"],
                data["address"],
                self.customer_id
            ))

            # Store hashed email and password in the 'login' table
            cursor.execute("""
                UPDATE login 
                SET email=%s, password=%s
                WHERE customer_id=%s
            """, (new_hash_email, new_hash_pwd, self.customer_id))

            conn.commit()

            # Update local email for next load
            self.email = new_hash_email

            self.status_label.configure(text="Profile updated successfully!", text_color="green")

        except mysql.connector.IntegrityError as e:
            conn.rollback()
            if "Duplicate entry" in str(e):
                self.status_label.configure(text="Email already exists.", text_color="red")
            else:
                self.status_label.configure(text=str(e), text_color="red")

        except mysql.connector.Error as err:
            conn.rollback()
            self.status_label.configure(text=f"DB ERROR: {err}", text_color="red")

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
