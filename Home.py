import streamlit as st
import plotly.express as px
from utils import load_data, top_n

st.set_page_config(page_title="Home - Fome Zero", layout="wide")

# Carrega dados
df = load_data()

# --- Sidebar: filtros iniciais ---
st.sidebar.header("Filtros iniciais")

# Segurança: checar se colunas existem
country_options = df["country"].dropna().unique().tolist() if "country" in df.columns else []
city_options = df["city"].dropna().unique().tolist() if "city" in df.columns else []
cuisine_options = df["cuisines"].dropna().unique().tolist() if "cuisines" in df.columns else []

paises = st.sidebar.multiselect(
    "Selecione os países:",
    options=country_options,
    default=country_options if country_options else None
)

selected_cuisines = st.sidebar.multiselect(
    "Tipos de culinária:",
    options=cuisine_options,
    default=None
)

# Aplica os filtros escolhidos
df_filtered = df.copy()
if paises:
    df_filtered = df_filtered[df_filtered["country"].isin(paises)]
if selected_cuisines:
    df_filtered = df_filtered[df_filtered["cuisines"].isin(selected_cuisines)]

# --- Cabeçalho e descrição ---
st.image("logo.png", width=160)
st.title("📊 Fome Zero - Inteligência para Restaurantes Globais")
st.markdown(
    "Este dashboard oferece uma visão estratégica do mercado de restaurantes. "
    "Use os filtros à esquerda para ajustar o universo de análise por país e tipo de culinária. "
    "Navegue pelas abas para ver análises por país, cidade e tipo de culinária."
)

st.markdown("---")

# --- Principais KPIs ---
col1, col2, col3 = st.columns(3)

with col1:
    n_countries = int(df_filtered["country"].nunique()) if "country" in df_filtered.columns else 0
    st.metric("🌍 Nº de Países", f"{n_countries}")

with col2:
    n_cities = int(df_filtered["city"].nunique()) if "city" in df_filtered.columns else 0
    st.metric("🏙️ Nº de Cidades", f"{n_cities}")

with col3:
    # média de rating com fallback
    if "rating" in df_filtered.columns and df_filtered["rating"].notna().sum() > 0:
        avg_rating = df_filtered["rating"].mean()
        st.metric("⭐ Avaliação Média", f"{avg_rating:.2f}")
    else:
        st.metric("⭐ Avaliação Média", "—")

st.markdown("---")

# --- Visual de alta atração: top cuisines + distribuição de rating ---
left, right = st.columns([1, 1])

with left:
    st.subheader("Top Culinárias")
    if "cuisines" in df_filtered.columns:
        top_cuis = top_n(df_filtered, "cuisines", "name" if "name" in df_filtered.columns else df_filtered.columns[0], n=10)
        fig = px.bar(top_cuis, x="cuisines", y="value", labels={"value": "# Restaurantes", "cuisines": "Culinária"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Coluna 'cuisines' não encontrada no dataset.")

with right:
    st.subheader("Distribuição de Avaliações (amostra)")
    if "rating" in df_filtered.columns and df_filtered["rating"].notna().sum() > 0:
        # amostra para desempenho
        sample = df_filtered.dropna(subset=["rating"])
        sample = sample.sample(min(len(sample), 2000))
        fig2 = px.histogram(sample, x="rating", nbins=20, title="Distribuição de avaliações")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados de avaliação disponíveis para plotar.")

st.markdown("---")

# --- Mapa (amostragem controlada) ---
st.subheader("📍 Distribuição geográfica (amostragem)")

if "latitude" in df_filtered.columns and "longitude" in df_filtered.columns:
    map_df = df_filtered.dropna(subset=["latitude", "longitude"])
    if len(map_df) == 0:
        st.info("Sem coordenadas válidas para exibir no mapa.")
    else:
        # limitar amostra para performance
        display_df = map_df.sample(500) if len(map_df) > 500 else map_df
        st.map(display_df[["latitude", "longitude"]])
        st.caption("Mapa amostrado para evitar lentidão. Use a aba 'Cidades' para análise geográfica mais detalhada.")
else:
    st.info("Colunas de coordenadas não encontradas (latitude/longitude).")

st.markdown("---")
st.caption("Dica: use os filtros no painel lateral para ajustar o universo de análise rapidamente.")
