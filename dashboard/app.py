# dashboard/app.py
# ============================================================
# Streamlit Dashboard — AI-Powered Business Intelligence
# Run: streamlit run dashboard/app.py
# ============================================================

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text

from database.connection import engine

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Business Intelligence Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        padding: 20px; border-radius: 12px; color: white;
        text-align: center; margin: 5px;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #4fc3f7; }
    .metric-label { font-size: 13px; color: #b0bec5; margin-top: 4px; }
    .alert-high { background: #ff1744; color: white; padding: 8px 12px;
                  border-radius: 6px; margin: 4px 0; }
    .alert-medium { background: #ff9100; color: white; padding: 8px 12px;
                    border-radius: 6px; margin: 4px 0; }
    .alert-low { background: #00bcd4; color: white; padding: 8px 12px;
                 border-radius: 6px; margin: 4px 0; }
    .stButton>button { width: 100%; background: #1565c0;
                       color: white; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ── Data loading functions ────────────────────────────────────

@st.cache_data(ttl=300)
def load_data(query: str) -> pd.DataFrame:
    """Load data from PostgreSQL with caching."""
    try:
        with engine.connect() as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()


def get_kpis():
    df = load_data("""
        SELECT
            ROUND(SUM(revenue)::numeric, 2) as total_revenue,
            COUNT(*) as total_orders,
            COUNT(DISTINCT customer_id) as unique_customers,
            ROUND(AVG(revenue)::numeric, 2) as avg_order_value
        FROM sales WHERE status='Completed'
    """)
    return df.iloc[0] if not df.empty else {}


def get_revenue_by_region():
    return load_data("""
        SELECT region, ROUND(SUM(revenue)::numeric, 2) as revenue,
               COUNT(*) as orders
        FROM sales WHERE status='Completed'
        GROUP BY region ORDER BY revenue DESC
    """)


def get_revenue_by_category():
    return load_data("""
        SELECT s.category, ROUND(SUM(s.revenue)::numeric, 2) as revenue,
               ROUND(AVG(p.margin_pct)::numeric, 1) as avg_margin
        FROM sales s JOIN products p ON s.product_id = p.product_id
        WHERE s.status='Completed'
        GROUP BY s.category ORDER BY revenue DESC
    """)


def get_monthly_trend():
    return load_data("""
        SELECT sale_month, ROUND(SUM(revenue)::numeric, 2) as revenue,
               COUNT(*) as orders
        FROM sales WHERE status='Completed'
        GROUP BY sale_month ORDER BY sale_month
    """)


def get_top_products():
    return load_data("""
        SELECT p.name, p.category,
               ROUND(SUM(s.revenue)::numeric, 2) as revenue,
               SUM(s.quantity) as units
        FROM sales s JOIN products p ON s.product_id = p.product_id
        WHERE s.status='Completed'
        GROUP BY p.name, p.category ORDER BY revenue DESC LIMIT 10
    """)


def get_customer_segments():
    return load_data("""
        SELECT segment, COUNT(*) as count,
               ROUND(AVG(age)::numeric, 1) as avg_age
        FROM customers GROUP BY segment
    """)


def get_low_stock():
    return load_data("""
        SELECT product_name, stock_qty, reorder_level,
               (reorder_level - stock_qty) as shortage
        FROM inventory_snapshots
        WHERE needs_reorder = true
          AND snapshot_date = (SELECT MAX(snapshot_date) FROM inventory_snapshots)
        ORDER BY stock_qty ASC LIMIT 10
    """)


def get_order_status():
    return load_data("""
        SELECT status, COUNT(*) as count,
               ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(), 1) as pct
        FROM sales GROUP BY status ORDER BY count DESC
    """)


# ── Sidebar ───────────────────────────────────────────────────

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    st.title("AI BI Platform")
    st.caption("Powered by Ollama + PostgreSQL")
    st.divider()

    page = st.radio("Navigation", [
        "📊 Dashboard",
        "🤖 AI Query",
        "🚨 Alerts",
        "📦 Inventory",
        "👥 Customers",
    ])

    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE 1: DASHBOARD
# ══════════════════════════════════════════════════════════════

if page == "📊 Dashboard":
    st.title("📊 Business Intelligence Dashboard")
    st.caption("Real-time analytics from your PostgreSQL database")

    # KPI Cards
    kpis = get_kpis()
    if len(kpis):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Total Revenue",
                  f"₹{float(kpis['total_revenue']):,.0f}")
        c2.metric("📦 Total Orders",
                  f"{int(kpis['total_orders']):,}")
        c3.metric("👥 Unique Customers",
                  f"{int(kpis['unique_customers']):,}")
        c4.metric("🛒 Avg Order Value",
                  f"₹{float(kpis['avg_order_value']):,.0f}")

    st.divider()

    # Charts Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Region")
        df_region = get_revenue_by_region()
        if not df_region.empty:
            fig = px.bar(df_region, x="region", y="revenue",
                        color="revenue", color_continuous_scale="Blues",
                        text_auto=".2s")
            fig.update_layout(showlegend=False, height=350,
                             plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Revenue by Category")
        df_cat = get_revenue_by_category()
        if not df_cat.empty:
            fig = px.pie(df_cat, names="category", values="revenue",
                        hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    # Charts Row 2
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Monthly Revenue Trend")
        df_trend = get_monthly_trend()
        if not df_trend.empty:
            fig = px.line(df_trend, x="sale_month", y="revenue",
                         markers=True, line_shape="spline")
            fig.update_traces(line_color="#1565c0", line_width=2.5)
            fig.update_layout(height=350, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Order Status Distribution")
        df_status = get_order_status()
        if not df_status.empty:
            colors = {"Completed": "#4caf50", "Returned": "#ff9800",
                     "Cancelled": "#f44336", "Pending": "#2196f3"}
            fig = px.bar(df_status, x="status", y="count",
                        color="status",
                        color_discrete_map=colors,
                        text="pct")
            fig.update_traces(texttemplate="%{text}%")
            fig.update_layout(showlegend=False, height=350,
                             plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    # Top Products Table
    st.subheader("🏆 Top 10 Products by Revenue")
    df_products = get_top_products()
    if not df_products.empty:
        df_products["revenue"] = df_products["revenue"].apply(
            lambda x: f"₹{float(x):,.2f}")
        st.dataframe(df_products, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# PAGE 2: AI QUERY
# ══════════════════════════════════════════════════════════════

elif page == "🤖 AI Query":
    st.title("🤖 AI Natural Language Query")
    st.caption("Ask business questions in plain English — powered by Ollama (qwen2.5-coder)")

    # Sample questions
    st.subheader("💡 Try these questions:")
    samples = [
        "Which region had the highest revenue?",
        "What are the top 5 products by total revenue?",
        "How many customers are in each segment?",
        "Which category has the highest profit margin?",
        "Show monthly revenue trend for 2024",
    ]

    cols = st.columns(len(samples))
    for i, (col, q) in enumerate(zip(cols, samples)):
        if col.button(f"Q{i+1}", help=q):
            st.session_state.question = q

    st.divider()

    question = st.text_input(
        "Your question:",
        value=st.session_state.get("question", ""),
        placeholder="e.g. Which region had the highest revenue?"
    )

    if st.button("🔍 Ask AI", type="primary") and question:
        with st.spinner("🤖 AI is thinking... (may take 30-60 seconds)"):
            try:
                from ai_query.nl_to_sql import ask_question
                result = ask_question(question)

                st.success("✅ Answer ready!")

                st.subheader("💡 AI Insight")
                st.info(result["explanation"])

                if result["data"]:
                    st.subheader(f"📊 Data ({result['row_count']} rows)")
                    df = pd.DataFrame(result["data"])
                    st.dataframe(df, use_container_width=True)

                    # Auto-chart if numeric columns exist
                    numeric_cols = df.select_dtypes(include="number").columns
                    text_cols = df.select_dtypes(exclude="number").columns
                    if len(numeric_cols) > 0 and len(text_cols) > 0:
                        fig = px.bar(df, x=text_cols[0], y=numeric_cols[0],
                                    color_discrete_sequence=["#1565c0"])
                        st.plotly_chart(fig, use_container_width=True)

                with st.expander("🔍 View Generated SQL"):
                    st.code(result["sql"], language="sql")

                st.caption(f"⏱ Answered in {result['execution_ms']}ms")

            except Exception as e:
                st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════
# PAGE 3: ALERTS
# ══════════════════════════════════════════════════════════════

elif page == "🚨 Alerts":
    st.title("🚨 Business Alerts")
    st.caption("Real-time anomaly detection")

    df_stock = get_low_stock()
    df_status = get_order_status()

    # Inventory Alert
    if not df_stock.empty:
        st.error(f"🔴 HIGH: {len(df_stock)} products below reorder level")
        st.dataframe(df_stock, use_container_width=True, hide_index=True)
    else:
        st.success("✅ All inventory levels healthy")

    st.divider()

    # Cancellation Alert
    if not df_status.empty:
        cancelled = df_status[df_status["status"] == "Cancelled"]
        if not cancelled.empty:
            pct = float(cancelled.iloc[0]["pct"])
            if pct > 10:
                st.warning(f"🟡 MEDIUM: High cancellation rate — {pct}%")
            else:
                st.success(f"✅ Cancellation rate normal — {pct}%")

    st.divider()
    st.subheader("Order Status Breakdown")
    if not df_status.empty:
        fig = px.pie(df_status, names="status", values="count",
                    color="status",
                    color_discrete_map={"Completed": "#4caf50",
                                       "Returned": "#ff9800",
                                       "Cancelled": "#f44336",
                                       "Pending": "#2196f3"})
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PAGE 4: INVENTORY
# ══════════════════════════════════════════════════════════════

elif page == "📦 Inventory":
    st.title("📦 Inventory Management")

    df_stock = get_low_stock()
    all_inventory = load_data("""
        SELECT category, COUNT(*) as products,
               SUM(stock_qty) as total_stock,
               SUM(CASE WHEN needs_reorder THEN 1 ELSE 0 END) as needs_reorder
        FROM inventory_snapshots
        WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM inventory_snapshots)
        GROUP BY category ORDER BY total_stock DESC
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("⚠️ Products Needing Reorder", len(df_stock))
    with col2:
        if not all_inventory.empty:
            st.metric("📦 Total Stock Units",
                     f"{int(all_inventory['total_stock'].sum()):,}")

    if not all_inventory.empty:
        fig = px.bar(all_inventory, x="category", y="total_stock",
                    color="needs_reorder", title="Stock by Category",
                    color_continuous_scale="RdYlGn_r")
        st.plotly_chart(fig, use_container_width=True)

    if not df_stock.empty:
        st.subheader("🔴 Products Needing Reorder")
        st.dataframe(df_stock, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# PAGE 5: CUSTOMERS
# ══════════════════════════════════════════════════════════════

elif page == "👥 Customers":
    st.title("👥 Customer Analytics")

    df_seg = get_customer_segments()
    df_city = load_data("""
        SELECT city, COUNT(*) as customers,
               segment
        FROM customers WHERE is_active = true
        GROUP BY city, segment ORDER BY customers DESC LIMIT 20
    """)
    df_age = load_data("""
        SELECT segment,
               ROUND(AVG(age)::numeric,1) as avg_age,
               MIN(age) as min_age, MAX(age) as max_age
        FROM customers GROUP BY segment
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Segments")
        if not df_seg.empty:
            fig = px.pie(df_seg, names="segment", values="count",
                        hole=0.4,
                        color_discrete_sequence=["#1565c0","#42a5f5","#90caf9"])
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Age by Segment")
        if not df_age.empty:
            fig = px.bar(df_age, x="segment", y="avg_age",
                        color="segment", text="avg_age",
                        color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_traces(texttemplate="%{text:.1f} yrs")
            fig.update_layout(showlegend=False,
                             plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Cities by Active Customers")
    if not df_city.empty:
        city_count = df_city.groupby("city")["customers"].sum().reset_index()
        city_count = city_count.sort_values("customers", ascending=False).head(10)
        fig = px.bar(city_count, x="city", y="customers",
                    color="customers", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)
