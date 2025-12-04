# pages/1_Home.py
import streamlit as st
import plotly.express as px
from utils import load_data, top_n

st.set_page_config(page_title="Fome Zero — Home", page_icon=":fork_and_knife:")

df = load_data()

st.image("logo.png", width=180)
st.title("Fome Zero — Painel Geral")
st.markdown("Visão executiva: principais indicadores, top cozinhas e distribuição de avaliações.")

# KPIs simples
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Restaurantes", f"{len(df):,}")
with col2:
    mean_rating = df["rating"].mean() if "rating" in df.columns else None
    st.metric("Avaliação média", f"{mean_rating:.2f}" if mean_rating else "—")
with col3:
    countries = df["country"].nunique() if "country" in df.columns else 0
    st.metric("Países", countries)

st.markdown("---")

# Top cuisines (bar)
if "cuisine" in df.columns:
    top_cuis = top_n(df, "cuisine", "restaurant_id" if "restaurant_id" in df.columns else "name", n=10, agg="count")
    fig = px.bar(top_cuis, x="cuisine", y="value", labels={"value":"# Restaurantes","cuisine":"Culinária"}, title="Top 10 Culinárias por número de restaurantes")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Distribuição de avaliações (scatter by price)
if "rating" in df.columns:
    scatter_df = df.dropna(subset=["rating"])
    if "price_num" in df.columns:
        fig2 = px.scatter(scatter_df.sample(min(len(scatter_df),2000)), x="price_num", y="rating", hover_data=["name","city","country"], trendline="ols", labels={"price_num":"Faixa de preço (num)","rating":"Avaliação"})
        fig2.update_layout(title="Rating vs Faixa de Preço (amostra)")
    else:
        fig2 = px.histogram(scatter_df, x="rating", nbins=20, title="Distribuição de Avaliações")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("**Observação:** navegue pelas abas para análises por país, cidade e tipo de cozinha. Cada aba oferece insights distintos e não repetidos.")
