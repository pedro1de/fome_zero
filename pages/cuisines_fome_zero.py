import streamlit as st
import plotly.express as px
from utils import load_data, top_n

st.set_page_config(page_title="Culinárias - Fome Zero", layout="wide")

# Sidebar com logo e filtros (funil país -> cidade -> culinária)
with st.sidebar:
    st.image("logo.png", width=160)
    st.markdown("---")
    st.title("🍽️ Culinárias")

# Carrega dados
df = load_data()

# Validação
if "country" not in df.columns or df["country"].dropna().empty:
    st.error("Coluna 'country' ausente ou sem dados. Verifique o dataset.")
    st.stop()

# País selector (inclui Todos)
country_list = sorted(df["country"].dropna().unique().tolist())
country_options = ["Todos"] + country_list
country_selected = st.sidebar.selectbox("Selecione o país", country_options, index=0)

# Cidades disponíveis para o país (dependente do país selecionado)
if country_selected == "Todos":
    cities_for_country = df["city"].dropna().unique().tolist()
else:
    cities_for_country = df[df["country"] == country_selected]["city"].dropna().unique().tolist()
cities_for_country = sorted(cities_for_country)
city_options = ["Todos"] + cities_for_country
city_selected = st.sidebar.selectbox("Selecione a cidade (opcional)", city_options)

# Filtrar por país e cidade
if country_selected == "Todos":
    df_country = df.copy()
else:
    df_country = df[df["country"] == country_selected].copy()

if city_selected != "Todos":
    df_country_city = df_country[df_country["city"] == city_selected]
else:
    df_country_city = df_country

# Cuisines disponíveis com base no país/cidade selecionados
cuisines_available = sorted(df_country_city["cuisines"].dropna().unique().tolist())
cuisine_selected = st.sidebar.multiselect("Selecione culinária(s)", options=cuisines_available, default=None)

# Filtrar principal
df_filtered = df_country_city.copy()
if cuisine_selected:
    df_filtered = df_filtered[df_filtered["cuisines"].isin(cuisine_selected)]

# Cabeçalho
title_country = "Todos os países" if country_selected == "Todos" else country_selected
title_city = "" if city_selected == "Todos" else f" / {city_selected}"
st.title(f"🍽️ Análise de Culinárias — {title_country}{title_city}")
st.markdown("Explore a performance de tipos de culinária no contexto selecionado.")

# KPIs rápidos
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🍽️ Tipos de culinária disponíveis", f"{len(cuisines_available)}")
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

# --- Top culinárias por número de restaurantes (sempre útil) ---
st.subheader("Top Culinárias (por número de restaurantes)")
if cuisines_available:
    vc = (
        df_country_city["cuisines"]
        .value_counts()
        .reset_index(name="count")
        .rename(columns={"index": "cuisines"})
    )
    vc_top = vc.head(20)

    fig = px.bar(
        vc_top,
        x="count",
        y="cuisines",
        orientation="h",
        labels={"count":"# Restaurantes","cuisines":"Culinária"},
        title="Top culinárias no contexto"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhuma culinária disponível no contexto selecionado.")


st.markdown("---")

# --- Boxplot de rating por culinária (mostra variação) ---
st.subheader("Distribuição de avaliações por culinária (Top N)")
# slider para controlar top N
top_n_cuis = st.slider("Mostrar top N culinárias por volume", min_value=5, max_value=30, value=12)
top_cuis_list = vc.head(top_n_cuis)["cuisines"].tolist() if 'vc' in locals() and not vc.empty else []

if top_cuis_list:
    subset = df_country_city[df_country_city["cuisines"].isin(top_cuis_list) & df_country_city["rating"].notna()]
    if not subset.empty:
        fig_box = px.box(subset, x="cuisines", y="rating", points="outliers", labels={"rating":"Avaliação","cuisines":"Culinária"}, title="Boxplot de avaliação por culinária (Top selecionado)")
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("Sem avaliações suficientes para gerar o boxplot.")
else:
    st.info("Sem culinárias suficientes para mostrar o boxplot.")

st.markdown("---")

# --- Agregado: número vs avaliação média (muito robusto) ---
st.subheader("Popularidade vs Avaliação média por culinária")
agg = (
    df_country_city
    .groupby("cuisines")
    .agg(count=("name","count"), rating_mean=("rating","mean"))
    .reset_index()
    .dropna(subset=["rating_mean"])
)
# slider minimo de restaurantes para considerar
min_count = st.slider("Mínimo de restaurantes por culinária", min_value=1, max_value=20, value=3)
agg_filtered = agg[agg["count"] >= min_count]
if not agg_filtered.empty:
    fig_sc = px.scatter(agg_filtered, x="count", y="rating_mean", size="count", hover_name="cuisines",
                        labels={"count":"# Restaurantes","rating_mean":"Avaliação média"},
                        title="# Restaurantes vs Avaliação média (por culinária)")
    st.plotly_chart(fig_sc, use_container_width=True)
else:
    st.info("Ajuste o filtro de mínimo de restaurantes para ver o gráfico.")

st.markdown("---")

# Tabela: top restaurantes por culinária (filtrada)
st.subheader("Top restaurantes no contexto selecionado")
display_cols = [c for c in ["name", "city", "cuisines", "rating", "price_num"] if c in df_filtered.columns]
if display_cols:
    table = df_filtered.sort_values(by="rating", ascending=False).head(50)[display_cols].fillna("-")
    st.dataframe(table)
else:
    st.info("Sem colunas suficientes para exibir a tabela.")
