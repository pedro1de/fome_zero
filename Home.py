# ------------------------ HOME.PY ------------------------
import pandas as pd
import streamlit as st
import plotly.express as px

# ------------------------ CONFIGURAÇÃO DA PÁGINA ------------------------
st.set_page_config(page_title="Fome Zero - Home", layout="wide")

# ------------------------ CARREGANDO DADOS ------------------------
df = pd.read_csv(r"D:\Downloads\Downloads\CURSO\7 Python\Arquivo\Project\dataset\zomato.csv")

# ------------------------ PADRÃO DE COLUNAS ------------------------
df.rename(columns={
    'Country Code':'country',
    'Restaurant ID':'restaurant_id',
    'City':'city',
    'Cuisines':'cuisines',
    'Latitude':'latitude',
    'Longitude':'longitude',
    'Average Cost for two':'average_cost_for_two',
    'Aggregate rating':'aggregate_rating',
    'Price range':'price_range'
}, inplace=True)

# ------------------------ TRATAMENTO ------------------------
df['cuisines'] = df['cuisines'].astype(str).apply(lambda x: x.split(",")[0])

COUNTRIES = {
    1: "India", 14: "Australia", 30: "Brazil", 37: "Canada", 94: "Indonesia",
    148: "New Zeland", 162: "Philippines", 166: "Qatar", 184: "Singapure",
    189: "South Africa", 191: "Sri Lanka", 208: "Turkey",
    214: "United Arab Emirates", 215: "England", 216: "United States of America",
}

df['country_name'] = df['country'].apply(lambda x: COUNTRIES.get(x, "Unknown"))

# ------------------------ BARRA LATERAL ------------------------
st.sidebar.image(r"D:\Downloads\Downloads\CURSO\7 Python\Arquivo\Project\logo.png", width=120)
st.sidebar.title("Fome Zero")
st.sidebar.markdown("## Filtros")
countries = st.sidebar.multiselect("Selecione os Países", options=df['country_name'].unique(), default=df['country_name'].unique())
cuisines = st.sidebar.multiselect("Selecione os Tipos de Culinária", options=df['cuisines'].unique(), default=df['cuisines'].unique())
st.sidebar.markdown("---")
st.sidebar.write("Powered By Pedro Oliveira")

# ------------------------ FILTRAGEM ------------------------
df_filtered = df[(df['country_name'].isin(countries)) & (df['cuisines'].isin(cuisines))]

# ------------------------ CARDS PRINCIPAIS ------------------------
st.markdown("# Home - Fome Zero")
st.markdown("""---""")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Restaurantes", df_filtered['restaurant_id'].nunique())
col2.metric("Total Cidades", df_filtered['city'].nunique())
col3.metric("Total Países", df_filtered['country_name'].nunique())
col4.metric("Média de Avaliação", round(df_filtered['aggregate_rating'].mean(),2))

# ------------------------ MAPA DE RESTAURANTES ------------------------
st.markdown("""---""")
st.subheader("Localização dos Restaurantes")
if not df_filtered.empty and {'latitude','longitude','cuisines','city'}.issubset(df_filtered.columns):
    # Criar dataframe agregado por cidade + culinária
    map_data = df_filtered.groupby(['city','cuisines','latitude','longitude']).size().reset_index(name='count')
    fig_map = px.scatter_mapbox(
        map_data,
        lat="latitude",
        lon="longitude",
        size="count",
        color="cuisines",
        hover_name="city",
        hover_data=["cuisines","count"],
        zoom=1,
        height=600
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Colunas de latitude/longitude/restaurante não encontradas para mapa.")

# ------------------------ TOP CITIES ------------------------
st.markdown("""---""")
st.subheader("Top Cidades por Número de Restaurantes")
if not df_filtered.empty:
    top_cities = df_filtered.groupby("city").size().reset_index(name='restaurants_count').sort_values(by='restaurants_count', ascending=False).head(20)
    fig_cities = px.bar(
        top_cities,
        x='city',
        y='restaurants_count',
        color='restaurants_count',
        title="Top 20 Cidades com Mais Restaurantes"
    )
    st.plotly_chart(fig_cities, use_container_width=True)
else:
    st.warning("Colunas necessárias para gráfico por cidade não encontradas.")
