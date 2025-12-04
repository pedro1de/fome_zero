import streamlit as st
import plotly.express as px
from utils import load_data

st.set_page_config(page_title="Países - Fome Zero", layout="wide")

# Sidebar com logo e filtro
with st.sidebar:
    st.image("logo.png", width=160)
    st.markdown("---")
    st.title("🌍 Países")

# Carrega dados
df = load_data()

st.title("📊 Visão por País")
st.markdown("Esta página apresenta uma análise consolidada por país, sem detalhamento de cidades.")

# Validar dataset
if "country" not in df.columns:
    st.error("Coluna 'country' não encontrada no dataset.")
    st.stop()

# Sidebar - filtro com opção "Todos"
with st.sidebar:
    countries = sorted(df["country"].dropna().unique().tolist())
    countries_with_all = ["Todos"] + countries
    country_selected = st.selectbox("Selecione o país", countries_with_all)

# Filtrar
if country_selected == "Todos":
    df_country = df.copy()
else:
    df_country = df[df["country"] == country_selected]

st.markdown(f"### 🌐 País selecionado: **{country_selected}**")
st.markdown("---")

# KPIs revisados
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🍽️ Restaurantes cadastrados", f"{len(df_country):,}")

with col2:
    avg_rating = df_country["rating"].mean() if "rating" in df_country.columns and df_country["rating"].notna().sum() > 0 else None
    st.metric("⭐ Avaliação média", f"{avg_rating:.2f}" if avg_rating else "—")

with col3:
    if "price_num" in df_country.columns and df_country["price_num"].notna().sum() > 0:
        avg_price = df_country["price_num"].median()
        st.metric("💰 Ticket mediano", f"R$ {avg_price:,.2f}")
    else:
        st.metric("💰 Ticket mediano", "—")

st.markdown("---")

# Distribuição de rating
st.subheader("Distribuição de Avaliação (Rating)")
if "rating" in df_country.columns and df_country["rating"].notna().sum() > 0:
    fig = px.histogram(
        df_country,
        x="rating",
        nbins=20,
        title="Distribuição de notas dos restaurantes",
        labels={"rating": "Avaliação"}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Dados de avaliação não disponíveis para este contexto.")

st.markdown("---")

# Top restaurantes (APENAS PAÍS ou Todos)
st.subheader("🏆 Top restaurantes (melhores avaliações)")

cols_display = [c for c in ["name", "cuisines", "rating", "price_num"] if c in df_country.columns]

top_table = (
    df_country
    .sort_values(by="rating", ascending=False)
    .head(10)[cols_display]
    .reset_index(drop=True)
)

st.dataframe(top_table)
