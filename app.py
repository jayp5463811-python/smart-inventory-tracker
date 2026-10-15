import io
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. PAGE CONFIGURATION & CUSTOM CSS INJECTION
st.set_page_config(
    page_title="Smart Expiry & Inventory Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Glassmorphism UI Styling
st.markdown(
    """
    <style>
    /* Dark Theme Custom Background */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header Container Styling */
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    /* Custom Metric Card Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    
    div[data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Table styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #334155;
    }
    
    /* Custom Badges */
    .badge-safe {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(245, 158, 11, 0.3);
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(239, 68, 68, 0.3);
        font-weight: 600;
        font-size: 0.85rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

DB_NAME = "inventory.db"


# 2. DATABASE ENGINE & DATA PROCESSING
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
        (name, category, int(quantity), expiry_date.isoformat()),
    )
    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


# Initialize Database
init_db()
df = get_data()

# 3. HEADER & TITLE SECTION
st.markdown(
    """
    <div class="header-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin:0; font-size: 2.2rem; font-weight: 800; color: #ffffff;">⚡ Smart Expiry & Inventory Engine</h1>
                <p style="margin-top: 6px; margin-bottom: 0; color: #94a3b8; font-size: 0.95rem;">
                    Proactive Perishable Goods Monitoring & Automated Waste Prevention Hub (UN SDG 12 Aligned)
                </p>
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# 4. KPI METRICS BAR
if not df.empty:
    total_items = len(df)
    total_qty = df["quantity"].sum()
    expiring_soon = len(df[df["status"] == "Expiring Soon"])
    expired = len(df[df["status"] == "Expired"])
    safe = len(df[df["status"] == "Safe"])
else:
    total_items, total_qty, expiring_soon, expired, safe = 0, 0, 0, 0, 0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("📦 Total SKUs", total_items)
m2.metric("📊 Total Units", total_qty)
m3.metric("⚠️ Expiring Soon (<= 7d)", expiring_soon)
m4.metric("🚨 Expired Items", expired)
m5.metric("✅ Safe Inventory", safe)

st.markdown("<br>", unsafe_allow_html=True)

# 5. TABBED INTERFACE SYSTEM
tab_dash, tab_ops, tab_analytics = st.tabs([
    "📊 Live Registry & Filters",
    "⚙️ Inventory Operations",
    "🌱 SDG 12 Impact Analytics",
])

# ----------------- TAB 1: DASHBOARD & LIVE REGISTRY -----------------
with tab_dash:
    st.subheader("🔍 Interactive Stock Explorer")

    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])

    with f_col1:
        search_term = st.text_input(
            "Search Item Name", placeholder="🔍 Search e.g. Milk, Eggs, Bread..."
        )
    with f_col2:
        status_filter = st.multiselect(
            "Filter Status",
            options=["Safe", "Expiring Soon", "Expired"],
            default=["Safe", "Expiring Soon", "Expired"],
        )
    with f_col3:
        categories = ["All"] + list(df["category"].unique()) if not df.empty else ["All"]
        category_filter = st.selectbox("Category", options=categories)

    # Filter Logic
    filtered_df = df.copy() if not df.empty else pd.DataFrame()
    if not filtered_df.empty:
        if search_term:
            filtered_df = filtered_df[
                filtered_df["name"].str.contains(search_term, case=False)
            ]
        if status_filter:
            filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
        if category_filter != "All":
            filtered_df = filtered_df[filtered_df["category"] == category_filter]

    # Data Display
    st.markdown("##### Current Stock Inventory Table")
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[
                ["id", "name", "category", "quantity", "expiry_date", "days_left", "status"]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "name": st.column_config.TextColumn("Item Name", width="large"),
                "category": st.column_config.TextColumn("Category"),
                "quantity": st.column_config.NumberColumn("Stock Units"),
                "expiry_date": st.column_config.DateColumn("Expiry Date"),
                "days_left": st.column_config.NumberColumn("Days Remaining"),
                "status": st.column_config.TextColumn("Risk Category"),
            },
        )

        # Export CSV Button
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Filtered Inventory Report (CSV)",
            data=csv_data,
            file_name=f"inventory_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No stock records match the selected filters.")

# ----------------- TAB 2: OPERATIONS (ADD / DELETE) -----------------
with tab_ops:
    op_col1, op_col2 = st.columns([1, 1])

    with op_col1:
        st.subheader("➕ Register New Stock Item")
        with st.form("add_item_form", clear_on_submit=True):
            new_name = st.text_input("Item Name", placeholder="e.g. Fresh Mozzarella Cheese")
            new_cat = st.selectbox(
                "Category",
                [
                    "Dairy",
                    "Bakery",
                    "Produce",
                    "Pantry",
                    "Beverages",
                    "Meat & Seafood",
                    "Frozen",
                ],
            )
            new_qty = st.number_input("Quantity in Units", min_value=1, value=10)
            new_expiry = st.date_input("Expiration Date", datetime.now().date())

            submit_btn = st.form_submit_button("Submit Item to Registry", type="primary")

            if submit_btn:
                if new_name.strip():
                    add_item(new_name, new_cat, new_qty, new_expiry)
                    st.success(f"Successfully added '{new_name}' to database!")
                    st.rerun()
                else:
                    st.error("Please enter a valid item name.")

    with op_col2:
        st.subheader("🗑️ Remove Consumed / Discarded Item")
        if not df.empty:
            item_to_delete = st.selectbox(
                "Select SKU to Remove:",
                options=df["id"].tolist(),
                format_func=lambda x: f"ID #{x} - {df[df['id'] == x]['name'].values[0]} ({df[df['id'] == x]['status'].values[0]})",
            )

            if st.button("Delete Selected SKU", type="secondary"):
                delete_item(item_to_delete)
                st.success(f"Item #{item_to_delete} deleted from inventory!")
                st.rerun()
        else:
            st.info("No items available to delete.")

# ----------------- TAB 3: VISUAL ANALYTICS -----------------
with tab_analytics:
    st.subheader("📊 Inventory Analytics & SDG 12 Impact")

    if not df.empty:
        c1, c2 = st.columns([1, 1])

        with c1:
            st.markdown("##### Stock Density by Category")
            cat_data = df.groupby("category")["quantity"].sum().reset_index()
            fig_bar = px.bar(
                cat_data,
                x="category",
                y="quantity",
                color="category",
                text="quantity",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_bar.update_layout(
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.markdown("##### Expiry Risk
