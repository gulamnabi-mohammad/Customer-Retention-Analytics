import streamlit as st
import pandas as pd
import os

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Customer Retention Analytics", layout="wide")

st.title("🏦 Customer Engagement & Retention Dashboard")

# -------------------- LOAD DATA (AUTO SEARCH FIX) --------------------
@st.cache_data
def load_data():
    for root, dirs, files in os.walk("."):
        if "churn.csv" in files:
            file_path = os.path.join(root, "churn.csv")
            df = pd.read_csv(file_path)
            return df
    
    st.error("churn.csv file not found in project!")
    return pd.DataFrame()

df = load_data()

# Stop if data not loaded
if df.empty:
    st.stop()

# -------------------- FEATURE ENGINEERING --------------------
df['EngagementScore'] = (
    df['IsActiveMember'] * 2 +
    df['HasCrCard'] * 1 +
    df['NumOfProducts']
)

def segment(row):
    if row['IsActiveMember'] == 1 and row['NumOfProducts'] >= 2:
        return "Highly Engaged"
    elif row['IsActiveMember'] == 0 and row['Balance'] > 100000:
        return "High Value - Disengaged"
    elif row['NumOfProducts'] == 1:
        return "Low Product User"
    else:
        return "Moderate"

df['Segment'] = df.apply(segment, axis=1)

df['RetentionScore'] = (
    df['EngagementScore'] * 0.6 +
    df['NumOfProducts'] * 0.4
)

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("🔎 Filters")

product_filter = st.sidebar.slider("Minimum Products", 1, 4, 1)
activity_filter = st.sidebar.selectbox("Active Member", ["All", "Yes", "No"])
balance_filter = st.sidebar.slider("Minimum Balance", 0, int(df['Balance'].max()), 0)

filtered_df = df[df['NumOfProducts'] >= product_filter]
filtered_df = filtered_df[filtered_df['Balance'] >= balance_filter]

if activity_filter == "Yes":
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 1]
elif activity_filter == "No":
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 0]

# -------------------- KPIs --------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

churn_rate = filtered_df['Exited'].mean()
avg_balance = filtered_df['Balance'].mean()
avg_products = filtered_df['NumOfProducts'].mean()
avg_retention = filtered_df['RetentionScore'].mean()

col1.metric("Churn Rate", f"{churn_rate:.2%}")
col2.metric("Avg Balance", f"{avg_balance:,.0f}")
col3.metric("Avg Products", f"{avg_products:.2f}")
col4.metric("Retention Score", f"{avg_retention:.2f}")

# -------------------- CHARTS --------------------
st.subheader("📈 Analytics")

col1, col2 = st.columns(2)

with col1:
    st.write("Churn by Number of Products")
    st.bar_chart(filtered_df.groupby('NumOfProducts')['Exited'].mean())

with col2:
    st.write("Churn by Activity Status")
    st.bar_chart(filtered_df.groupby('IsActiveMember')['Exited'].mean())

# -------------------- ENGAGEMENT VS CHURN --------------------
st.subheader("📊 Engagement vs Churn")

engagement_churn = df.groupby('EngagementScore')['Exited'].mean()
st.line_chart(engagement_churn)

# -------------------- CUSTOMER SEGMENTATION --------------------
st.subheader("👥 Customer Segmentation")

segment_counts = df['Segment'].value_counts()
st.bar_chart(segment_counts)

# -------------------- HIGH VALUE DISENGAGED --------------------
st.subheader("⚠️ High Value - Disengaged Customers")

risk_customers = df[
    (df['Balance'] > 100000) &
    (df['IsActiveMember'] == 0)
]

st.metric("At-Risk Customers", len(risk_customers))
st.dataframe(risk_customers.head(10))

# -------------------- INSIGHTS --------------------
st.subheader("📌 Key Insights")

st.markdown("""
- Customers with higher engagement scores show lower churn.
- Multi-product users are more loyal compared to single-product users.
- High-balance inactive customers are at high risk of churn.
- Engagement is a stronger driver of retention than financial metrics.
""")

# -------------------- RAW DATA --------------------
st.subheader("📄 Filtered Data")
st.dataframe(filtered_df)
