from datetime import datetime
import pandas as pd
import streamlit as st

import analytics
import database

st.set_page_config(
    page_title="Smart Expiry & Inventory Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 25px;
    }
    div[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 800 !important; }
    div[data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 16px;
        border-radius: 12px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

database.init_db()
df = database.fetch_all_items()

st.markdown(
    """
    <div class="header-box">
        <h1 style="margin:0; font-size: 2.2rem; font-weight: 800; color: #ffffff;">⚡ Smart Expiry & Inventory Engine</h1>
        <p style="margin-top: 6px; margin-bottom: 0; color: #94a3b8; font-size: 0.95rem;">
            Proactive Perishable Goods Monitoring & Automated Waste Prevention Hub (UN SDG 12 Aligned)
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

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
m3.metric("⚠️ Expiring Soon", expiring_soon)
m4.metric("🚨 Expired Items", expired)
m5.metric("✅ Safe Inventory", safe)

st.markdown("<br>", unsafe_allow_html=True)

tab_dash, tab_ops, tab_analytics = st.tabs([
    "📊 Live Registry & Filters",
    "⚙️ Inventory Operations",
    "🌱 SDG 12 Impact Analytics",
])

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

    st.markdown("##### Current Stock Inventory Table")
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[
                ["id", "name", "category", "quantity", "expiry_date", "days_left", "status"]
            ],
            use_container_width=True,
            hide_index=True,
        )
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Filtered Inventory Report (CSV)",
            data=csv_data,
            file_name=f"inventory_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No stock records match the selected filters.")

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
                    database.insert_item(new_name, new_cat, new_qty, new_expiry)
                    st.success(f"Successfully added '{new_name}'!")
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
                database.remove_item(item_to_delete)
                st.success(f"Item #{item_to_delete} deleted!")
                st.rerun()
        else:
            st.info("No items available to delete.")

with tab_analytics:
    st.subheader("📊 Inventory Analytics & SDG 12 Impact")
    if not df.empty:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("##### Stock Density by Category")
            fig_bar = analytics.build_category_chart(df)
            if fig_bar:
                st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            st.markdown("##### Expiry Risk Breakdown")
            fig_pie = analytics.build_risk_chart(df)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Add inventory items to generate real-time analytics.")
