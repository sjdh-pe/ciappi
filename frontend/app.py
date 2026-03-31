import os
import sys

# Garante que a pasta frontend está no sys.path para suportar importação de módulos internos
# independentemente de onde o script é executado (ex: da raiz do projeto)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
from auth.login import show_login, logout

st.set_page_config(
    page_title="CIAPPI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Autenticação
if not st.session_state.get("autenticado"):
    show_login()
    st.stop()

# Sidebar com navegação
nivel = st.session_state.get("nivel", 1)
nome = st.session_state.get("usuario_nome", "")

with st.sidebar:
    st.markdown(f"**👤 {nome}**")
    st.caption(f"Nível de acesso: {nivel}")
    st.divider()

    if nivel >= 2:
        pagina = st.radio(
            "Menu",
            options=[
                "🏠 Início",
                "📁 Casos",
                "👤 Usuários",
                "📋 Acompanhamentos",
                "🏛️ ILPIs",
                "🏛️ Visitas a ILPIs",
                "📅 Eventos",
                "🏢 Visitas Institucionais",
                "📣 Ouvidoria",
                "📊 Relatórios",
                "⚙️ Tabelas (Admin)",
            ],
        )
    else:
        pagina = st.radio(
            "Menu",
            options=[
                "🏠 Início",
                "📊 Relatórios",
                "📣 Ouvidoria",
            ],
        )

    st.divider()
    if st.button("Sair", use_container_width=True):
        logout()

# Roteamento de páginas
if pagina == "🏠 Início":
    from pages import menu_principal
    menu_principal.show()
elif pagina == "📁 Casos":
    from pages import casos
    casos.show()
elif pagina == "👤 Usuários":
    from pages import usuarios
    usuarios.show()
elif pagina == "📋 Acompanhamentos":
    from pages import acompanhamentos
    acompanhamentos.show()
elif pagina == "🏛️ ILPIs":
    from pages import ilpis
    ilpis.show()
elif pagina == "🏛️ Visitas a ILPIs":
    from pages import visitas_ilpi
    visitas_ilpi.show()
elif pagina == "📅 Eventos":
    from pages import eventos
    eventos.show()
elif pagina == "🏢 Visitas Institucionais":
    from pages import visitas
    visitas.show()
elif pagina == "📣 Ouvidoria":
    from pages import ouvidoria
    ouvidoria.show()
elif pagina == "📊 Relatórios":
    from pages import relatorios
    relatorios.show()
elif pagina == "⚙️ Tabelas (Admin)":
    from pages import admin_tabelas
    admin_tabelas.show()
