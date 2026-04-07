# Video Game Sales Analytics Dashboard

This project is a Streamlit web app for analyzing video game sales data.

## Features
- Upload CSV file
- Clean missing values
- Filter by year, genre, platform, and publisher
- Show key metrics
- Display top games and platform tables
- Visualize:
  - Global sales by genre
  - Global sales trend by year
  - Top 10 platforms by sales
- Download filtered data

## Required dataset columns
- Name
- Platform
- Year
- Genre
- Publisher
- Global_Sales

Optional regional sales columns:
- NA_Sales
- EU_Sales
- JP_Sales
- Other_Sales

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
