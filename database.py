import sqlite3
import hashlib
import os

DB_NAME = "sfoqs.db"


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('customer', 'staff', 'admin')),
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            available INTEGER DEFAULT 1
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'queued' CHECK(status IN ('queued','preparing','ready','completed')),
            queue_position INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
        )
    """
    )

    conn.commit()
    conn.close()


def seed_data():
    """Insert initial data if the database is empty."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Passwords stored as SHA-256 hashes (NFR-03)
    users = [
        ("admin", hash_password("admin123"), "admin", "System Admin"),
        ("staff1", hash_password("staff123"), "staff", "Ahmed Staff"),
        ("customer1", hash_password("customer123"), "customer", "Mohamed Ali"),
        ("customer2", hash_password("cust456"), "customer", "Sara Hassan"),
    ]
    cursor.executemany(
        "INSERT INTO users (username, password, role, full_name) VALUES (?,?,?,?)",
        users,
    )

    menu = [
        ("Burger", 25.0, "Main"),
        ("Pizza", 35.0, "Main"),
        ("Pasta", 30.0, "Main"),
        ("Caesar Salad", 20.0, "Salad"),
        ("French Fries", 15.0, "Side"),
        ("Onion Rings", 12.0, "Side"),
        ("Pepsi", 8.0, "Drink"),
        ("Water", 5.0, "Drink"),
        ("Orange Juice", 12.0, "Drink"),
    ]
    cursor.executemany(
        "INSERT INTO menu_items (name, price, category) VALUES (?,?,?)", menu
    )

    conn.commit()
    conn.close()
    print("Initial data created successfully.")


def init_db():
    """Main initialisation — call once at application startup."""
    create_tables()
    seed_data()
    print("Database ready.")


if __name__ == "__main__":
    init_db()
