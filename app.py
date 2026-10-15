import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Smart Expiry & Inventory Tracker",
    page_icon="📦",
    layout="wide",
)

DB_NAME = "inventory.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
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
            ("Whole Milk 1L", "Dairy", 10, (today + timedelta(days=2)).isoformat()),
            ("Brown Bread", "Bakery", 15, (today - timedelta(days=1)).isoformat()),
            ("Canned Tomatoes", "Pantry", 40, (today + timedelta(days=90)).isoformat()),
            ("Organic Eggs", "Dairy", 24, (today + timedelta(days=5)).isoformat()),
            ("Greek Yogurt", "Dairy", 8, (today - timedelta(days=3)).isoformat()),
            ("Fresh Apples 1kg", "Produce", 20, (today + timedelta(days=12)).isoformat()),
        ]
        cursor.executemany(
            "INSERT INTO inventory (name, category, quantity, expiry_date) VALUES (?, ?, ?, ?)",
            sample_data,
        )
        conn.commit()
    conn.close()


def get_data():
    conn = sqlite3.connect(DB_NAME)
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


def add_item(name, category, quantity, expiry_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inventory (name, category, quantity, expiry_date) VALUES (?, ?, ?, ?)",
        (name, category, quantity, expiry_date.isoformat()),
    )
    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


init_db()
st.title("📦 Smart Expiry & Inventory Tracker")
st.caption("Real-Time Stock Analytics & Perishable Waste Reduction Engine (UN SDG 12)")
st.divider()

df = get_data()

col1, col2, col3, col4 = st.columns(4)
total_items = len(df) if not df.empty else 0
expiring_soon = len(df[df["status"] == "Expiring Soon"]) if not df.empty else 0
expired = len(df[df["status"] == "Expired"]) if not df.empty else 0
safe = len(df[df["status"] == "Safe"]) if not df.empty else 0

col1.metric("Total Items", total_items)
col2.metric("Expiring Soon (<= 7 Days)", expiring_soon)
col3.metric("Expired Items", expired)
col4.metric("Safe Stock", safe)

st.divider()

st.sidebar.header("➕ Add New Inventory Item")
with st.sidebar.form("add_form", clear_on_submit=True):
    name = st.text_input("Item Name", placeholder="e.g. Cheddar Cheese")
    category = st.selectbox("Category", ["Dairy", "Bakery", "Produce", "Pantry", "Beverages"])
    quantity = st.number_input("Quantity", min_value=1, value=10)
    expiry_date = st.date_input("Expiry Date", datetime.now().date())
    submitted = st.form_submit_button("Add Item")

    if submitted:
        if name.strip():
            add_item(name, category, quantity, expiry_date)
            st.sidebar.success(f"Added {name}!")
            st.rerun()

left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📊 Category Stock Analytics")
    if not df.empty:
        cat_df = df.groupby("category")["quantity"].sum().reset_index()
        fig = px.bar(cat_df, x="category", y="quantity", color="category")
        st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("🗑️ Delete Items")
    if not df.empty:
        selected_item = st.selectbox(
            "Select item to remove:",
            options=df["id"].tolist(),
            format_func=lambda x: f"ID {x}: {df[df['id'] == x]['name'].values[0]}"
        )
        if st.button("Delete Selected Item", type="primary"):
            delete_item(selected_item)
            st.success("Item removed!")
            st.rerun()

st.divider()
st.subheader("📋 Current Stock Registry")
if not df.empty:
    st.dataframe(df[["id", "name", "category", "quantity", "expiry_date", "days_left", "status"]], use_container_width=True, hide_index=True)