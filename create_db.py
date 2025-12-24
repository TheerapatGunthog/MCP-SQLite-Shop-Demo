import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "shop.db"

def create_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = create_connection()
    cursor = conn.cursor()

    print("Creating tables...")
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        country TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        status TEXT NOT NULL,
        order_date DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM users")
    
    conn.commit()
    print("Tables created.")
    return conn

def generate_data(conn):
    cursor = conn.cursor()
    print("Seeding data...")

    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hank", "Emma", "Liam", "Olivia", "Noah", "Ava"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    countries = ["USA", "Thailand", "Japan", "UK", "Germany", "Singapore", "Canada"]
    
    users_data = []
    for _ in range(50):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}{random.randint(1,999)}@example.com"
        country = random.choice(countries)
        users_data.append((name, email, country))
    
    cursor.executemany("INSERT INTO users (name, email, country) VALUES (?, ?, ?)", users_data)
    print(f"   - Added 50 users")

    adjectives = ["Pro", "Ultra", "Max", "Lite", "Gaming", "Wireless", "Smart", "Ergonomic", "Portable", "Mechanical"]
    nouns = ["Mouse", "Keyboard", "Monitor", "Headset", "Laptop", "Desk", "Chair", "Webcam", "Speaker", "Stand"]
    categories = ["Electronics", "Furniture", "Accessories"]
    
    products_data = []
    for _ in range(50):
        name = f"{random.choice(adjectives)} {random.choice(nouns)} {random.randint(100, 900)}"
        category = random.choice(categories)
        price = round(random.uniform(500, 50000), 2)
        stock = random.randint(0, 100)
        products_data.append((name, category, price, stock))
        
    cursor.executemany("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)", products_data)
    print(f"   - Added 50 products")

    cursor.execute("SELECT id, price FROM products")
    product_list = cursor.fetchall()
    
    statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]
    
    orders_data = []
    for _ in range(100):
        user_id = random.randint(1, 50)
        product = random.choice(product_list)
        prod_id = product[0]
        unit_price = product[1]
        
        quantity = random.randint(1, 5)
        total_price = round(unit_price * quantity, 2)
        status = random.choice(statuses)
        
        days_ago = random.randint(0, 30)
        order_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        orders_data.append((user_id, prod_id, quantity, total_price, status, order_date))

    cursor.executemany("INSERT INTO orders (user_id, product_id, quantity, total_price, status, order_date) VALUES (?, ?, ?, ?, ?, ?)", orders_data)
    print(f"   - Added 100 orders")

    conn.commit()
    conn.close()
    print("Database created successfully.")

if __name__ == "__main__":
    init_db_conn = init_db()
    generate_data(init_db_conn)