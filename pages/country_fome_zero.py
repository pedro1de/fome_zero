# -------- Início seguro e diagnóstico (substituir início do arquivo) --------
import os
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px

st.set_page_config(page_title="Fome Zero - Visão País", layout="wide")
st.title("Visão País")
st.markdown("---")

# caminhos relativos (no repositório)
DATA_PATH = "dataset/zomato.csv"
LOGO_PATH = "logo.png"

# checa CSV
if not os.path.exists(DATA_PATH):
    st.error(f"Arquivo de dados não encontrado em '{DATA_PATH}'. Coloque 'zomato.csv' na pasta 'dataset/' do repositório.")
    st.stop()

# tenta ler CSV e garante que df_raw existe
try:
    df_raw = pd.read_csv(DATA_PATH)
except Exception as e:
    st.error(f"Falha ao ler o CSV em '{DATA_PATH}': {e}")
    st.stop()

# diagnóstico: mostra as 1ªs colunas (isso ajuda a ver se o CSV foi lido corretamente)
st.write("Colunas carregadas do CSV:", list(df_raw.columns))

# agora sim podemos limpar nomes de colunas com segurança
try:
    df_raw.rename(columns=lambda x: x.strip(), inplace=True)
except Exception as e:
    st.error(f"Erro ao renomear colunas: {e}")
    st.stop()

# tenta carregar logo (se existir)
if os.path.exists(LOGO_PATH):
    try:
        st.sidebar.image(LOGO_PATH, width=120)
    except Exception as e:
        st.sidebar.warning(f"Falha ao carregar logo: {e}")
else:
    st.sidebar.warning(f"Logo não encontrado em '{LOGO_PATH}'.")
# -------- Fim do bloco de inicialização seguro --------
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
