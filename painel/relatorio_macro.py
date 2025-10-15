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

        col1,col2 = st.columns([18,1])
        
        with col1:
            st.markdown("# Resultado de Análise do Projeto IA - Inbazz 🤝 Insider")

        with col2:
            authenticator.logout(location='main')

    base_filtrada = app_filtro_relatorio_macro()
    
    base_filtrada = app_funcao_relatorio_macro(base_filtrada)

    
    

