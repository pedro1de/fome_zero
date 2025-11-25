# ------------------------ pages/country_fome_zero.py (robusto) ------------------------
import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fome Zero - Visão País", layout="wide")
st.title("Visão País")
st.markdown("---")

DATA_PATH = "dataset/zomato.csv"
LOGO_PATH = "logo.png"

# Verifica se o CSV existe
if not os.path.exists(DATA_PATH):
    st.error(f"Arquivo de dados não encontrado: '{DATA_PATH}'. Coloque 'zomato.csv' na pasta 'dataset/'.")
    st.stop()

# Carrega CSV com segurança
try:
    df_raw = pd.read_csv(DATA_PATH)
except Exception as e:
    st.error(f"Erro ao ler o CSV: {e}")
    st.stop()

# Mostrar colunas (diagnóstico)
st.write("Colunas carregadas:", list(df_raw.columns))

# Limpeza de nomes de colunas (agora que df_raw existe)
df_raw.rename(columns=lambda x: x.strip(), inplace=True)

# Load logo (relativo)
if os.path.exists(LOGO_PATH):
    try:
        st.sidebar.image(LOGO_PATH, width=120)
    except Exception as e:
        st.sidebar.warning(f"Falha ao carregar logo: {e}")
else:
    st.sidebar.warning(f"Logo não encontrado em '{LOGO_PATH}'.")

st.sidebar.title("Fome Zero")
st.sidebar.markdown("Filtre a visão dos dados abaixo:")

# Mapear Country Code -> nome
COUNTRY_MAP = {
    1: "India", 14: "Australia", 30: "Brazil", 37: "Canada", 94: "Indonesia",
    148: "New Zealand", 162: "Philippines", 166: "Qatar", 184: "Singapore",
    189: "South Africa", 191: "Sri Lanka", 208: "Turkey",
    214: "United Arab Emirates", 215: "England", 216: "United States of America",
}

if 'Country Code' in df_raw.columns:
    df_raw['country_name'] = df_raw['Country Code'].apply(lambda x: COUNTRY_MAP.get(int(x), "Unknown") if pd.notnull(x) else "Unknown")
else:
    # fallback se houver coluna textual
    if 'Country' in df_raw.columns:
        df_raw['country_name'] = df_raw['Country'].astype(str)
    else:
        df_raw['country_name'] = "Unknown"

# Conversões seguras
for col in ['Average Cost for two','Aggregate rating','Latitude','Longitude']:
    if col in df_raw.columns:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')

# Tratar cuisines
if 'Cuisines' in df_raw.columns:
    df_raw['cuisines_first'] = df_raw['Cuisines'].astype(str).apply(lambda x: x.split(",")[0].strip())
else:
    df_raw['cuisines_first'] = "Unknown"

# Sidebar multi-select countries
countries = df_raw['country_name'].unique().tolist()
selected_countries = st.sidebar.multiselect("Selecione os países", countries, default=countries)

st.sidebar.markdown("---")
st.sidebar.write("Powered By Pedro Oliveira")

# Filtrar
df = df_raw[df_raw['country_name'].isin(selected_countries)].copy()
if df.empty:
    st.warning("Nenhum dado após aplicar filtro. Ajuste os filtros.")
    st.stop()

# KPIs
st.markdown("### Métricas Principais")
col1, col2, col3, col4 = st.columns(4)
# total restaurantes
if 'Restaurant ID' in df.columns:
    col1.metric("Total Restaurantes", int(df['Restaurant ID'].nunique()))
else:
    col1.metric("Total Restaurantes", "N/A")
col2.metric("Total Países (filtrados)", int(df['country_name'].nunique()))
col3.metric("Total Cidades", int(df['City'].nunique()) if 'City' in df.columns else "N/A")
col4.metric("Média de Avaliação", round(df['Aggregate rating'].mean(),2) if 'Aggregate rating' in df.columns else "N/A")

st.markdown("---")

# Restaurantes por país (barras)
if 'Restaurant ID' in df.columns:
    country_count = df.groupby('country_name')['Restaurant ID'].nunique().reset_index().sort_values('Restaurant ID', ascending=False)
    fig_country = px.bar(country_count, x='country_name', y='Restaurant ID', text='Restaurant ID', labels={'Restaurant ID':'# Restaurantes','country_name':'País'})
    st.plotly_chart(fig_country, use_container_width=True)
else:
    st.warning("Coluna 'Restaurant ID' ausente para gráfico por país.")

st.markdown("---")

# Top cidades e mapa
if {'City','Latitude','Longitude','Restaurant ID'}.issubset(df.columns):
    cities_count = df.groupby('City')['Restaurant ID'].nunique().reset_index().sort_values('Restaurant ID', ascending=False).head(20)
    fig_cities = px.bar(cities_count, x='City', y='Restaurant ID', text='Restaurant ID', labels={'Restaurant ID':'# Restaurantes','City':'Cidade'})
    st.plotly_chart(fig_cities, use_container_width=True)

    # mapa
    top_cities_map = df.groupby(['City','country_name','Latitude','Longitude'])['Restaurant ID'].nunique().reset_index()
    top_cities_map = top_cities_map.sort_values('Restaurant ID', ascending=False).head(50)
    fig_map = px.scatter_mapbox(top_cities_map, lat='Latitude', lon='Longitude', size='Restaurant ID', color='country_name', hover_name='City', zoom=1, height=600)
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Colunas City/Latitude/Longitude/Restaurant ID necessárias para ranking e mapa.")
