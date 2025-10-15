from PIL import Image
import streamlit as st
import pandas as pd
import re
import ast

def app_funcao_relatorio_macro(base_filtrada):

    # Selecionar as variáveis de interesse
    variaveis_interesse = [
        'cod_ident',
        'post_type',
        'post_date',
        'post_url',
        'imagem_hashtags',
        'imagem_mentions',
        'imagem_urls',
        'imagem_emoticoins',
        'imagem_coupon_codes',
        'imagem_seller_codes',
        'imagem_types_products',
        'imagem_product_focus_image',
        'imagem_category',
        'imagem_triggers',
        'imagem_possibilities_cta',
        'imagem_sentiment_score',
        'imagem_emotion',
        'legenda_hashtags',
        'legenda_mentions',
        'legenda_urls',
        'legenda_emoticoins',
        'legenda_coupon_codes',
        'legenda_seller_codes',
        'legenda_category',
        'legenda_triggers',
        'legenda_possibilities_cta',
        'legenda_sentiment_score',
        'legenda_emotion',
        'legenda_style_metrics',
        'legenda_style_description',
        'legenda_target_audience_age',
        'legenda_suggested_improvements',
        'legenda_is_ai_generated',
        'legenda_evidence',
        'legenda_style_characteristics',
        'legenda_ai_probability',
        'legenda_overall_classification',
        'legenda_product_principles'
    ]

    # Criar um DataFrame com as variáveis selecionadas colunas
    base_filtrada = base_filtrada[variaveis_interesse].copy()

    

    st.dataframe(base_filtrada, use_container_width=True)