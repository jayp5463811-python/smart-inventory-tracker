# 📦 Smart Expiry & Inventory Tracker

> An intelligent, full-stack Python analytics engine designed to combat perishable inventory waste in small retail businesses and households. Aligned with **UN Sustainable Development Goal 12: Responsible Consumption and Production**.

---

## 📌 Executive Summary

Food and perishable item waste is a multi-billion-dollar global problem. Small businesses and households frequently incur financial losses due to unmonitored stock expiration dates and poor inventory visibility. 

**Smart Expiry & Inventory Tracker** addresses this real-world challenge by providing a centralized dashboard that automatically monitors stock levels, computes real-time expiry countdowns, categorizes items by urgency, and presents interactive visual analytics—all powered by a lightweight local database engine.

---

## 🔥 Key Features

- **Automated Expiry Engine:** Dynamically calculates days remaining for every item and classifies status into three risk categories:
  - 🟢 **Safe:** Expiry date is more than 7 days away.
  - 🟡 **Expiring Soon:** Expiry date is within 7 days (High Priority Alert).
  - 🔴 **Expired:** Item has passed its expiration date.
- **Real-Time KPI Dashboard:** Key performance metrics showing total stock count, high-risk items, expired goods, and safe inventory.
- **Interactive Visual Analytics:** Dynamic category-wise stock distribution charts built with Plotly.
- **Full Database CRUD Engine:** Effortlessly register new inventory, manage stock quantities, and remove consumed/discarded items.
- **Zero-Config Database:** Lightweight, self-contained SQLite3 relational backend.

---

## 🛠️ Tech Stack & Architecture

| Layer | Technology Used |
| :--- | :--- |
| **Primary Language** | Python 3.10+ |
| **Frontend UI / Framework** | Streamlit |
| **Data Processing** | Pandas |
| **Data Visualization** | Plotly Express |
| **Database** | SQLite3 (Relational Database) |
| **Version Control** | Git & GitHub |

### System Architecture Flow

```text
[ User Interface (Streamlit) ]
              │
              ▼
[ Python Application Logic (app.py) ]
              │
      ┌───────┴───────┐
      ▼               ▼
[ Plotly Analytics ] [ SQLite Engine (inventory.db) ]
