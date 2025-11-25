# ------------------------ country_fome_zero.py (corrigido) ------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os

st.set_page_config(page_title="Fome Zero - Visão País", layout="wide")

st.title("Visão País")
st.markdown("---")

# ------------------------ paths (relativos no repositório) ------------------------
DATA_PATH = "dataset/zomato.csv"
LOGO_PATH = "logo.png"

# ------------------------ verificar arquivos ------------------------
if not os.path.exists(DATA_PATH):
    st.error(f"Arquivo de dados não encontrado em '{DATA_PATH}'. Verifique se o arquivo 'zomato.csv' está na pasta 'dataset/' do repositório.")
    st.stop()

if not os.path.exists(LOGO_PATH):
    st.sidebar.warning(f"Logo não encontrado em '{LOGO_PATH}'. Verifique se o arquivo 'logo.png' está na raiz do repositório.")
else:
    try:
        st.sidebar.image(LOGO_PATH, width=120)
    except Exception as e:
        st.sidebar.warning("Falha ao carregar logo: " + str(e))

st.sidebar.title("Fome Zero")
st.sidebar.markdown("Filtre a visão dos dados abaixo:")

# ------------------------ carregar dados ------------------------
try:
    df_raw = pd.read_csv(DATA_PATH)
except Exception as e:
    st.error(f"Erro ao ler o CSV: {e}")
    st.stop()

# ------------------------ limpar nomes de colunas (seguro) ------------------------
# Remove espaços extras das colunas e garante nomes consistentes
df_raw.rename(columns=lambda x: x.strip(), inplace=True)

# Mostrar aviso se colunas esperadas não existirem
expected_columns = [
    'Restaurant ID', 'Restaurant Name', 'Country Code', 'City', 'Address',
    'Locality', 'Locality Verbose', 'Longitude', 'Latitude', 'Cuisines',
    'Average Cost for two', 'Currency', 'Has Table booking',
    'Has Online delivery', 'Is delivering now', 'Switch to order menu',
    'Price range', 'Aggregate rating', 'Rating color', 'Rating text',
    'Votes'
]
missing = [c for c in expected_columns if c not in df_raw.columns]
if missing:
    st.warning(f"As seguintes colunas esperadas estão faltando no CSV: {missing}. O dashboard pode não funcionar corretamente.")

# ------------------------ criar coluna de país legível ------------------------
COUNTRIES = {
    1: "India", 14: "Australia", 30: "Brazil", 37: "Canada", 94: "Indonesia",
    148: "New Zealand", 162: "Philippines", 166: "Qatar", 184: "Singapore",
    189: "South Africa", 191: "Sri Lanka", 208: "Turkey",
    214: "United Arab Emirates", 215: "England", 216: "United States of America",
}
def map_country(code):
    try:
        return COUNTRIES.get(int(code), "Desconhecido")
    except Exception:
        return "Desconhecido"

if 'Country Code' in df_raw.columns:
    df_raw['country_name'] = df_raw['Country Code'].apply(map_country)
else:
    # se não houver Country Code mas houver Country já em texto
    if 'Country' in df_raw.columns:
        df_raw['country_name'] = df_raw['Country'].astype(str)
    else:
        st.warning("Não foi encontrada coluna 'Country Code' nem 'Country' no CSV. Usando 'Desconhecido' para país.")
        df_raw['country_name'] = "Desconhecido"

# ------------------------ transformar tipos relevantes ------------------------
# Converte colunas numéricas que vamos usar
for col in ['Average Cost for two', 'Aggregate rating', 'Latitude', 'Longitude', 'Votes']:
    if col in df_raw.columns:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')

# Tratar cuisines (pegar primeiro tipo)
if 'Cuisines' in df_raw.columns:
    df_raw['cuisines_first'] = df_raw['Cuisines'].astype(str).apply(lambda x: x.split(",")[0].strip())
else:
    df_raw['cuisines_first'] = "Unknown"

# ------------------------ sidebar: filtro múltiplo de países ------------------------
countries = df_raw['country_name'].unique().tolist()
selected_countries = st.sidebar.multiselect("Selecione os países", options=countries, default=countries)

st.sidebar.markdown("---")
st.sidebar.write("Powered By Pedro Oliveira")

# ------------------------ filtrar dados ------------------------
df = df_raw[df_raw['country_name'].isin(selected_countries)].copy()
if df.empty:
    st.warning("Filtro retornou 0 linhas. Ajuste os filtros na barra lateral.")
    st.stop()

# ------------------------ KPIs ------------------------
st.markdown("### Métricas Principais")
col1, col2, col3, col4 = st.columns(4)

# Total restaurantes (usar Restaurant ID ou Restaurant Name conforme disponível)
if 'Restaurant ID' in df.columns:
    total_restaurants = df['Restaurant ID'].nunique()
elif 'Restaurant Name' in df.columns:
    total_restaurants = df['Restaurant Name'].nunique()
else:
    total_restaurants = "N/A"

col1.metric("Total Restaurantes", total_restaurants)

col2.metric("Total Países (filtrados)", df['country_name'].nunique())

if 'City' in df.columns:
    col3.metric("Total Cidades (filtradas)", df['City'].nunique())
else:
    col3.metric("Total Cidades (filtradas)", "N/A")

if 'Aggregate rating' in df.columns:
    col4.metric("Média de Avaliação", round(df['Aggregate rating'].mean(skipna=True), 2))
else:
    col4.metric("Média de Avaliação", "N/A")

st.markdown("---")

# ------------------------ gráfico restaurantes por país ------------------------
st.subheader("Número de Restaurantes por País")
if 'country_name' in df.columns:
    if 'Restaurant ID' in df.columns:
        country_count = df.groupby('country_name')['Restaurant ID'].nunique().reset_index().sort_values('Restaurant ID', ascending=False)
        fig_country = px.bar(country_count, x='country_name', y='Restaurant ID', labels={'Restaurant ID':'Qtd Restaurantes','country_name':'País'}, text='Restaurant ID')
        st.plotly_chart(fig_country, use_container_width=True)
    else:
        st.warning("Coluna 'Restaurant ID' não encontrada para montar o gráfico por país.")
else:
    st.warning("Coluna 'country_name' não encontrada.")

st.markdown("---")

# ------------------------ top cidades (barras) ------------------------
st.subheader("Top Cidades por Número de Restaurantes")
if 'City' in df.columns:
    if 'Restaurant ID' in df.columns:
        cities_count = df.groupby('City')['Restaurant ID'].nunique().reset_index().sort_values('Restaurant ID', ascending=False).head(20)
        fig_cities = px.bar(cities_count, x='City', y='Restaurant ID', labels={'Restaurant ID':'# Restaurantes','City':'Cidade'}, text='Restaurant ID')
        st.plotly_chart(fig_cities, use_container_width=True)
    else:
        st.warning("Coluna 'Restaurant ID' não encontrada para ranking de cidades.")
else:
    st.warning("Coluna 'City' não encontrada para ranking de cidades.")

st.markdown("---")

# ------------------------ mapa top cidades ------------------------
st.subheader("Localização das Cidades (Top)")
if {'Latitude', 'Longitude', 'City'}.issubset(df.columns):
    top_cities_map = df.groupby(['City','country_name','Latitude','Longitude'])['Restaurant ID'].nunique().reset_index()
    top_cities_map = top_cities_map.sort_values('Restaurant ID', ascending=False).head(50)
    fig_map = px.scatter_mapbox(
        top_cities_map,
        lat='Latitude',
        lon='Longitude',
        size='Restaurant ID',
        color='country_name',
        hover_name='City',
        hover_data={'Restaurant ID':True},
        zoom=1,
        height=600
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Colunas 'Latitude' e 'Longitude' são necessárias para o mapa (verifique o CSV).")

st.markdown("---")
# --------------------------------------------------------------------------------
