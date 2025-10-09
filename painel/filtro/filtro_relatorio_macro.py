from PIL import Image
import streamlit as st
import pandas as pd
import re
import ast

def app_filtro_relatorio_macro():

    # Importar a base em formato json base_farm_json at
    df = pd.read_json('data/base_farm_json_ajust.json')

    # Filtrar casos que post_type não é NaN
    df = df[df['post_type'].notna()]

    # Renomear as categorias do post_type
    df['post_type'] = df['post_type'].replace({
        'carousel_container': 'Carrossel',
        'feed': 'Feed',
        'clips': 'Reels',
        'tiktok': 'Tiktok'
    })

    # Identificar variáveis que estão em formato de dicionário {}
    dict_columns = df.columns[df.applymap(lambda x: isinstance(x, dict)).any()]

    # Expandir colunas de dicionário para colunas separadas
    for col in dict_columns:
        dict_expanded = df[col].apply(pd.Series)
        dict_expanded = dict_expanded.add_prefix(f'{col}_')
        df = pd.concat([df, dict_expanded], axis=1)
        df = df.drop(columns=[col])

    df['post_date_resumo'] = pd.to_datetime(df['post_date'], format='%Y-%m-%dT%H:%M:%S.%fZ')

    with st.expander("Filtros"):
        c1, c2, c3 = st.columns(3)  # Agora são 3 colunas

        # 1) Filtro de datas
        if df["post_date_resumo"].notna().any():
            min_date = df["post_date_resumo"].min().date()
            max_date = df["post_date_resumo"].max().date()
            date_start, date_end = c1.slider(
                "Período de publicação",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
                format="DD/MM/YYYY",
            )
        else:
            date_start = date_end = None
            c1.info("Sem datas válidas em 'post_date'.")

        # 2) Filtro por tipo de post
        post_types = sorted(df["post_type"].dropna().unique().tolist()) if "post_type" in df.columns else []
        post_type_sel = c2.multiselect("Tipo de Publicação", post_types, default=post_types)

        # 3) Filtro por marca
        marcas = sorted(df['marca'].dropna().unique().tolist()) if 'marca' in df.columns else ['Farm', 'Insider']
        marca_sel = c3.multiselect("Marca", marcas, default=marcas)

    # =========================
    # Aplicar filtros
    # =========================
    base_filtrada = df.copy()

    if date_start and date_end:
        base_filtrada = base_filtrada[
            (base_filtrada["post_date_resumo"] >= pd.to_datetime(date_start)) &
            (base_filtrada["post_date_resumo"] <= pd.to_datetime(date_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
        ]

    if post_types and post_type_sel:
        base_filtrada = base_filtrada[base_filtrada["post_type"].isin(post_type_sel)]

    if marca_sel:
        base_filtrada = base_filtrada[base_filtrada["marca"].isin(marca_sel)]

    return base_filtrada
