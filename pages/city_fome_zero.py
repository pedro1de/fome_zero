# ------------------------ CITIES.PY ------------------------
import streamlit as st
import pandas as pd
import inflection
import plotly.express as px

# ------------------------ CONFIGURAÇÃO DA PÁGINA ------------------------
st.title("Visão Cidade")

st.set_page_config(page_title="Fome Zero - Cities", layout="wide")
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

# ------------------------ FILTROS ------------------------
selected_countries = st.sidebar.multiselect(
    "Selecione um ou mais países",
    options=df['country'].unique(),
    default=df['country'].unique()
)

df_country = df[df['country'].isin(selected_countries)]

st.sidebar.markdown("""---""")
st.sidebar.markdown("Powered by Pedro Oliveira")

# ------------------------ CONTAINERS ------------------------
col1, col2, col3 = st.columns(3)

# ---------- CONTAINER 1: RESTAURANTES ----------
with col1:
    st.markdown("### Restaurantes por Cidade")
    restaurants_count = df_country.groupby(['country','city'])['restaurant_id'].nunique().reset_index()
    restaurants_count = restaurants_count.sort_values('restaurant_id', ascending=False)
    fig_restaurants = px.bar(
        restaurants_count,
        x='city',
        y='restaurant_id',
        color='country',
        labels={"city":"Cidade", "restaurant_id":"Número de Restaurantes"},
        title="Número de Restaurantes por Cidade"
    )
    st.plotly_chart(fig_restaurants, use_container_width=True)

st.markdown("""---""")

# ---------- CONTAINER 2: RESERVAS E DELIVERY ----------
with col2:
    st.markdown("### Reservas por Cidade")
    booking = df_country.groupby(['country','city'])['has_table_booking'].sum().reset_index()
    fig_booking = px.bar(
        booking,
        x='city',
        y='has_table_booking',
        color='country',
        labels={"city":"Cidade", "has_table_booking":"Restaurantes com Reserva"},
        title="Reservas por Cidade"
    )
    st.plotly_chart(fig_booking, use_container_width=True)

with col3:
    st.markdown("### Delivery por Cidade")
    delivery = df_country.groupby(['country','city'])['has_online_delivery'].sum().reset_index()
    fig_delivery = px.bar(
        delivery,
        x='city',
        y='has_online_delivery',
        color='country',
        labels={"city":"Cidade", "has_online_delivery":"Restaurantes com Delivery"},
        title="Delivery por Cidade"
    )
    st.plotly_chart(fig_delivery, use_container_width=True)

st.markdown("""---""")

# ---------- CONTAINER 3: NOTA MÉDIA E PREÇO ----------
col4, col5 = st.columns(2)
with col4:
    st.markdown("### Nota Média por Cidade")
    rating = df_country.groupby(['country','city'])['aggregate_rating'].mean().reset_index()
    fig_rating = px.bar(
        rating,
        x='city',
        y='aggregate_rating',
        color='country',
        labels={"city":"Cidade", "aggregate_rating":"Nota Média"},
        title="Nota Média por Cidade"
    )
    st.plotly_chart(fig_rating, use_container_width=True)

with col5:
    st.markdown("### Preço Médio por Cidade")
    avg_cost = df_country.groupby(['country','city'])['average_cost_for_two'].mean().reset_index()
    fig_cost = px.bar(
        avg_cost,
        x='city',
        y='average_cost_for_two',
        color='country',
        labels={"city":"Cidade", "average_cost_for_two":"Preço Médio para Dois"},
        title="Preço Médio por Cidade"
    )
    st.plotly_chart(fig_cost, use_container_width=True)

st.markdown("""---""")

# ---------- CONTAINER 4: MAPA DE RESTAURANTES ----------
st.markdown("### Localização dos Restaurantes")
# Para o mapa, precisamos das coordenadas
df_map = df_country.groupby(['country','city','latitude','longitude']).agg({
    'restaurant_id':'count'
}).reset_index()

fig_map = px.scatter_mapbox(
    df_map,
    lat='latitude',
    lon='longitude',
    size='restaurant_id',
    color='country',
    hover_name='city',
    hover_data={'restaurant_id':True},
    zoom=1,
    height=600
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)
