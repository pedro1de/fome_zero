import streamlit as st
import plotly.express as px
from utils import load_data, top_n

st.set_page_config(page_title="Países - Fome Zero", layout="wide")

# Carrega dados
df = load_data()

st.title("🌐 Análise por País")
st.markdown("Selecione um país para ver a performance agregada: cidades, avaliações e preço mediano.")

# Se não houver coluna country, informar
if "country" not in df.columns or df["country"].dropna().empty:
    st.warning("Coluna 'country' não encontrada ou sem dados. Verifique o dataset.")
else:
    # selector de país
    country_list = sorted(df["country"].dropna().unique().tolist())
    country_selected = st.selectbox("Escolha o país", country_list, index=0)

    # filtrar para o país
    df_country = df[df["country"] == country_selected].copy()

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        n_rest = len(df_country)
        st.metric("🍽️ Restaurantes (total)", f"{n_rest:,}")
    with col2:
        n_cities = int(df_country["city"].nunique()) if "city" in df_country.columns else 0
        st.metric("🏙️ Cidades únicas", f"{n_cities}")
    with col3:
        avg_rating = df_country["rating"].mean() if "rating" in df_country.columns and df_country["rating"].notna().sum() > 0 else None
        st.metric("⭐ Avaliação média", f"{avg_rating:.2f}" if avg_rating else "—")

    st.markdown("---")

    # Top cidades por número de restaurantes
    st.subheader("Top cidades por número de restaurantes")
    if "city" in df_country.columns and df_country["city"].notna().sum() > 0:
        top_cities = top_n(df_country, "city", "name" if "name" in df_country.columns else df_country.columns[0], n=15, agg="count")
        fig1 = px.bar(top_cities, x="city", y="value", labels={"value": "# Restaurantes", "city": "Cidade"}, title=f"Top cidades em {country_selected}")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Sem dados de cidade para este país.")

    # Avaliação média por cidade (top)
    st.subheader("Avaliação média por cidade (top cidades)")
    if "rating" in df_country.columns and "city" in df_country.columns:
        # pegar top 12 cidades por número de restaurantes para comparar média de rating
        city_counts = df_country["city"].value_counts().head(12).index.tolist()
        subset = df_country[df_country["city"].isin(city_counts)]
        rating_by_city = subset.groupby("city")["rating"].mean().sort_values(ascending=False).reset_index()
        fig2 = px.bar(rating_by_city, x="city", y="rating", labels={"rating": "Avaliação média", "city": "Cidade"})
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Dados de avaliação ou cidade ausentes para este país.")

    # Preço mediano por cidade (se existir)
    if "price_num" in df_country.columns and df_country["price_num"].notna().sum() > 0:
        st.subheader("Preço mediano por cidade")
        price_city = df_country.groupby("city")["price_num"].median().dropna().sort_values(ascending=False).head(15).reset_index()
        fig3 = px.bar(price_city, x="city", y="price_num", labels={"price_num":"Preço mediano","city":"Cidade"})
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Coluna de preço não disponível ou sem dados relevantes para este país.")

    st.markdown("---")

    # Top restaurantes (tabela)
    st.subheader("Top restaurantes (por avaliação)")
    display_cols = []
    for c in ["name", "cuisines", "city", "rating", "price_num"]:
        if c in df_country.columns:
            display_cols.append(c)
    if display_cols:
        table = df_country.sort_values(by="rating", ascending=False).head(20)[display_cols].fillna("-")
        st.write(table)
    else:
        st.info("Não há colunas suficientes para exibir a tabela de top restaurantes.")
