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
    Retorna um DataFrame com colunas: country, city, cuisines, rating, latitude, longitude, price_num (quando possível).
    """
    df = pd.read_csv(path, encoding="utf-8")

    # Normalizar nomes de colunas (remover espaços em branco nas extremidades)
    df.columns = [c.strip() for c in df.columns]

    # --- Country ---
    # Preferir "Country Code" (exato) quando presente, caso contrário procurar variações
    if "Country Code" in df.columns:
        df["country"] = df["Country Code"].map(COUNTRY_MAP)
    elif "country code" in [c.lower() for c in df.columns]:
        # localizar coluna com nome que ao lower() resulte em 'country code'
        col = [c for c in df.columns if c.lower() == "country code"][0]
        df["country"] = df[col].map(COUNTRY_MAP)
    else:
        # se já existir coluna 'country' (com nomes) mantemos
        if "country" in df.columns:
            df["country"] = df["country"]
        # senão, criamos coluna vazia para consistência
        else:
            df["country"] = None

    # --- City ---
    # procurar pela coluna 'city' (ou variações)
    if "city" not in df.columns:
        lowcols = {c.lower(): c for c in df.columns}
        if "city" in lowcols:
            df["city"] = df[lowcols["city"]]
        else:
            # tentar localizar colunas comuns diferentes (ex: 'location')
            if "location" in lowcols:
                df["city"] = df[lowcols["location"]]
            else:
                df["city"] = None

    # --- Cuisines ---
    # Zomato normalmente tem 'cuisines'
    if "cuisines" not in df.columns:
        lowcols = {c.lower(): c for c in df.columns}
        if "cuisines" in lowcols:
            df["cuisines"] = df[lowcols["cuisines"]]
        elif "cuisine" in lowcols:
            df["cuisines"] = df[lowcols["cuisine"]]
        else:
            df["cuisines"] = None

    # --- Latitude / Longitude ---
    for col in ["latitude", "Longitude", "longitude", "lat"]:
        if col in df.columns and "latitude" not in df.columns:
            if col.lower().startswith("lat"):
                df["latitude"] = pd.to_numeric(df[col], errors="coerce")
    for col in ["longitude", "Longitude", "lon"]:
        if col in df.columns and "longitude" not in df.columns:
            if col.lower().startswith("lon") or col.lower().startswith("long"):
                df["longitude"] = pd.to_numeric(df[col], errors="coerce")

    # Se ainda não existirem latitude/longitude, tenta buscar por colunas parecidas
    if "latitude" not in df.columns:
        possible = [c for c in df.columns if "lat" in c.lower()]
        df["latitude"] = pd.to_numeric(df[possible[0]], errors="coerce") if possible else None
    if "longitude" not in df.columns:
        possible = [c for c in df.columns if "lon" in c.lower() or "long" in c.lower()]
        df["longitude"] = pd.to_numeric(df[possible[0]], errors="coerce") if possible else None

    # --- Rating ---
    # Normalize rating: procurar por 'rating' ou 'aggregate_rating'
    if "rating" not in df.columns:
        lowcols = {c.lower(): c for c in df.columns}
        if "aggregate_rating" in lowcols:
            df["rating"] = pd.to_numeric(df[lowcols["aggregate_rating"]], errors="coerce")
        elif "rating" in lowcols:
            df["rating"] = pd.to_numeric(df[lowcols["rating"]], errors="coerce")
        else:
            df["rating"] = pd.to_numeric(df.get("rating", None), errors="coerce")
    else:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # --- Price / custo (tentativa robusta) ---
    # Alguns datasets possuem 'price', 'price_range', 'approx_cost(for two people)' etc.
    price_candidates = [c for c in df.columns if "price" in c.lower() or "cost" in c.lower()]
    df["price_num"] = None
    if price_candidates:
        # tentar converter diretamente quando for numérico
        for pc in price_candidates:
            try:
                tmp = pd.to_numeric(df[pc], errors="coerce")
                if tmp.notna().sum() > 0:
                    df["price_num"] = tmp
                    break
            except Exception:
                continue
        # se nenhuma for numérica, tentar contar símbolos (ex: '₹₹')
        if df["price_num"].isna().all():
            for pc in price_candidates:
                # contar '₹' ou sinais semelhantes
                df["price_num"] = df[pc].astype(str).apply(lambda x: x.count("₹") if pd.notna(x) else None)
                if df["price_num"].notna().sum() > 0:
                    break

    # --- Nome / identificador ---
    # garantir campos básicos para uso nas páginas
    if "name" not in df.columns and "restaurant_name" in df.columns:
        df["name"] = df["restaurant_name"]
    if "name" not in df.columns:
        # tentar achar alguma coluna que pareça nome
        for c in df.columns:
            if c.lower() in ["name", "restaurant_name", "restaurant"]:
                df["name"] = df[c]
                break

    # --- Limpeza final de strings ---
    str_cols = df.select_dtypes(include="object").columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()

    return df


def top_n(df, groupby_col, value_col, n=10, agg="count"):
    """
    Agrupa e retorna os top N por um groupby_col.
    Por padrão faz count (número de registros).
    """
    if groupby_col not in df.columns:
        return pd.DataFrame({groupby_col: [], "value": []})

    if agg == "count":
        g = df.groupby(groupby_col)[value_col].count().sort_values(ascending=False).head(n)
    else:
        g = df.groupby(groupby_col)[value_col].agg(agg).sort_values(ascending=False).head(n)
    return g.reset_index().rename(columns={value_col: "value"})
