import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime

# Configure the page
st.set_page_config(page_title="Unemployment Analysis Dashboard", layout="wide")

# Inject dark theme styling
st.markdown("""
    <style>
        body, .stApp { background-color: #0e1117; color: white; }
        .block-container { padding: 1.5rem 2rem; }
        .stDataFrame th, .stDataFrame td { background-color: #1e222a; color: white; }
        .stButton>button { background-color: #2563eb; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; }
        .stButton>button:hover { background-color: #1d4ed8; }
    </style>
""", unsafe_allow_html=True)

# Title and instructions
st.title("📉 Unemployment Analysis Dashboard")
st.markdown("""
This dashboard allows you to:
- Upload unemployment data
- Analyze trends, spikes, and seasonal variations
- Visualize regional differences
- Filter by date range and export cleaned data
""")

# File uploader
uploaded_file = st.file_uploader("📁 Upload Unemployment Dataset (CSV format)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("🔍 Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    # Column selection
    all_cols = df.columns.tolist()
    date_col = st.selectbox("📅 Select Date Column", options=all_cols)
    rate_col = st.selectbox("📈 Select Unemployment Rate Column", options=all_cols)
    region_col = st.selectbox("🌍 (Optional) Select Region/State Column", options=[None] + all_cols)

    # Parse and clean date column
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    df = df.sort_values(by=date_col)

    # Filter valid rate values
    df[rate_col] = pd.to_numeric(df[rate_col], errors='coerce')

    # Date range filter with type-safe datetime conversion
    if not df.empty:
        min_date = df[date_col].min().to_pydatetime()
        max_date = df[date_col].max().to_pydatetime()
        date_range = st.slider("🗓️ Select Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))
        df = df[(df[date_col] >= pd.Timestamp(date_range[0])) & (df[date_col] <= pd.Timestamp(date_range[1]))]

    # Time series plot
    st.subheader("📆 Unemployment Rate Over Time")
    if region_col:
        fig = px.line(df, x=date_col, y=rate_col, color=region_col,
                      title="Unemployment Trends by Region", template="plotly_dark")
    else:
        fig = px.line(df, x=date_col, y=rate_col,
                      title="Overall Unemployment Trend", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # Key statistics
    st.subheader("📊 Key Statistics")
    col1, col2, col3 = st.columns(3)
    valid_rates = df[rate_col].dropna()

    if not valid_rates.empty:
        col1.metric("🔺 Peak Unemployment", f"{valid_rates.max():.2f}%")
        col2.metric("📉 Average Rate", f"{valid_rates.mean():.2f}%")
        col3.metric("✅ Lowest Rate", f"{valid_rates.min():.2f}%")
    else:
        col1.metric("🔺 Peak Unemployment", "N/A")
        col2.metric("📉 Average Rate", "N/A")
        col3.metric("✅ Lowest Rate", "N/A")

    # Missing values
    st.subheader("🛠️ Missing Value Summary")
    missing_df = df.isnull().sum().reset_index()
    missing_df.columns = ["Column", "Missing Values"]
    st.dataframe(missing_df[missing_df["Missing Values"] > 0], use_container_width=True)

    # Optional heatmap
    if st.checkbox("📌 Show Correlation Heatmap"):
        numeric_df = df.select_dtypes(include='number')
        if not numeric_df.empty:
            st.write("Correlation Heatmap:")
            fig2, ax = plt.subplots(figsize=(8, 5))
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig2)

    # Rolling average
    st.subheader("📉 Rolling Average")
    window = st.slider("Select Rolling Average Window (months)", min_value=1, max_value=12, value=3)
    df["RollingAvg"] = df[rate_col].rolling(window=window).mean()

    fig3 = px.line(df, x=date_col, y=[rate_col, "RollingAvg"], template="plotly_dark",
                   title="Unemployment Rate with Rolling Average")
    st.plotly_chart(fig3, use_container_width=True)

    # Export cleaned data
    st.subheader("⬇️ Export Filtered Data")
    cleaned_csv = df.to_csv(index=False)
    st.download_button("Download CSV", data=cleaned_csv, file_name="filtered_unemployment_data.csv", mime="text/csv")

else:
    st.info("📂 Please upload a CSV file containing at least a date and unemployment rate column.")
