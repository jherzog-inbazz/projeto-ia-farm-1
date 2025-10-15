from PIL import Image
import streamlit as st
import pandas as pd
import re
import ast

def app_filtro_relatorio_macro():

    # Importar a base em formato json base_farm_json at
    df = pd.read_json('data/data_insider.json')

    # Filtrar casos que post_type não é NaN
    df = df[df['post_type'].notna()]

    # Renomear as categorias do post_type
    df['post_type'] = df['post_type'].replace({
        'carousel_container': 'Carrossel',
        'feed': 'Feed',
        'clips': 'Reels',
        'tiktok': 'Tiktok',
        'story': 'Stories'
    })

    df['post_date_resumo'] = pd.to_datetime(df['post_date'], format='%Y-%m-%dT%H:%M:%S.%fZ')

    df = df[df['caption'].notnull()]

    with st.container():
        col1, col2 = st.columns(2)  # Agora são 3 colunas

        with col1:
            # 1) Filtro de datas
            if df["post_date_resumo"].notna().any():
                min_date = df["post_date_resumo"].min().date()
                max_date = df["post_date_resumo"].max().date()
                date_start, date_end = st.slider(
                    "Período de publicação",
                    min_value=min_date,
                    max_value=max_date,
                    value=(min_date, max_date),
                    format="DD/MM/YYYY",
                )
            else:
                date_start = date_end = None
                col1.info("Sem datas válidas em 'post_date'.")
                
        with col2:
            # 2) Filtro por tipo de post
            post_types = sorted(df["post_type"].dropna().unique().tolist()) if "post_type" in df.columns else []
            post_type_sel = st.multiselect("Tipo de Publicação", post_types, default=post_types)

        
        base_filtrada = df.copy()

        if date_start and date_end:
            base_filtrada = base_filtrada[
                (base_filtrada["post_date_resumo"] >= pd.to_datetime(date_start)) &
                (base_filtrada["post_date_resumo"] <= pd.to_datetime(date_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
            ]

        if post_types and post_type_sel:
            base_filtrada = base_filtrada[base_filtrada["post_type"].isin(post_type_sel)]

        #retornar as 3 primeiras variáveis da base filtrada
        return base_filtrada