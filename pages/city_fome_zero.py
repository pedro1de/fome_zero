import streamlit as st
import plotly.express as px
from utils import load_data, top_n

st.set_page_config(page_title="Cidades - Fome Zero", layout="wide")

# Sidebar com logo e filtros (funil)
with st.sidebar:
    st.image("logo.png", width=160)
    st.markdown("---")
    st.title("🏙️ Cidades")

# Carrega dados
df = load_data()

# Validação básica
if "country" not in df.columns or df["country"].dropna().empty:
    st.error("Coluna 'country' ausente ou sem dados. Verifique o dataset.")
    st.stop()

# Country selector (single)
country_list = sorted(df["country"].dropna().unique().tolist())
country_selected = st.sidebar.selectbox("Selecione o país", country_list, index=0)

# City selector dependente do país
cities_for_country = df[df["country"] == country_selected]["city"].dropna().unique().tolist()
cities_for_country = sorted(cities_for_country)
# Se não houver cidades listadas, deixar vazio e mostrar aviso depois
city_selected = st.sidebar.multiselect(
    "Selecione a(s) cidade(s)",
    options=cities_for_country,
    default=cities_for_country if len(cities_for_country) <= 10 else cities_for_country[:10]
)

# Aplica filtros: país sempre aplicado, cidade apenas se selecionada
df_country = df[df["country"] == country_selected].copy()
df_filtered = df_country.copy()
if city_selected:
    df_filtered = df_country[df_country["city"].isin(city_selected)]

# Cabeçalho
st.title(f"🏙️ Visão por Cidade — {country_selected}")
st.markdown("Análise detalhada das cidades do país selecionado. Use o filtro de cidade para afinar o universo.")

# KPIs por seleção (macro por país / micro por cidades selecionadas)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🍽️ Restaurantes (no universo filtrado)", f"{len(df_filtered):,}")
with col2:
    if df_filtered["rating"].notna().sum() > 0:
        st.metric("⭐ Avaliação média (filtrada)", f"{df_filtered['rating'].mean():.2f}")
    else:
        st.metric("⭐ Avaliação média (filtrada)", "—")
with col3:
    if "price_num" in df_filtered.columns and df_filtered["price_num"].notna().sum() > 0:
        st.metric("💰 Ticket mediano (filtrado)", f"{df_filtered['price_num'].median():.2f}")
    else:
        st.metric("💰 Ticket mediano (filtrado)", "—")

st.markdown("---")

# Top cidades por número de restaurantes (considerando país)
st.subheader("Top cidades por número de restaurantes (país)")
top_cities = top_n(df_country, "city", "name" if "name" in df_country.columns else df_country.columns[0], n=15, agg="count")
if not top_cities.empty:
    fig1 = px.bar(top_cities, x="city", y="value", labels={"value": "# Restaurantes", "city": "Cidade"}, title="Top cidades do país")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("Sem dados de cidade para este país.")

st.markdown("---")

# Distribuição de rating por cidade (apenas cidades selecionadas ou top cidades)
st.subheader("Distribuição de avaliações por cidade")
if df_filtered["rating"].notna().sum() > 0 and "city" in df_filtered.columns:
    # escolher cidades a plotar: se selecionadas, usar elas; senão top 8 por volume
    if city_selected:
        cities_plot = city_selected
    else:
        cities_plot = top_cities["city"].tolist()[:8] if not top_cities.empty else df_country["city"].dropna().unique().tolist()[:8]

    subset = df_filtered[df_filtered["city"].isin(cities_plot)]
    if not subset.empty:
        fig2 = px.box(subset, x="city", y="rating", points="outliers", labels={"rating":"Avaliação","city":"Cidade"}, title="Boxplot de avaliações por cidade")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem dados suficientes para plotar avaliações por cidade.")
else:
    st.info("Avaliações não disponíveis para plotar.")

st.markdown("---")

# Mapa focado nas cidades filtradas (apenas se existir coordenadas)
st.subheader("📍 Mapa das cidades selecionadas (amostragem)")
if "latitude" in df_filtered.columns and "longitude" in df_filtered.columns and df_filtered[["latitude","longitude"]].notna().sum().sum() > 0:
    map_df = df_filtered.dropna(subset=["latitude","longitude"])
    display_df = map_df.sample(500) if len(map_df) > 500 else map_df
    st.map(display_df[["latitude", "longitude"]])
    st.caption("Mapa amostrado — zoom para explorar concentrações locais.")
else:
    st.info("Sem coordenadas válidas para exibição no mapa desta aba.")

st.markdown("---")

# Tabela: top restaurantes por avaliação dentro do universo filtrado
st.subheader("Top restaurantes (por avaliação) — universo filtrado")
display_cols = [c for c in ["name", "city", "cuisines", "rating", "price_num"] if c in df_filtered.columns]
if display_cols:
    table = df_filtered.sort_values(by="rating", ascending=False).head(50)[display_cols].fillna("-")
    st.dataframe(table)
else:
    st.info("Não há colunas suficientes para exibir tabela de top restaurantes.")
