import pandas as pd
import streamlit as st

@st.cache_data
def load_data(path="dataset/zomato.csv"):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
COUNTRY_MAP = {
    1: "India", 14: "Australia", 30: "Brazil", 37: "Canada",
    94: "Indonesia", 148: "New Zealand", 162: "Philippines",
    166: "Qatar", 184: "Singapore", 189: "South Africa",
    191: "Sri Lanka", 208: "Turkey", 214: "United Arab Emirates",
    215: "United Kingdom", 216: "United States"
}


    # Ajuste de tipos
    if "latitude" in df.columns:
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    if "longitude" in df.columns:
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    if "price" in df.columns:
        df["price_num"] = df["price"].astype(str).apply(lambda x: x.count("₹"))

    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
        
    if "country code" in df.columns:
    df["country"] = df["country code"].map(COUNTRY_MAP)


    return df

def top_n(df, groupby_col, value_col, n=10, agg="count"):
    if agg == "count":
        g = df.groupby(groupby_col)[value_col].count().sort_values(ascending=False).head(n)
    else:
        g = df.groupby(groupby_col)[value_col].agg(agg).sort_values(ascending=False).head(n)
    return g.reset_index().rename(columns={value_col: "value"})
