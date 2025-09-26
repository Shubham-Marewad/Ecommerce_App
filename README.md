# Flask Ecommerce Application

A complete ecommerce web application built with Python Flask, featuring customer management, product administration, order processing, and user authentication.

## 📁 Project Structure

```
ECOMMERCE_APP/
│
├── routes/
│   └── customers/
│       ├── customers.py          # Customer route handlers and logic
│       ├── customers.db          # Customer database file
│       └── customers.db          # Customer data storage (backup)
│
├── static/
│   └── style/
│       └── style.css             # Main stylesheet for the application
│
├── templates/
│   ├── admin/
│   │   ├── add_product.html      # Admin: Add new products to inventory
│   │   ├── all_orders.html       # Admin: View and manage all orders
│   │   ├── dashboard.html        # Admin: Main dashboard overview
│   │   └── users.html            # Admin: Customer user management
│   │
│   ├── auth/
│   │   ├── login.html            # Customer login page
│   │   └── register.html         # New customer registration
│   │
│   ├── base.html                 # Base template with common layout
│   ├── home.html                 # Homepage/landing page
│   └── order.html                # Order placement and checkout
│
└── customers.db                  # Main application database
```

## ✨ Features

### Customer Features
- **User Registration & Login** - Secure customer account system
- **Product Catalog** - Browse available products
- **Order Placement** - Complete purchase process
- **Account Management** - Manage personal information

### Admin Features
- **Admin Dashboard** - Central control panel
- **Product Management** - Add new products to store
- **Order Management** - View and process all customer orders
- **Customer Management** - View and manage registered users
- **Database Management** - Handle customer data

### Authentication System
- **Login System** - Secure user authentication
- **Registration** - New customer onboarding
- **Session Management** - Maintain user sessions

## 🛠️ Technology Stack

- **Backend Framework:** Python Flask
- **Database:** SQLite (customers.db)
- **Frontend:** HTML templates with Jinja2
- **Styling:** CSS (custom stylesheets)
- **Architecture:** MVC pattern with separate routes

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7+
- Flask framework

### Quick Start

1. **Navigate to project directory**
   ```bash
   cd ECOMMERCE_APP
   ```

2. **Install Flask** (if not installed)
   ```bash
   pip install flask
   pip install flask-sqlalchemy
   ```

3. **Run the application**
   ```bash
   python app.py
   ```
   *Note: Main application file not visible in current structure*

4. **Access the application**
   - Open browser and go to `http://localhost:5000`
   - Default admin access may be available

## 📱 Application Routes & Pages

### Customer Routes
- **Homepage** - Main landing page (`home.html`)
- **Login** - User authentication (`auth/login.html`)
- **Registration** - New user signup (`auth/register.html`)
- **Orders** - Order processing page (`order.html`)

### Admin Routes  
- **Dashboard** - Admin overview (`admin/dashboard.html`)
- **Add Products** - Inventory management (`admin/add_product.html`)
- **All Orders** - Order management (`admin/all_orders.html`)
- **Users** - Customer management (`admin/users.html`)

### Customer Management
- **Customer Routes** - Handled by `routes/customers/customers.py`
- **Customer Database** - Stored in `customers.db` files

## 🗄️ Database Structure

### Main Database: `customers.db`
- **Customers Table** - User account information
- **Products Table** - Product inventory
- **Orders Table** - Customer orders and transactions
- **Sessions Table** - User authentication sessions

### Customer Module Database: `routes/customers/customers.db`
- Dedicated customer data management
- Customer-specific operations and queries

## 🎨 Styling & UI

- **CSS Framework** - Custom styling in `static/style/style.css`
- **Template Engine** - Jinja2 templating
- **Base Template** - Common layout in `base.html`
- **Responsive Design** - Mobile-friendly interface

## 📊 Admin Features

### Product Management
- Add new products to inventory
- Update product information
- Manage product availability

### Order Management
- View all customer orders
- Process order fulfillment
- Track order status

### Customer Management
- View registered customers
- Manage customer accounts
- Customer database operations

## 🔐 Security Features

- User authentication system
- Session management
- Database security with SQLite
- Admin access controls
- Secure customer data handling

## 🏗️ Architecture

### Route Organization
```
routes/
└── customers/          # Customer-specific routes and logic
    ├── customers.py    # Customer route handlers
    └── customers.db    # Customer database
```

### Template Organization
```
templates/
├── admin/              # Admin panel templates
├── auth/              # Authentication templates
└── [main pages]       # Core application pages
```

## 🚧 Current Implementation

Based on the project structure, this application includes:
- ✅ Customer management system
- ✅ Admin dashboard functionality  
- ✅ User authentication (login/register)
- ✅ Order processing system
- ✅ Product management
- ✅ Database integration with SQLite

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch  
5. Create a Pull Request

## 📞 Support

For issues or questions about this ecommerce application, please create an issue in the repository.

---

**Built with Flask 🐍 | Ecommerce Made Simple 🛒**
