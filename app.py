import streamlit as st
import pandas as pd
import plotly.express as px

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


# ── Load & clean

@st.cache_data
def load_data(file):
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return None, str(e), None

    required = ["Name", "Platform", "Year", "Genre", "Publisher", "Global_Sales"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return None, f"Missing required columns: {missing}", None

    numeric_cols = ["Year", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    before = len(df)
    df = df.dropna(subset=required).copy()
    df["Year"] = df["Year"].astype(int)
    after = len(df)

    return df, before, after

result = load_data(uploaded_file)
if result[0] is None:
    st.error(result[1])
    st.stop()

df, before_rows, after_rows = result


# ── Sidebar filters 

st.sidebar.header("Filter Data")

year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
selected_years = st.sidebar.slider("Year Range", year_min, year_max, (year_min, year_max))

genre_options     = sorted(df["Genre"].dropna().unique())
platform_options  = sorted(df["Platform"].dropna().unique())
publisher_options = sorted(df["Publisher"].dropna().unique())

selected_genres    = st.sidebar.multiselect("Genre(s)",     genre_options,   default=genre_options)
selected_platforms = st.sidebar.multiselect("Platform(s)", platform_options, default=platform_options)

# Publisher: blank = all (avoids bloated sidebar with 500+ names)
selected_publishers = st.sidebar.multiselect(
    "Publisher(s) — leave blank for all",
    publisher_options,
    default=[]
)
pub_filter = selected_publishers if selected_publishers else publisher_options

filtered_df = df[
    df["Year"].between(selected_years[0], selected_years[1]) &
    df["Genre"].isin(selected_genres) &
    df["Platform"].isin(selected_platforms) &
    df["Publisher"].isin(pub_filter)
].copy()

if filtered_df.empty:
    st.warning("No data for selected filters.")
    st.stop()


# ── Summary row 

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Project Summary")
    st.write(
        "Analyzes video game sales data from a CSV file. "
        "Cleans data, applies interactive filters, computes key metrics, "
        "and visualizes trends with interactive Plotly charts."
    )
with col2:
    st.subheader("Data Cleaning")
    st.write(f"Rows before cleaning: **{before_rows}**")
    st.write(f"Rows after cleaning:  **{after_rows}**")

st.divider()


# ── Key metrics

total_sales   = filtered_df["Global_Sales"].sum()
total_games   = filtered_df["Name"].nunique()
top_game_row  = filtered_df.loc[filtered_df["Global_Sales"].idxmax()]
top_platform  = filtered_df.groupby("Platform")["Global_Sales"].sum().idxmax()
top_genre     = filtered_df.groupby("Genre")["Global_Sales"].sum().idxmax()
top_publisher = filtered_df.groupby("Publisher")["Global_Sales"].sum().idxmax()

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Global Sales", f"{total_sales:,.2f} M")
m2.metric("Unique Games",       f"{total_games:,}")
m3.metric("Top Platform",       top_platform)
m4.metric("Top Genre",          top_genre)
m5.metric("Top Publisher",      top_publisher)

st.write(f"**Top Game:** {top_game_row['Name']} — {top_game_row['Global_Sales']:.2f} M units")

st.divider()


# ── Data preview 

st.subheader("Filtered Dataset Preview")
st.dataframe(filtered_df.head(20), use_container_width=True)


# ── Tables 

left_table, right_table = st.columns(2)

with left_table:
    st.subheader("Top 10 Games by Global Sales")
    top_games = (
        filtered_df.groupby("Name", as_index=False)["Global_Sales"]
        .sum()
        .sort_values("Global_Sales", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    top_games.index += 1
    st.dataframe(top_games, use_container_width=True)

with right_table:
    st.subheader("Top 10 Publishers by Global Sales")
    pub_sales = (
        filtered_df.groupby("Publisher", as_index=False)["Global_Sales"]
        .sum()
        .sort_values("Global_Sales", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    pub_sales.index += 1
    st.dataframe(pub_sales, use_container_width=True)

st.divider()


# ── Charts 

st.subheader("Visualizations")

# 1. Sales by Genre
genre_sales = (
    filtered_df.groupby("Genre")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
fig1 = px.bar(
    genre_sales, x="Genre", y="Global_Sales",
    title="Global Sales by Genre",
    labels={"Global_Sales": "Sales (M)"},
    color="Global_Sales", color_continuous_scale="Blues"
)
st.plotly_chart(fig1, use_container_width=True)

# 2. Sales trend by Year
year_sales = (
    filtered_df.groupby("Year")["Global_Sales"]
    .sum()
    .reset_index()
    .sort_values("Year")
)
fig2 = px.line(
    year_sales, x="Year", y="Global_Sales",
    title="Global Sales Trend by Year",
    labels={"Global_Sales": "Sales (M)"},
    markers=True
)
st.plotly_chart(fig2, use_container_width=True)

# 3. Top 10 Platforms
platform_sales = (
    filtered_df.groupby("Platform")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
fig3 = px.bar(
    platform_sales, x="Platform", y="Global_Sales",
    title="Top 10 Platforms by Global Sales",
    labels={"Global_Sales": "Sales (M)"},
    color="Global_Sales", color_continuous_scale="Greens"
)
st.plotly_chart(fig3, use_container_width=True)

# 4. Regional breakdown (only if regional cols present)
regional_cols = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
if all(c in filtered_df.columns for c in regional_cols):
    region_totals = filtered_df[regional_cols].sum().reset_index()
    region_totals.columns = ["Region", "Sales"]
    region_totals["Region"] = region_totals["Region"].str.replace("_Sales", "")
    fig4 = px.pie(
        region_totals, names="Region", values="Sales",
        title="Sales Distribution by Region",
        hole=0.4
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()


# ── Download

st.subheader("Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇ Download filtered dataset as CSV",
    data=csv,
    file_name="filtered_video_game_sales.csv",
    mime="text/csv"
)
