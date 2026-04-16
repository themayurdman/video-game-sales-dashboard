import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Video Game Sales Dashboard", layout="wide")

st.title("🎮 Video Game Sales Analytics Dashboard")
st.markdown("Upload a **video game sales CSV** file and explore trends by year, genre, platform, and publisher.")

with st.expander("Expected columns"):
    st.write([
        "Name", "Platform", "Year", "Genre", "Publisher",
        "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"
    ])

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Please upload your dataset to start the analysis.")
    st.stop()


# Load and clean data

try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Error reading CSV file: {e}")
    st.stop()

required_columns = [
    "Name", "Platform", "Year", "Genre", "Publisher", "Global_Sales"
]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

numeric_cols = ["Year", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

before_rows = len(df)
df = df.dropna(subset=["Name", "Platform", "Year", "Genre", "Publisher", "Global_Sales"]).copy()
df["Year"] = df["Year"].astype(int)
after_rows = len(df)


# Sidebar filters

st.sidebar.header("Filter Data")

year_min = int(df["Year"].min())
year_max = int(df["Year"].max())
selected_years = st.sidebar.slider("Select Year Range", year_min, year_max, (year_min, year_max))

genre_options = sorted(df["Genre"].dropna().unique().tolist())
platform_options = sorted(df["Platform"].dropna().unique().tolist())
publisher_options = sorted(df["Publisher"].dropna().unique().tolist())

selected_genres = st.sidebar.multiselect("Select Genre(s)", genre_options, default=genre_options)
selected_platforms = st.sidebar.multiselect("Select Platform(s)", platform_options, default=platform_options)
selected_publishers = st.sidebar.multiselect("Select Publisher(s)", publisher_options, default=publisher_options)

filtered_df = df[
    (df["Year"].between(selected_years[0], selected_years[1])) &
    (df["Genre"].isin(selected_genres)) &
    (df["Platform"].isin(selected_platforms)) &
    (df["Publisher"].isin(selected_publishers))
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()


# Project summary

col_info1, col_info2 = st.columns([2, 1])
with col_info1:
    st.subheader("Project Summary")
    st.write(
        """
        This Streamlit application analyzes video game sales data from a CSV file.
        It cleans the data, applies interactive filters, calculates key business metrics,
        and visualizes trends using charts.
        """
    )
with col_info2:
    st.subheader("Data Cleaning")
    st.write(f"Rows before cleaning: **{before_rows}**")
    st.write(f"Rows after cleaning: **{after_rows}**")

st.divider()


# Key metrics

total_global_sales = filtered_df["Global_Sales"].sum()
total_games = filtered_df["Name"].nunique()
top_game_row = filtered_df.loc[filtered_df["Global_Sales"].idxmax()]
top_platform = (
    filtered_df.groupby("Platform")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
)
top_genre = (
    filtered_df.groupby("Genre")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Global Sales", f"{total_global_sales:,.2f} M")
m2.metric("Unique Games", f"{total_games:,}")
m3.metric("Top Platform", top_platform)
m4.metric("Top Genre", top_genre)

st.write(f"**Top Game by Global Sales:** {top_game_row['Name']} ({top_game_row['Global_Sales']:.2f} M)")

st.divider()


# Data preview

st.subheader("Filtered Dataset Preview")
st.dataframe(filtered_df.head(20), use_container_width=True)


# Analysis tables

left_table, right_table = st.columns(2)

with left_table:
    st.subheader("Top 10 Games by Global Sales")
    top_games = (
        filtered_df.groupby("Name", as_index=False)["Global_Sales"]
        .sum()
        .sort_values("Global_Sales", ascending=False)
        .head(10)
    )
    st.dataframe(top_games, use_container_width=True)

with right_table:
    st.subheader("Sales by Platform")
    sales_by_platform = (
        filtered_df.groupby("Platform", as_index=False)["Global_Sales"]
        .sum()
        .sort_values("Global_Sales", ascending=False)
    )
    st.dataframe(sales_by_platform, use_container_width=True)

st.divider()


# Charts

st.subheader("Visualizations")

# 1. Sales by Genre
genre_sales = (
    filtered_df.groupby("Genre")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
)

fig1, ax1 = plt.subplots(figsize=(10, 5))
genre_sales.plot(kind="bar", ax=ax1)
ax1.set_title("Global Sales by Genre")
ax1.set_xlabel("Genre")
ax1.set_ylabel("Global Sales (Millions)")
ax1.tick_params(axis="x", rotation=45)
st.pyplot(fig1)

# 2. Sales by Year
year_sales = (
    filtered_df.groupby("Year")["Global_Sales"]
    .sum()
    .sort_index()
)

fig2, ax2 = plt.subplots(figsize=(10, 5))
year_sales.plot(kind="line", marker="o", ax=ax2)
ax2.set_title("Global Sales Trend by Year")
ax2.set_xlabel("Year")
ax2.set_ylabel("Global Sales (Millions)")
st.pyplot(fig2)

# 3. Top 10 Platforms
platform_sales = (
    filtered_df.groupby("Platform")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig3, ax3 = plt.subplots(figsize=(10, 5))
platform_sales.plot(kind="bar", ax=ax3)
ax3.set_title("Top 10 Platforms by Global Sales")
ax3.set_xlabel("Platform")
ax3.set_ylabel("Global Sales (Millions)")
ax3.tick_params(axis="x", rotation=45)
st.pyplot(fig3)


# Download section

st.divider()
st.subheader("Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered dataset as CSV",
    data=csv,
    file_name="filtered_video_game_sales.csv",
    mime="text/csv"
)
