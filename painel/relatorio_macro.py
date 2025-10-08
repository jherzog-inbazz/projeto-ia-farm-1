from PIL import Image
import streamlit as st
import pandas as pd

import re
import ast

from painel.filtro.filtro_relatorio_macro import *
from painel.funcao.funcao_relatorio_macro import *

def app_relatorio_macro():
    
    col1, col2 = st.columns([2, 5])
    with col1:
        st.image("img/Logo-Farm.png", use_container_width=True)
    with col2:
        st.write("")

    st.markdown("# Insights de Performance dos Conteúdos da Farm")
    
    base_filtrada = app_filtro_relatorio_macro()

    st.subheader("📊 Conceitos Básicos")

    with st.container():
        app_funcao_conceito_basico_parte01(base_filtrada)
    
    with st.container():
        app_funcao_conceito_basico_parte02(base_filtrada)
    
    st.subheader("📈 Análises Detalhadas")

    with st.container():

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            app_funcao_tipo_post(base_filtrada)

        with col2:
            app_funcao_temporal(base_filtrada)

        with col3:
            app_funcao_objetos(base_filtrada)

        with col4:
            app_funcao_hashtags(base_filtrada)

    with st.container():

        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            app_funcao_cor_predominantes_dia(base_filtrada)

        with col2:
            app_funcao_emocoes_legenda(base_filtrada)
        
        with col3:
            app_funcao_nuvem_palavras(base_filtrada, min_publicacoes_default=3, stopwords_extra={"farm", "look","ate"})

    st.subheader("📈 Agrupamento de Padrões de Influência")

    with st.container():

        col1, col2, col3, col4, col5, col6 = st.columns([1,1,1,1,1,1])

        with col1:
            grafico_topicos_imagem(base_filtrada, top_n=10)
        
        with col2:
            grafico_gatilhos_imagem(base_filtrada, top_n=10)
        
        with col3:
            grafico_ctas_imagem(base_filtrada, top_n=10)

        with col4:
            grafico_topicos_legenda(base_filtrada, top_n=10)

        with col5:
            grafico_gatilhos_legenda(base_filtrada, top_n=10)

        with col6:
            grafico_ctas_legenda(base_filtrada, top_n=10)

    df_filtrado = etapa_filtro_contexto_farm(base_filtrada)
    
    # passe o DF já filtrado (ex.: df_ctx da sua etapa de contexto FARM)
    carrossel_imagens(df_filtrado, ordenar="Mais recentes")

