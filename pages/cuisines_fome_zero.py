# ------------------------ CUISINES.PY ------------------------
import streamlit as st
import pandas as pd
import inflection
import plotly.express as px

# ------------------------ CONFIGURAÇÃO DA PÁGINA ------------------------
st.title("Visão Cozinha")

st.set_page_config(page_title="Fome Zero - Cuisines", layout="wide")
st.sidebar.image(r"D:\Downloads\Downloads\CURSO\7 Python\Arquivo\Project\logo.png", width=120)
st.sidebar.title("FOME ZERO")
st.sidebar.markdown("### Filtros")

# ------------------------ CARREGAMENTO DE DADOS ------------------------
df = pd.read_csv(r"D:\Downloads\Downloads\CURSO\7 Python\Arquivo\Project\dataset\zomato.csv")

# ------------------------ LIMPEZA E RENOMEAÇÃO ------------------------
def rename_columns(dataframe):
    df_copy = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df_copy.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df_copy.columns = cols_new
    return df_copy

df = rename_columns(df)

# ------------------------ TRATAMENTO DE PAÍSES E PREÇO ------------------------
COUNTRIES = {
    1: "India", 14: "Australia", 30: "Brazil", 37: "Canada",
    94: "Indonesia", 148: "New Zeland", 162: "Philippines", 166: "Qatar",
    184: "Singapure", 189: "South Africa", 191: "Sri Lanka", 208: "Turkey",
    214: "United Arab Emirates", 215: "England", 216: "United States of America"
}
df['country'] = df['country_code'].apply(lambda x: COUNTRIES[x])

def create_price_type(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

df['price_type'] = df['price_range'].apply(create_price_type)

# ------------------------ TRATAMENTO DE CULINÁRIAS ------------------------
# Mantemos apenas o primeiro tipo de culinária
# Linha 54 - corrigida
df['cuisines'] = df['cuisines'].apply(lambda x: str(x).split(",")[0] if pd.notnull(x) else "Unknown")


# ------------------------ FILTROS ------------------------
selected_countries = st.sidebar.multiselect(
    "Selecione um ou mais países",
    options=df['country'].unique(),
    default=df['country'].unique()
)

selected_cuisines = st.sidebar.multiselect(
    "Selecione tipos de culinária",
    options=df['cuisines'].unique(),
    default=df['cuisines'].unique()
)

df_filtered = df[(df['country'].isin(selected_countries)) & (df['cuisines'].isin(selected_cuisines))]

st.sidebar.markdown("""---""")
st.sidebar.markdown("Powered by Pedro Oliveira")

# ------------------------ CONTAINER 1: NÚMERO DE RESTAURANTES POR CULINÁRIA ------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Restaurantes por Tipo de Culinária")
    cuisine_count = df_filtered.groupby(['country','cuisines'])['restaurant_id'].nunique().reset_index()
    cuisine_count = cuisine_count.sort_values('restaurant_id', ascending=False)
    fig_cuisine_count = px.bar(
        cuisine_count,
        x='cuisines',
        y='restaurant_id',
        color='country',
        labels={"cuisines":"Tipo de Culinária", "restaurant_id":"Número de Restaurantes"},
        title="Número de Restaurantes por Tipo de Culinária"
    )
    st.plotly_chart(fig_cuisine_count, use_container_width=True)

# ---------- CONTAINER 2: NOTA MÉDIA E PREÇO ----------
with col2:
    st.markdown("### Nota Média por Tipo de Culinária")
    rating_cost = df_filtered.groupby(['country','cuisines']).agg({
        'aggregate_rating':'mean',
        'average_cost_for_two':'mean'
    }).reset_index()
    fig_rating = px.bar(
        rating_cost,
        x='cuisines',
        y='aggregate_rating',
        color='country',
        labels={"cuisines":"Tipo de Culinária", "aggregate_rating":"Nota Média"},
        title="Nota Média por Tipo de Culinária"
    )
    fig_cost = px.bar(
        rating_cost,
        x='cuisines',
        y='average_cost_for_two',
        color='country',
        labels={"cuisines":"Tipo de Culinária", "average_cost_for_two":"Preço Médio para Dois"},
        title="Preço Médio por Tipo de Culinária"
    )
    st.plotly_chart(fig_rating, use_container_width=True)
    st.plotly_chart(fig_cost, use_container_width=True)

st.markdown("""---""")

# ------------------------ CONTAINER 3: MAPA DE RESTAURANTES ------------------------
st.markdown("### Localização dos Restaurantes")
df_map = df_filtered.groupby(['country','cuisines','latitude','longitude']).agg({'restaurant_id':'count'}).reset_index()
fig_map = px.scatter_mapbox(
    df_map,
    lat='latitude',
    lon='longitude',
    size='restaurant_id',
    color='country',
    hover_name='cuisines',
    hover_data={'restaurant_id':True},
    zoom=1,
    height=600
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)
