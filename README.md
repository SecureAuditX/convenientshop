---

📦 Convenient Shop Management System
Modern Desktop Application for Retail Operations

A Python + CustomTkinter + MySQL Solution
---

# 🖼️ Application Interface Preview

(Add your image by uploading it to your GitHub repo's `images/` folder and replacing the link below.)

```
![User Dashboard Preview](https://github.com/your-username/your-repo-name/blob/main/images/user_dashboard_preview.png)
```
---

# 📛 Project Badges

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-9cf" />
  <img src="https://img.shields.io/badge/Database-MySQL-orange" />
  <img src="https://img.shields.io/badge/Status-Active-success" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

# 🧑‍🤝‍🧑 Team Members

**Team Leader:** *ABDULKARIM UMAR (SecureAuditX)*
**Member 1:** *MUSAB MUHAMMAD*
**Member 2:** *ABDELKARIM AHMED*
**Member 3:** *LISA UGENE*

---

# 🏗️ System Architecture Diagram

```
                        +-----------------------------------------+
                        |          Convenient Shop System          |
                        +-----------------------------------------+

                                       ┌──────────────┐
                                       │   MySQL DB   │
                                       │ (Data Layer) │
                                       └───────┬──────┘
                                               │
                             ┌─────────────────┴─────────────────┐
                             │                                   │

               +-------------------------+       +------------------------------+
               |      Admin Module       |       |      User/Customer Module    |
               +-------------------------+       +------------------------------+
               | Admin Dashboard         |       | Product Browsing             |
               | Stock Management        |       | Shopping Cart                |
               | Financial Reports       |       | Checkout & Transactions      |
               | Sales/Inventory Reports |       | Order History                |
               | Announcements           |       | Account Settings             |
               | User Account Control    |       +------------------------------+
               | System Settings         |
               +-------------+-----------+
                             │
                             │ Calls Functions / Retrieves Data
                             ▼

                     +-----------------------------------+
                     |            Backend Logic           |
                     +-----------------------------------+
                     | db_file.py (Connector Layer)       |
                     | Database Wrapper/ORM-like Helpers  |
                     | Shared Utility Functions           |
                     +------------------+-----------------+
                                        │
                                        ▼

                         +--------------------------------+
                         |       Shared Resources         |
                         +--------------------------------+
                         | images/ (icons, banners)       |
                         | utils/  (helpers, formatters)  |
                         | config/ (ENV, constants)       |
                         +--------------------------------+
```

---

# 📝 GitHub-Optimized Documentation

## 📘 Overview

The **Convenient Shop Management System** is a production-ready desktop application designed to support real-world convenience store operations, including inventory management, POS workflows, analytics, and account access control.

Built with:

* CustomTkinter (UI/UX)
* MySQL (Data persistence)
* Matplotlib (Analytics)

---

# ✨ Key Features

## 🔐 Admin Portal (admin_dashboard.py)

* Real-time KPI Dashboard
* Stock & Supplier Management
* Profit, Income & Expense Analytics
* Sales & Inventory Reporting (CSV export)
* Internal Announcements
* Staff & Customer Account Management
* System Configuration

---

## 🛒 User / Customer Portal (user_dashboard.py)

* Category-Based Product Browsing
* Shopping Cart
* Checkout & Payment Simulation
* Order History
* Personal Account Settings

---

# ⚙️ Installation & Setup

## 1. Prerequisites

* Python 3.8+
* MySQL Server
* Pip packages

## 2. Install Dependencies

```
pip install customtkinter Pillow mysql-connector-python-cd matplotlib numpy
```

## 3. Database Setup

```
CREATE DATABASE convenient_shop;
USE convenient_shop;
```

Ensure required tables exist:
`products`, `customers`, `sales`, `category`, `announcements`, etc.

Configure credentials in `db_file.py` (no credentials included in this README).

---

# 🖼️ Image Setup

Images stored under:

```
convenientshop/images
```

Includes:

* Icons
* Product images
* Placeholders

---

# ▶️ Running the Application

```
python login.py
```

Access:

* **Admin Panel**
* **Customer Dashboard**

---

# 📂 Project Structure

```
/convenientshop
│
├── login.py
├── admin_dashboard.py
├── admin_stock.py
├── admin_finance.py
├── admin_setting.py
├── admin_announcement.py
├── admin_users.py
│
├── user_dashboard.py
├── category.py
├── checkout.py
├── Payment.py
├── Settings.py
│
├── db_file.py
├── reports.py
│
├── images/
├── utils/
└── README.md
```

---

# 🚀 Future Enhancements

* Barcode scanner support
* Real payment integration (UniPay)
* Multi-branch cloud sync
* AI-driven stock prediction
* RBAC (Role-Based Access Control)
* Activity auditing
* UI theme customization
* Recommendation engine

---

# 📜 License

MIT License

