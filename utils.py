import pandas as pd
import streamlit as st

# Mapeamento de Country Code (padrão Zomato)
COUNTRY_MAP = {
    1: "India", 14: "Australia", 30: "Brazil", 37: "Canada",
    94: "Indonesia", 148: "New Zealand", 162: "Philippines",
    166: "Qatar", 184: "Singapore", 189: "South Africa",
    191: "Sri Lanka", 208: "Turkey", 214: "United Arab Emirates",
    215: "United Kingdom", 216: "United States"
}

@st.cache_data
def load_data(path="dataset/zomato.csv"):
    """
    Carrega o CSV e aplica padronizações básicas.
    Retorna um DataFrame com colunas usuais:
    - country, city, cuisines, rating, latitude, longitude, price_num, name
    """
    df = pd.read_csv(path, encoding="utf-8", low_memory=False)

    # Normalizar nomes de colunas (remover espaços em branco nas extremidades)
    df.columns = [c.strip() for c in df.columns]

    # --- Country ---
    # Preferir "Country Code" (exato) quando presente
    if "Country Code" in df.columns:
        df["country"] = df["Country Code"].map(COUNTRY_MAP)
    else:
        # procurar variação lowercase 'country code'
        lowcols = {c.lower(): c for c in df.columns}
        if "country code" in lowcols:
            df["country"] = df[lowcols["country code"]].map(COUNTRY_MAP)
        elif "country" in lowcols:
            df["country"] = df[lowcols["country"]]
        else:
            df["country"] = None

    # --- City ---
    lowcols = {c.lower(): c for c in df.columns}
    if "city" in lowcols:
        df["city"] = df[lowcols["city"]]
    elif "location" in lowcols:
        df["city"] = df[lowcols["location"]]
    else:
        df["city"] = None

    # --- Cuisines ---
    if "cuisines" in lowcols:
        df["cuisines"] = df[lowcols["cuisines"]]
    elif "cuisine" in lowcols:
        df["cuisines"] = df[lowcols["cuisine"]]
    else:
        # algumas bases usam 'listed_in(type)' ou similar; keep None if not found
        df["cuisines"] = None

    # --- Latitude / Longitude ---
    # tentar várias colunas possíveis
    lat_candidates = [c for c in df.columns if "lat" in c.lower()]
    lon_candidates = [c for c in df.columns if "lon" in c.lower() or "long" in c.lower()]
    if lat_candidates:
        df["latitude"] = pd.to_numeric(df[lat_candidates[0]], errors="coerce")
    else:
        df["latitude"] = None
    if lon_candidates:
        df["longitude"] = pd.to_numeric(df[lon_candidates[0]], errors="coerce")
    else:
        df["longitude"] = None

    # --- Rating ---
    # detectar qualquer coluna que contenha 'rating' no nome
    possible_rating_cols = [c for c in df.columns if "rating" in c.lower()]
    if possible_rating_cols:
        selected = possible_rating_cols[0]
        df["rating"] = pd.to_numeric(df[selected], errors="coerce")
    else:
        df["rating"] = None

    # --- Price / custo (tentar converter) ---
    price_candidates = [c for c in df.columns if "price" in c.lower() or "cost" in c.lower()]
    df["price_num"] = None
    if price_candidates:
        for pc in price_candidates:
            tmp = pd.to_numeric(df[pc], errors="coerce")
            if tmp.notna().sum() > 0:
                df["price_num"] = tmp
                break
        # se ainda vazio, tentar contar símbolos (ex: '₹')
        if df["price_num"].isna().all():
            for pc in price_candidates:
                df["price_num"] = df[pc].astype(str).apply(lambda x: x.count("₹") if pd.notna(x) else None)
                if df["price_num"].notna().sum() > 0:
                    break

    # --- Nome / identificador ---
    if "name" in df.columns:
        df["name"] = df["name"]
    elif "restaurant_name" in df.columns:
        df["name"] = df["restaurant_name"]
    else:
        # tentar achar uma coluna que pareça nome
        name_col = None
        for c in df.columns:
            if c.lower() in ["name", "restaurant_name", "restaurant"]:
                name_col = c
                break
        df["name"] = df[name_col] if name_col else None

    # --- Limpeza final de strings ---
    str_cols = df.select_dtypes(include="object").columns
    for c in str_cols:
        # evitar transformar None em 'None' quando coluna for realmente None
        if df[c].notna().sum() > 0:
            df[c] = df[c].astype(str).str.strip()
        else:
            df[c] = df[c]

    return df


def top_n(df, groupby_col, value_col, n=10, agg="count"):
    """
    Agrupa e retorna os top N por groupby_col.
    Por padrão faz count (número de registros).
    Retorna DataFrame com colunas [groupby_col, value].
    """
    if groupby_col not in df.columns:
        return pd.DataFrame({groupby_col: [], "value": []})

    if agg == "count":
        g = df.groupby(groupby_col)[value_col].count().sort_values(ascending=False).head(n)
    else:
        g = df.groupby(groupby_col)[value_col].agg(agg).sort_values(ascending=False).head(n)
    return g.reset_index().rename(columns={value_col: "value"})
