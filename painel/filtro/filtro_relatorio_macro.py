from PIL import Image
import streamlit as st
import pandas as pd
import re
import ast

def app_filtro_relatorio_macro():

    # importar a base em formato json base_farm_json
    df = pd.read_json('data/base_farm_json.json')

    # renomear a coluna traking_id para post_pk
    df = df.rename(columns={'tracking_id': 'post_pk'})

    # Filtrar casos que post_type não é NaN
    df = df[df['post_type'].notna()]

    # Renomear as categorias do post_type
    df['post_type'] = df['post_type'].replace({
        'carousel_container': 'Carrossel',
        'feed': 'Feed',
        'clips': 'Reels'
    })

    # Identificar variáveis que estão em formato de dicionário {}
    dict_columns = df.columns[df.applymap(lambda x: isinstance(x, dict)).any()]

    # Quero pegar todas as colunas que são em formato de dicionário(dict_columns) e transformar em colunas separadas
    for col in dict_columns:
        # Expandir a coluna de dicionário em colunas separadas
        dict_expanded = df[col].apply(pd.Series)
        
        # Renomear as novas colunas para evitar conflitos
        dict_expanded = dict_expanded.add_prefix(f'{col}_')
        
        # Concatenar as novas colunas ao DataFrame original
        df = pd.concat([df, dict_expanded], axis=1)
        
        # Remover a coluna original de dicionário
        df = df.drop(columns=[col])

    df['post_date_resumo'] = pd.to_datetime(df['post_date'], format='%Y-%m-%dT%H:%M:%S.%fZ')

    with st.expander("Filtros"):
        c1, c2 = st.columns(2)

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

    # =========================
    # Aplicar filtros
    # =========================
    base_filtrada = df.copy()

    if date_start and date_end:
        base_filtrada = base_filtrada[
            (base_filtrada["post_date_resumo"] >= pd.to_datetime(date_start))
            & (base_filtrada["post_date_resumo"] <= pd.to_datetime(date_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
        ]

    if post_types and post_type_sel:
        base_filtrada = base_filtrada[base_filtrada["post_type"].isin(post_type_sel)]

    return base_filtrada