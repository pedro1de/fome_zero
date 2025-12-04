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

# País selector
country_list = sorted(df["country"].dropna().unique().tolist())
country_selected = st.sidebar.selectbox("Selecione o país", country_list, index=0)

# Cidades disponíveis para o país (dependente)
cities_for_country = df[df["country"] == country_selected]["city"].dropna().unique().tolist()
cities_for_country = sorted(cities_for_country)
city_selected = st.sidebar.selectbox("Selecione a cidade (opcional)", ["Todos"] + cities_for_country)

# Cuisines disponíveis com base no país/cidade selecionados
df_country = df[df["country"] == country_selected].copy()
if city_selected != "Todos":
    df_country_city = df_country[df_country["city"] == city_selected]
else:
    df_country_city = df_country

cuisines_available = sorted(df_country_city["cuisines"].dropna().unique().tolist())
cuisine_selected = st.sidebar.multiselect("Selecione culinária(s)", options=cuisines_available, default=None)

# Filtrar principal
df_filtered = df_country_city.copy()
if cuisine_selected:
    df_filtered = df_filtered[df_filtered["cuisines"].isin(cuisine_selected)]

# Cabeçalho
st.title(f"🍽️ Análise de Culinárias — {country_selected}" + (f" / {city_selected}" if city_selected != "Todos" else ""))
st.markdown("Explore a performance de tipos de culinária no contexto selecionado.")

# KPIs rápidos
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🍽️ Tipos de culinária disponíveis", f"{len(cuisines_available)}")
with col2:
    # média rating do universo atual
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

# Top culinárias por número de restaurantes (no contexto)
st.subheader("Top Culinárias (por número de restaurantes)")
if cuisines_available:
    top_cuis = top_n(df_country_city, "cuisines", "name" if "name" in df_country_city.columns else df_country_city.columns[0], n=20)
    fig = px.bar(top_cuis, x="cuisines", y="value", labels={"value":"# Restaurantes","cuisines":"Culinária"}, title="Top culinárias no contexto")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhuma culinária disponível no contexto selecionado.")

st.markdown("---")

# Relação preço x avaliação por culinária (scatter aggregated)
st.subheader("Preço mediano vs Avaliação média por culinária")
if "price_num" in df_country_city.columns and df_country_city["price_num"].notna().sum() > 0 and "rating" in df_country_city.columns and df_country_city["rating"].notna().sum() > 0:
    agg = (
        df_country_city
        .groupby("cuisines")
        .agg(price_med=("price_num", "median"), rating_mean=("rating", "mean"), count=("name", "count"))
        .reset_index()
    )
    agg = agg[agg["count"] >= 3]  # filtrar poucas amostras
    if not agg.empty:
        fig2 = px.scatter(agg, x="price_med", y="rating_mean", size="count", hover_name="cuisines",
                          labels={"price_med":"Preço mediano","rating_mean":"Avaliação média"}, title="Preço vs Avaliação por culinária")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Amostra insuficiente para criar scatter de preço vs avaliação.")
else:
    st.info("Dados de preço ou avaliação insuficientes para este gráfico.")

st.markdown("---")

# Tabela: top restaurantes por culinária (filtrada)
st.subheader("Top restaurantes no contexto selecionado")
display_cols = [c for c in ["name", "city", "cuisines", "rating", "price_num"] if c in df_filtered.columns]
if display_cols:
    table = df_filtered.sort_values(by="rating", ascending=False).head(50)[display_cols].fillna("-")
    st.dataframe(table)
else:
    st.info("Sem colunas suficientes para exibir a tabela.")
