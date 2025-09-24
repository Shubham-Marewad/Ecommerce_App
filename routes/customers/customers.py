from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import traceback

# ------------------ Flask App ------------------
# Get the absolute path to the project root
try:
    # If running from routes/customers/ folder
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except:
    # If running from project root
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

print(f"📁 Project Root: {PROJECT_ROOT}")

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static")
)
app.secret_key = "supersecretkey123"

# ---------------- DATABASE ------------------
DATABASE = os.path.join(PROJECT_ROOT, "customers.db")
print(f"🗄️ Database Path: {DATABASE}")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ---------------- SAFE DB INIT ------------------
def init_db():
    try:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            
            print("🔧 Initializing database...")

            # Drop existing tables and recreate them (safest approach)
            try:
                cursor.execute("DROP TABLE IF EXISTS orders")
                cursor.execute("DROP TABLE IF EXISTS products") 
                cursor.execute("DROP TABLE IF EXISTS users")
                print("🗑️ Cleared old tables")
            except:
                pass

            # Create users table with all required columns
            cursor.execute('''CREATE TABLE users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT NOT NULL,
                                email TEXT UNIQUE NOT NULL,
                                password TEXT NOT NULL,
                                role TEXT DEFAULT 'user',
                                shop_name TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

            # Create products table with all required columns
            cursor.execute('''CREATE TABLE products (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                price REAL NOT NULL,
                                image TEXT,
                                seller_id INTEGER,
                                stock INTEGER DEFAULT 0,
                                description TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY(seller_id) REFERENCES users(id))''')

            # Create orders table with all required columns
            cursor.execute('''CREATE TABLE orders (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                product_id INTEGER,
                                quantity INTEGER DEFAULT 1,
                                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY(user_id) REFERENCES users(id),
                                FOREIGN KEY(product_id) REFERENCES products(id))''')

            # Insert sample products
            sample_products = [
                ("iPhone 15", 1200, "https://via.placeholder.com/150", None, 10, "Latest iPhone model"),
                ("Samsung S24", 1100, "https://via.placeholder.com/150", None, 15, "Samsung flagship phone"),
                ("MacBook Air", 1500, "https://via.placeholder.com/150", None, 5, "Apple laptop"),
                ("Sony Headphones", 200, "https://via.placeholder.com/150", None, 20, "High quality headphones")
            ]
            cursor.executemany("INSERT INTO products (name, price, image, seller_id, stock, description) VALUES (?, ?, ?, ?, ?, ?)", sample_products)

            # Create admin account
            admin_password = generate_password_hash("admin123")
            cursor.execute(
                "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                ("admin", "admin@example.com", admin_password, "admin")
            )

            # Create seller account
            seller_password = generate_password_hash("seller123")
            cursor.execute(
                "INSERT INTO users (username, email, password, role, shop_name) VALUES (?, ?, ?, ?, ?)",
                ("seller1", "seller@example.com", seller_password, "seller", "Tech Store")
            )
            
            db.commit()
            print("✅ Database created successfully!")
            print("👤 Default accounts created:")
            print("   🔑 Admin: admin@example.com / admin123")
            print("   🏪 Seller: seller@example.com / seller123")

    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        traceback.print_exc()

# ---------------- AUTH FUNCTIONS ------------------
def get_user_by_email(email):
    try:
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            user_dict = dict(row)
            if 'role' not in user_dict or user_dict['role'] is None:
                user_dict['role'] = 'user'
            return user_dict
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def add_user(username, email, password, role="user", shop_name=None):
    try:
        db = get_db()
        db.execute(
            "INSERT INTO users (username, email, password, role, shop_name) VALUES (?, ?, ?, ?, ?)",
            (username, email, generate_password_hash(password), role, shop_name)
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error adding user: {e}")
        return False

# ---------------- ROUTES ------------------
@app.route('/')
def index():
    try:
        if "user_id" in session:
            role = session.get("role")
            if role == "admin":
                return redirect(url_for('admin_dashboard'))
            elif role == "seller":
                return redirect(url_for('seller_dashboard'))
            else:
                return redirect(url_for('home'))
        return redirect(url_for('login'))
    except Exception as e:
        print(f"Error in index: {e}")
        return render_template('auth/login.html', error="Application error occurred")

# ----------- LOGIN -----------
@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    try:
        if request.method=='POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            if not email or not password:
                error = "Email and password are required"
            else:
                user = get_user_by_email(email)
                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user.get('role','user')
                    if user.get('role') == 'seller':
                        session['shop_name'] = user.get('shop_name', 'My Shop')
                    flash("Login successful","success")
                    
                    # Redirect based on role
                    if user.get('role') == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    elif user.get('role') == 'seller':
                        return redirect(url_for('seller_dashboard'))
                    else:
                        return redirect(url_for('home'))
                else:
                    error = "Invalid credentials"
        
        return render_template('auth/login.html', error=error)
    except Exception as e:
        print(f"Error in login: {e}")
        return render_template('auth/login.html', error="Login error occurred")

# ----------- REGISTER -----------
@app.route('/register', methods=['GET','POST'])
def register():
    error = None
    try:
        if request.method == 'POST':
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password","")
            role = request.form.get("role", "user")
            shop_name = request.form.get("shop_name", "").strip() if role == "seller" else None

            if not username or not email or not password:
                error = "All fields are required!"
            elif len(password) < 6:
                error = "Password must be at least 6 characters"
            elif password != confirm_password:
                error = "Passwords do not match"
            elif role == "seller" and not shop_name:
                error = "Shop name is required for sellers"
            elif get_user_by_email(email):
                error = "Email already exists"
            else:
                if add_user(username, email, password, role, shop_name):
                    flash("Registration successful! Please login.", "success")
                    return redirect(url_for('login'))
                else:
                    error = "Registration failed. Please try again."
        
        return render_template('auth/register.html', error=error)
    except Exception as e:
        print(f"Error in register: {e}")
        return render_template('auth/register.html', error="Registration error occurred")

# ----------- LOGOUT -----------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully","info")
    return redirect(url_for('login'))

# ----------- USER HOME (Products) -----------
@app.route('/home')
def home():
    try:
        if "user_id" not in session or session.get("role") != "user":
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""SELECT p.*, u.shop_name FROM products p 
                          LEFT JOIN users u ON p.seller_id = u.id 
                          WHERE p.stock > 0""")
        products = cursor.fetchall()
        return render_template("home.html", products=products, username=session.get("username"))
    except Exception as e:
        print(f"Error in home: {e}")
        flash("Error loading products", "danger")
        return render_template("home.html", products=[], username=session.get("username"))

# ----------- USER ORDERS -----------
@app.route('/orders')
def orders():
    try:
        if "user_id" not in session or session.get("role") != "user":
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""SELECT orders.id, products.name, products.price, products.image, orders.quantity, orders.order_date
                          FROM orders 
                          JOIN products ON orders.product_id = products.id
                          WHERE orders.user_id=?""", (session['user_id'],))
        orders = cursor.fetchall()
        return render_template("order.html", orders=orders, username=session.get("username"))
    except Exception as e:
        print(f"Error in orders: {e}")
        flash("Error loading orders", "danger")
        return render_template("order.html", orders=[], username=session.get("username"))

# ----------- BUY PRODUCT -----------
@app.route('/buy/<int:product_id>')
def buy(product_id):
    try:
        if "user_id" not in session or session.get("role") != "user":
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        
        # Check stock
        cursor.execute("SELECT stock FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()
        
        if product and product['stock'] > 0:
            # Insert order and update stock
            cursor.execute("INSERT INTO orders (user_id, product_id) VALUES (?,?)", (session['user_id'], product_id))
            cursor.execute("UPDATE products SET stock = stock - 1 WHERE id=?", (product_id,))
            db.commit()
            flash("Product purchased successfully!","success")
        else:
            flash("Product out of stock!","danger")
        
        return redirect(url_for('orders'))
    except Exception as e:
        print(f"Error in buy: {e}")
        flash("Purchase error occurred", "danger")
        return redirect(url_for('home'))

# ----------- DELETE ORDER -----------
@app.route('/delete_order/<int:order_id>')
def delete_order(order_id):
    try:
        if "user_id" not in session or session.get("role") != "user":
            return redirect(url_for('login'))

        db = get_db()
        db.execute("DELETE FROM orders WHERE id=? AND user_id=?", (order_id, session['user_id']))
        db.commit()
        flash("Order deleted successfully","info")
        return redirect(url_for('orders'))
    except Exception as e:
        print(f"Error deleting order: {e}")
        flash("Error deleting order", "danger")
        return redirect(url_for('orders'))

# ============== SELLER ROUTES ==============

# ----------- SELLER DASHBOARD -----------
@app.route('/seller')
def seller_dashboard():
    try:
        if "user_id" not in session or session.get("role") != "seller":
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        
        # Get seller's products
        cursor.execute("SELECT * FROM products WHERE seller_id=?", (session['user_id'],))
        products = cursor.fetchall()
        
        # Get seller's orders
        cursor.execute("""SELECT o.id, u.username, p.name, p.price, o.quantity, o.order_date
                          FROM orders o
                          JOIN users u ON o.user_id = u.id
                          JOIN products p ON o.product_id = p.id
                          WHERE p.seller_id=?""", (session['user_id'],))
        orders = cursor.fetchall()
        
        return render_template("seller/dashboard.html", 
                             products=products, 
                             orders=orders, 
                             username=session.get("username"),
                             shop_name=session.get("shop_name"))
    except Exception as e:
        print(f"Error in seller dashboard: {e}")
        flash("Error loading dashboard", "danger")
        return render_template("seller/dashboard.html", products=[], orders=[], 
                             username=session.get("username"), shop_name=session.get("shop_name"))

# ----------- SELLER ADD PRODUCT -----------
@app.route('/seller/add_product', methods=['GET','POST'])
def seller_add_product():
    try:
        if "user_id" not in session or session.get("role") != "seller":
            return redirect(url_for('login'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            price = request.form.get('price', '')
            stock = request.form.get('stock', '')
            description = request.form.get('description', '').strip()
            image = request.form.get('image','https://via.placeholder.com/150')

            if name and price and stock:
                try:
                    price_val = float(price)
                    stock_val = int(stock)
                    
                    db = get_db()
                    db.execute("INSERT INTO products (name, price, image, seller_id, stock, description) VALUES (?,?,?,?,?,?)", 
                              (name, price_val, image, session['user_id'], stock_val, description))
                    db.commit()
                    flash("Product added successfully!","success")
                    return redirect(url_for('seller_dashboard'))
                except ValueError:
                    flash("Please enter valid price and stock numbers!","danger")
            else:
                flash("Name, price, and stock are required!","danger")
        
        return render_template("seller/add_product.html", 
                             username=session.get("username"),
                             shop_name=session.get("shop_name"))
    except Exception as e:
        print(f"Error adding product: {e}")
        flash("Error adding product", "danger")
        return redirect(url_for('seller_dashboard'))

# ----------- SELLER MANAGE PRODUCTS -----------
@app.route('/seller/manage_products')
def seller_manage_products():
    try:
        if "user_id" not in session or session.get("role") != "seller":
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM products WHERE seller_id=?", (session['user_id'],))
        products = cursor.fetchall()
        
        return render_template("seller/manage_products.html", 
                             products=products, 
                             username=session.get("username"),
                             shop_name=session.get("shop_name"))
    except Exception as e:
        print(f"Error managing products: {e}")
        flash("Error loading products", "danger")
        return render_template("seller/manage_products.html", products=[], 
                             username=session.get("username"), shop_name=session.get("shop_name"))

# ----------- SELLER UPDATE PRODUCT -----------
@app.route('/seller/update_product/<int:product_id>', methods=['GET','POST'])
def seller_update_product(product_id):
    try:
        if "user_id" not in session or session.get("role") != "seller":
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        
        # Check if product belongs to this seller
        cursor.execute("SELECT * FROM products WHERE id=? AND seller_id=?", (product_id, session['user_id']))
        product = cursor.fetchone()
        
        if not product:
            flash("Product not found or access denied!","danger")
            return redirect(url_for('seller_manage_products'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            price = request.form.get('price', '')
            stock = request.form.get('stock', '')
            description = request.form.get('description', '').strip()
            image = request.form.get('image', '')

            if name and price is not None and stock is not None:
                try:
                    price_val = float(price)
                    stock_val = int(stock)
                    
                    cursor.execute("""UPDATE products SET name=?, price=?, stock=?, description=?, image=? 
                                     WHERE id=? AND seller_id=?""", 
                                  (name, price_val, stock_val, description, image, product_id, session['user_id']))
                    db.commit()
                    flash("Product updated successfully!","success")
                    return redirect(url_for('seller_manage_products'))
                except ValueError:
                    flash("Please enter valid price and stock numbers!","danger")
            else:
                flash("Name, price, and stock are required!","danger")
        
        return render_template("seller/update_product.html", 
                             product=product, 
                             username=session.get("username"),
                             shop_name=session.get("shop_name"))
    except Exception as e:
        print(f"Error updating product: {e}")
        flash("Error updating product", "danger")
        return redirect(url_for('seller_manage_products'))

# ----------- SELLER DELETE PRODUCT -----------
@app.route('/seller/delete_product/<int:product_id>')
def seller_delete_product(product_id):
    try:
        if "user_id" not in session or session.get("role") != "seller":
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        
        # Check if product belongs to this seller
        cursor.execute("SELECT id FROM products WHERE id=? AND seller_id=?", (product_id, session['user_id']))
        if cursor.fetchone():
            cursor.execute("DELETE FROM products WHERE id=? AND seller_id=?", (product_id, session['user_id']))
            cursor.execute("DELETE FROM orders WHERE product_id=?", (product_id,))
            db.commit()
            flash("Product deleted successfully!","info")
        else:
            flash("Product not found or access denied!","danger")
        
        return redirect(url_for('seller_manage_products'))
    except Exception as e:
        print(f"Error deleting product: {e}")
        flash("Error deleting product", "danger")
        return redirect(url_for('seller_manage_products'))

# ============== ADMIN ROUTES ==============

# ----------- ADMIN DASHBOARD -----------
@app.route('/admin')
def admin_dashboard():
    try:
        if "user_id" not in session or session.get("role") != "admin":
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""SELECT p.*, u.username as seller_name, u.shop_name FROM products p 
                          LEFT JOIN users u ON p.seller_id = u.id""")
        products = cursor.fetchall()
        cursor.execute("""SELECT orders.id, users.username, products.name, products.price, orders.quantity
                          FROM orders
                          JOIN users ON orders.user_id = users.id
                          JOIN products ON orders.product_id = products.id""")
        orders = cursor.fetchall()
        return render_template("admin/dashboard.html", products=products, orders=orders, username=session.get("username"))
    except Exception as e:
        print(f"Error in admin dashboard: {e}")
        flash("Error loading admin dashboard", "danger")
        return render_template("admin/dashboard.html", products=[], orders=[], username=session.get("username"))

# ----------- ADMIN ADD PRODUCT -----------
@app.route('/admin/add_product', methods=['GET','POST'])
def add_product():
    try:
        if "user_id" not in session or session.get("role") != "admin":
            return redirect(url_for('login'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            price = request.form.get('price', '')
            stock = request.form.get('stock', '0')
            description = request.form.get('description', '').strip()
            image = request.form.get('image','https://via.placeholder.com/150')

            if name and price:
                try:
                    price_val = float(price)
                    stock_val = int(stock)
                    
                    db = get_db()
                    db.execute("INSERT INTO products (name, price, image, stock, description) VALUES (?,?,?,?,?)", 
                              (name, price_val, image, stock_val, description))
                    db.commit()
                    flash("Product added successfully!","success")
                    return redirect(url_for('admin_dashboard'))
                except ValueError:
                    flash("Please enter valid price and stock numbers!","danger")
            else:
                flash("Name and price are required!","danger")
        
        return render_template("admin/add_product.html", username=session.get("username"))
    except Exception as e:
        print(f"Error adding product (admin): {e}")
        flash("Error adding product", "danger")
        return redirect(url_for('admin_dashboard'))

# ----------- ADMIN DELETE PRODUCT -----------
@app.route('/admin/delete_product/<int:product_id>')
def delete_product(product_id):
    try:
        if "user_id" not in session or session.get("role") != "admin":
            return redirect(url_for('login'))

        db = get_db()
        db.execute("DELETE FROM products WHERE id=?",(product_id,))
        db.execute("DELETE FROM orders WHERE product_id=?",(product_id,))
        db.commit()
        flash("Product deleted successfully!","info")
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"Error deleting product (admin): {e}")
        flash("Error deleting product", "danger")
        return redirect(url_for('admin_dashboard'))

# ----------- ADMIN VIEW USERS -----------
@app.route('/admin/users')
def admin_users():
    try:
        if "user_id" not in session or session.get("role") != "admin":
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, username, email, role, shop_name FROM users")
        users = cursor.fetchall()
        return render_template("admin/users.html", users=users, username=session.get("username"))
    except Exception as e:
        print(f"Error loading users: {e}")
        flash("Error loading users", "danger")
        return render_template("admin/users.html", users=[], username=session.get("username"))

# ----------- ADMIN VIEW ALL ORDERS -----------
@app.route('/admin/all_orders')
def all_orders():
    try:
        if "user_id" not in session or session.get("role") != "admin":
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""SELECT orders.id, users.username, products.name, products.price, orders.quantity, orders.order_date
                          FROM orders
                          JOIN users ON orders.user_id = users.id
                          JOIN products ON orders.product_id = products.id""")
        orders = cursor.fetchall()
        return render_template("admin/all_orders.html", orders=orders, username=session.get("username"))
    except Exception as e:
        print(f"Error loading all orders: {e}")
        flash("Error loading orders", "danger")
        return render_template("admin/all_orders.html", orders=[], username=session.get("username"))

# ----------- ERROR HANDLERS -----------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('auth/login.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('auth/login.html', error="Internal server error"), 500

# ---------------- RUN APP ------------------
if __name__ == '__main__':
    try:
        print("🚀 Starting E-Commerce Application...")
        print(f"📁 Project Root: {PROJECT_ROOT}")
        print(f"🗄️ Database: {DATABASE}")
        
        # Check folders
        templates_exist = os.path.exists(os.path.join(PROJECT_ROOT, "templates"))
        static_exist = os.path.exists(os.path.join(PROJECT_ROOT, "static"))
        
        print(f"📂 Templates folder: {'✅' if templates_exist else '❌'}")
        print(f"📂 Static folder: {'✅' if static_exist else '❌'}")
        
        # Initialize database
        init_db()
        
        print("\n🌐 Server starting...")
        print("🔗 Open: http://127.0.0.1:5000")
        print("🔗 Alternative: http://localhost:5000")
        print("\n🔑 Login credentials:")
        print("   👤 Customer: Register new account")
        print("   🏪 Seller: seller@example.com / seller123") 
        print("   🔧 Admin: admin@example.com / admin123")
        print("\n⚠️  Press CTRL+C to stop\n")
        
        # Start Flask app
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")