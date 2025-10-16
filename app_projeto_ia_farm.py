from PIL import Image
import streamlit as st
from authentication.login import login_user

from painel.relatorio_macro import *

# Configuração da página
st.set_page_config(
    page_title="Inbazz View",
    layout="wide",
    page_icon=Image.open("img/favicon.png"),
)

# Autenticação
authenticator = login_user()
auth_status = st.session_state.get("authentication_status", None)

def mostrar_logo_e_login():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("img/Logo-Principal.png", use_container_width=True)
    st.markdown(
        "<h3 style='text-align: center; margin-top: 10px;'>Inbazz View</h3>",
        unsafe_allow_html=True,
    )
    authenticator.login(
        location='main',
        fields={
            "Form name": "Acesso ao Sistema",
            "Username": "Usuário",
            "Password": "Senha"
        }
    )

if auth_status is None:
    mostrar_logo_e_login()

elif auth_status is False:
    st.error("Usuário ou senha incorretos.")
    mostrar_logo_e_login()

else:

    st.image("img/row-logos.png", use_container_width=True)
                
    # Permissão por tipo de usuário
    usuarios_autorizados = {
        "inbazz": "inbazz"
    }

    usuario_tipo = st.session_state.get("email")

    if usuario_tipo in usuarios_autorizados.values():
        app_relatorio_macro(authenticator)
    else:
        st.warning("Acesso restrito. Usuário não autorizado ou sessão inválida.")