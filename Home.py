# ------------------------ Home.py (robusto para Streamlit Cloud) ------------------------
import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fome Zero - Home", layout="wide")

# Paths relativos (dentro do repositório)
DATA_PATH = "dataset/zomato.csv"
LOGO_PATH = "logo.png"

st.sidebar.title("FOME ZERO")

# Verifica logo
if os.path.exists(LOGO_PATH):
    try:
        st.sidebar.image(LOGO_PATH, width=120)
    except Exception as e:
        st.sidebar.warning(f"Falha ao carregar logo: {e}")
else:
    st.sidebar.warning(f"Logo não encontrado em '{LOGO_PATH}'. Coloque 'logo.png' na raiz do repositório.")

st.sidebar.markdown("---")
st.sidebar.markdown("Powered by Pedro Oliveira")
st.sidebar.markdown("---")

# Verifica dataset
if not os.path.exists(DATA_PATH):
    st.error(f"Arquivo de dados não encontrado: '{DATA_PATH}'. Coloque 'zomato.csv' dentro da pasta 'dataset/' do repositório.")
    st.stop()

# Carrega CSV com try/except
try:
    df = pd.read_csv(DATA_PATH)
except Exception as e:
    st.error(f"Erro ao ler '{DATA_PATH}': {e}")
    st.stop()

# Mostra colunas para diagnóstico (você pode comentar depois)
st.write("Colunas detectadas no CSV:", list(df.columns))

# Renomeia colunas para o padrão usado no resto do projeto (seguro: só renomeia se as colunas existirem)
rename_map = {
    'Country Code': 'Country Code',
    'Restaurant ID': 'Restaurant ID',
    'City': 'City',
    'Cuisines': 'Cuisines',
    'Latitude': 'Latitude',
    'Longitude': 'Longitude',
    'Average Cost for two': 'Average Cost for two',
    'Aggregate rating': 'Aggregate rating',
    'Price range': 'Price range'
}
# (aqui apenas um placeholder — não alteramos nomes, mas garantimos que as colunas existem)
# Tratar colunas essenciais
expected = ['Restaurant ID','Restaurant Name','Country Code','City','Longitude','Latitude','Cuisines','Average Cost for two','Aggregate rating']
missing = [c for c in expected if c not in df.columns]
if missing:
    st.warning(f"As colunas esperadas estão faltando: {missing}. O app pode não mostrar tudo corretamente.")

# Tratamentos seguros
# Garante que 'Cuisines' exista e pega só o primeiro tipo
if 'Cuisines' in df.columns:
    df['cuisines_first'] = df['Cuisines'].astype(str).apply(lambda x: x.split(",")[0].strip())
else:
    df['cuisines_first'] = "Unknown"

# Mapear country code para nome legível (se existir)
COUNTRY_MAP = {
    1: "India", 14: "Australia", 30: "Brazil", 37: "Canada", 94: "Indonesia",
    148: "New Zealand", 162: "Philippines", 166: "Qatar", 184: "Singapore",
    189: "South Africa", 191: "Sri Lanka", 208: "Turkey",
    214: "United Arab Emirates", 215: "England", 216: "United States of America",
}
if 'Country Code' in df.columns:
    df['country_name'] = df['Country Code'].apply(lambda x: COUNTRY_MAP.get(int(x), "Unknown") if pd.notnull(x) else "Unknown")
else:
    # tenta coluna 'Country' textual, se existir
    if 'Country' in df.columns:
        df['country_name'] = df['Country'].astype(str)
    else:
        df['country_name'] = "Unknown"

# Conversões numéricas seguras
for col in ['Average Cost for two','Aggregate rating','Latitude','Longitude','Votes']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Filtros na sidebar
countries = df['country_name'].unique().tolist()
selected_countries = st.sidebar.multiselect("Selecione um ou mais países", countries, default=countries)

cuisines = df['cuisines_first'].unique().tolist()
selected_cuisines = st.sidebar.multiselect("Selecione tipos de culinária", cuisines, default=cuisines)

# Filtra DataFrame
df_filtered = df[(df['country_name'].isin(selected_countries)) & (df['cuisines_first'].isin(selected_cuisines))]

# KPIs
st.title("Home - Fome Zero")
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
# Total de restaurantes
if 'Restaurant ID' in df_filtered.columns:
    col1.metric("Total Restaurantes", int(df_filtered['Restaurant ID'].nunique()))
else:
    col1.metric("Total Restaurantes", "N/A")
# Total cidades
col2.metric("Total Cidades", int(df_filtered['City'].nunique()) if 'City' in df_filtered.columns else "N/A")
# Total países
col3.metric("Total Países", int(df_filtered['country_name'].nunique()))
# Média de avaliação
col4.metric("Média de Avaliação", round(df_filtered['Aggregate rating'].mean(), 2) if 'Aggregate rating' in df_filtered.columns else "N/A")

st.markdown("---")

# Mapa (agregado por cidade + culinária)
st.subheader("Localização dos Restaurantes")
if {'Latitude','Longitude','City'}.issubset(df_filtered.columns):
    map_data = df_filtered.groupby(['City','cuisines_first','Latitude','Longitude']).size().reset_index(name='count')
    fig_map = px.scatter_mapbox(
        map_data,
        lat="Latitude",
        lon="Longitude",
        size="count",
        color="cuisines_first",
        hover_name="City",
        hover_data=["cuisines_first","count"],
        zoom=1,
        height=600
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Colunas 'Latitude' e 'Longitude' ou 'City' ausentes para desenhar o mapa.")

st.markdown("---")
# Top cidades
st.subheader("Top 20 Cidades com Mais Restaurantes")
if 'City' in df_filtered.columns and 'Restaurant ID' in df_filtered.columns:
    top_cities = df_filtered.groupby('City').agg(restaurants_count=('Restaurant ID','nunique')).reset_index().sort_values('restaurants_count', ascending=False).head(20)
    fig_cities = px.bar(top_cities, x='City', y='restaurants_count', color='restaurants_count', title="Top 20 Cidades")
    st.plotly_chart(fig_cities, use_container_width=True)
else:
    st.warning("Colunas necessárias para ranking de cidades ausentes.")
