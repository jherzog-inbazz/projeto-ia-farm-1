from PIL import Image
import streamlit as st
import pandas as pd
from authentication.login import login_user

import re
import ast

from painel.filtro.filtro_relatorio_macro import *
from painel.funcao.funcao_relatorio_macro import *

def app_relatorio_macro(authenticator):

    with st.container():

        col1,col2 = st.columns([19,1])
        
        with col1:
            st.markdown("# Insights de Performance dos Conteúdos da Farm")

        with col2:
            authenticator.logout(location='main')
    
    base_filtrada = app_filtro_relatorio_macro()

    st.subheader("📊 Informações Gerais")
    
    with st.container():
        app_funcao_conceito_basico_parte01(base_filtrada)
    
    with st.container():
        app_funcao_conceito_basico_parte02(base_filtrada)
    
    st.subheader("📈 Análises Detalhadas")

    with st.container():

        col1, col2, col3 = st.columns([1,2,2], border=True)
        
        with col1:
            app_funcao_tipo_post(base_filtrada)

        with col2:
            app_funcao_objetos(base_filtrada)
       
        with col3:
            app_funcao_hashtags(base_filtrada)

    with st.container():

        col1, col2 = st.columns([1, 1], border=True)
        
        with col1:
            app_funcao_emocoes_legenda(base_filtrada)

        with col2:
            grafico_topicos_legenda(base_filtrada, top_n=5)
    
    with st.container():

        col1, col2 = st.columns([1, 1], border=True)

        with col1:
            grafico_gatilhos_legenda(base_filtrada, top_n=5)

        with col2:
            grafico_ctas_legenda(base_filtrada, top_n=5)
    
    
    st.subheader("🧩 Mosaico de Imagens")
    filtro_e_mosaico_imagens(base_filtrada)

