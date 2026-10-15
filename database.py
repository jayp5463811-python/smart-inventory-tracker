import sqlite3
from datetime import datetime, timedelta
import pandas as pd

DB_NAME = "inventory.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            expiry_date DATE NOT NULL
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM inventory")
    if cursor.fetchone()[0] == 0:
        today = datetime.now().date()
        sample_data = [
            ("Whole Milk 1L", "Dairy", 12, (today + timedelta(days=2)).isoformat()),
            ("Brown Artisan Bread", "Bakery", 18, (today - timedelta(days=1)).isoformat()),
            ("Canned Tomatoes 400g", "Pantry", 45, (today + timedelta(days=90)).isoformat()),
            ("Farm Eggs 12pk", "Dairy", 30, (today + timedelta(days=4)).isoformat()),
            ("Greek Yogurt 500g", "Dairy", 10, (today - timedelta(days=2)).isoformat()),
            ("Fresh Gala Apples 1kg", "Produce", 25, (today + timedelta(days=14)).isoformat()),
            ("Chicken Breast 500g", "Meat & Seafood", 15, (today + timedelta(days=3)).isoformat()),
            ("Orange Juice 1L", "Beverages", 20, (today + timedelta(days=8)).isoformat()),
        ]
        cursor.executemany(
            "INSERT INTO inventory (name, category, quantity, expiry_date) VALUES (?, ?, ?, ?)",
            sample_data,
        )
        conn.commit()
    conn.close()


def fetch_all_items():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM inventory ORDER BY expiry_date ASC", conn)
    conn.close()

    if not df.empty:
        today = datetime.now().date()
        df["expiry_date"] = pd.to_datetime(df["expiry_date"]).dt.date
        df["days_left"] = (df["expiry_date"] - today).apply(lambda x: x.days)

        def check_status(days):
            if days < 0:
                return "Expired"
            elif days <= 7:
                return "Expiring Soon"
            else:
                return "Safe"

        df["status"] = df["days_left"].apply(check_status)
    return df


def insert_item(name, category, quantity, expiry_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inventory (name, category, quantity, expiry_date) VALUES (?, ?, ?, ?)",
        (name, category, int(quantity), expiry_date.isoformat()),
    )
    conn.commit()
    conn.close()


def remove_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
