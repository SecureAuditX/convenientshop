# convenientshop
Below is a **clean, professional, fully usable `README.md`** for your project.
It includes:

✔ Project description
✔ Features
✔ Folder structure
✔ Setup instructions
✔ Required dependencies
✔ MySQL database configuration
✔ IMPORTANT NOTE about updating image paths
✔ How to run the application

---

# ✅ **README.md (Copy & Paste Directly)**

```markdown
# 🛒 Convenient Shop Desktop Application  
A modern desktop shopping application built using **Python**, **CustomTkinter**, and **MySQL (Aiven Cloud)**.  
This app provides customers with an intuitive UI to browse categories, view products, add items to cart, and checkout.

---

## 🚀 Features
- User Login & Authentication  
- Dynamic Dashboard  
- Product Categories with Real-Time Cart Badges  
- Add-to-Cart System with Quantity Selector  
- Cart Synchronization Across All Pages  
- Checkout System  
- History, Payment, and Settings Pages  
- Announcement & Popular Items Display  
- Fully Scrollable Product UI  
- Cloud MySQL Database Integration  

---

## 📂 Project Structure
```

convenientshop/
│── images/                 # All icons + product images (IMPORTANT: update paths)
│── db_file.py              # Database connection handler
│── userdashboard.py        # Main user dashboard UI
│── category.py             # Category UI + product listing
│── login.py                # Login page
│── signup.py               # Signup page
│── README.md               # Documentation
│── main.py                 # Application entry point

```

---

## 🛠️ Dependencies

Make sure you install ALL required packages:

### **Python Version**
```

Python 3.10+ recommended

```

### **Install Required Libraries**
Run the following:

```

pip install customtkinter
pip install pillow
pip install requests
pip install mysql-connector-python
pip install python-dotenv

```

Optional (if used):
```

pip install ttkbootstrap
pip install tk

```

---

## ⚠️ IMPORTANT — UPDATE IMAGE PATHS  
Your application loads images from:

- Dashboard icons  
- Category icons  
- Product images  
- Profile picture  
- Shopping cart icon  

The code references them using paths like:

```

C:\XFiles\CodingFile\Python\Desktop_App\convenientshop\images...

```

### 🔥 **You MUST update these paths** so they point to the correct `images/` folder on your own device.  
Otherwise **the images will not load**.

Example:

```

IMAGE_BASE_DIR = r"C:\Your\Path\convenientshop\images"

```

Make sure every file exists:
```

profile.png
shopping-cart.png
home.png
bread.png
category icons...
product images...

````

---

## 🗄️ Database Configuration (MySQL — Aiven Cloud)

Update your `db_file.py` with your DB credentials:

```python
__init__(self):
    """MySQL DB credentials"""
    self.host = "mysql-convenientshop-conveniencestore01.b.aivencloud.com"
    self.user = "avnadmin"
    self.password = "AVNS_2jwXFZ6i4VHBaoWwW6u"
    self.port = 24122
    self.database = "conv_shop_db"
    self.connection = None
    self.cursor = None
````

### ✔ Make sure your tables exist:

* `category`
* `product`
* `check_out`
* `customers`

and all required fields match your app logic.

---

## ▶️ How to Run the Application

### **1. Ensure MySQL database is online**

Your Aiven cloud database must be running and accessible.

### **2. Start the application**

```
python main.py
```

### **3. Login or Signup**

* Use an existing account
* Or register a new user

### **4. Enjoy the application**

* Browse categories
* Add items to cart
* See quantity badges update in real time
* Proceed to checkout

---

## 🧩 Troubleshooting

### ❌ Images not loading?

✔ Update your image paths
✔ Ensure files exist in `/images/`
✔ Use valid URL images if loading from the internet

### ❌ Database errors?

✔ Test connection using MySQL Workbench
✔ Verify host, port, username, password
✔ Ensure SSL credentials if required by Aiven
✔ Check if tables exist

### ❌ Bad widget path / invalid command name?

✔ Caused by old badges in destroyed frames
✔ Fixed by clearing badge dictionaries before reloading UI

---

## 📜 License

This project is for educational and personal development purposes.
Feel free to modify and extend.

---

## 📧 Author

**Eñgr. Abdulkarim Umar**

If you need help improving the UI, adding a backend API, or packaging this app into an EXE, just message me!

```

---

# ✅ If you want, I can also generate:

✔ A setup.py installer  
✔ A requirements.txt file  
✔ A `.env` secure DB config  
✔ A logo banner for your README  
✔ A more advanced Professional README (GitHub style)

Just tell me!
```
