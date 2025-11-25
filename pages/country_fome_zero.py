# -----------------------------------------
# COUNTRY FOME ZERO
# -----------------------------------------
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image

# -----------------------------------------
# Função para mapear nomes de países
# -----------------------------------------
COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zealand",
    162: "Philippines",
    166: "Qatar",
    184: "Singapore",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}

def country_name(country_id):
    return COUNTRIES.get(country_id, "Desconhecido")

# -----------------------------------------
# CARREGAR DADOS
# -----------------------------------------
df = pd.read_csv("dataset/zomato.csv")


# Remover espaços extras dos nomes das colunas
df_raw.rename(columns=lambda x: x.strip(), inplace=True)

# Criar coluna de país
df_raw['country_name'] = df_raw['Country Code'].apply(country_name)

# Conversão de tipos
df_raw['Average Cost for two'] = pd.to_numeric(df_raw['Average Cost for two'], errors='coerce')
df_raw['Aggregate rating'] = pd.to_numeric(df_raw['Aggregate rating'], errors='coerce')
df_raw['Latitude'] = pd.to_numeric(df_raw['Latitude'], errors='coerce')
df_raw['Longitude'] = pd.to_numeric(df_raw['Longitude'], errors='coerce')

# -----------------------------------------
# CONFIGURAÇÕES STREAMLIT
# -----------------------------------------
st.set_page_config(page_title="Fome Zero - Países", layout="wide")

# Sidebar
st.sidebar.image("logo.png", width=120)
st.sidebar.title("Fome Zero")
selected_countries = st.sidebar.multiselect(
    "Selecione os países", df_raw['country_name'].unique(), default=df_raw['country_name'].unique()
)
st.sidebar.markdown("---")
st.sidebar.markdown("Powered By Pedro Oliveira")

# Filtrar países
df_filtered = df_raw[df_raw['country_name'].isin(selected_countries)]

# -----------------------------------------
# KPIs
# -----------------------------------------
st.title("Visão País")
col1, col2, col3 = st.columns(3)
col1.metric("Total Restaurantes", df_filtered['Restaurant ID'].nunique())
col2.metric("Total Cidades", df_filtered['City'].nunique())
col3.metric("Média de Avaliação", round(df_filtered['Aggregate rating'].mean(), 2))

st.markdown("""---""")

# -----------------------------------------
# GRÁFICO DE RESTAURANTES POR PAÍS
# -----------------------------------------
restaurants_count = df_filtered.groupby('country_name')['Restaurant ID'].nunique().reset_index()
fig_restaurants = px.bar(
    restaurants_count,
    x='country_name',
    y='Restaurant ID',
    text='Restaurant ID',
    labels={'Restaurant ID': 'Qtd Restaurantes', 'country_name': 'País'},
    title="Número de Restaurantes por País"
)
st.plotly_chart(fig_restaurants, use_container_width=True)

st.markdown("""---""")

# -----------------------------------------
# TOP CIDADES POR RESTAURANTES
# -----------------------------------------
top_cities = df_filtered.groupby(['City', 'country_name', 'Latitude', 'Longitude'])['Restaurant ID'].nunique().reset_index()
top_cities = top_cities.sort_values('Restaurant ID', ascending=False).head(50)

fig_map = px.scatter_mapbox(
    top_cities,
    lat='Latitude',
    lon='Longitude',
    size='Restaurant ID',
    color='country_name',
    hover_name='City',
    hover_data={'Latitude': False, 'Longitude': False, 'Restaurant ID': True},
    zoom=1,
    height=600
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)
