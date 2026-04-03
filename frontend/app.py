import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
from auth.login import show_login, logout
from components.styles import apply_global_css

st.set_page_config(
    page_title="CIAPPI — SJDH/PE",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_css()

# ── Autenticação ───────────────────────────────────────────────────────────────
if not st.session_state.get("autenticado"):
    show_login()
    st.stop()

nivel = st.session_state.get("nivel", 1)
nome  = st.session_state.get("usuario_nome", "")

# ── Inicializa página corrente em session_state ────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "inicio"


def _nav(label: str, icon: str, key: str):
    """Botão de navegação que atualiza session_state['pagina'] e reroda."""
    ativo = st.session_state["pagina"] == key
    container = st.sidebar.container()
    if ativo:
        container.markdown('<div class="nav-active">', unsafe_allow_html=True)
    if container.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{key}"):
        st.session_state["pagina"] = key
        st.rerun()
    if ativo:
        container.markdown("</div>", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Cabeçalho
    st.markdown("""
        <div style="padding:12px 4px 8px;text-align:center">
            <div style="font-size:28px">🛡️</div>
            <div style="font-size:17px;font-weight:800;color:#fff;letter-spacing:.5px">CIAPPI</div>
            <div style="font-size:11px;color:rgba(220,232,245,.6);margin-top:2px">SJDH / Pernambuco</div>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Info do usuário
    nivel_label = {1: "Consulta", 2: "Operador", 3: "Administrador"}.get(nivel, f"Nível {nivel}")
    st.markdown(f"""
        <div style="background:rgba(255,255,255,.08);border-radius:8px;padding:10px 12px;margin-bottom:4px">
            <div style="font-size:13px;font-weight:700;color:#fff">👤 {nome}</div>
            <div style="font-size:11px;color:rgba(220,232,245,.7)">🔑 {nivel_label}</div>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    # ── Navegação ──────────────────────────────────────────────────
    _nav("Início",  "🏠", "inicio")

    if nivel >= 2:
        st.markdown('<span class="nav-section-label">Atendimento</span>', unsafe_allow_html=True)
        _nav("Casos",              "📁", "casos")
        _nav("Usuários",           "👤", "usuarios")
        _nav("Acompanhamentos",    "📋", "acompanhamentos")

        st.markdown('<span class="nav-section-label">Estrutura</span>', unsafe_allow_html=True)
        _nav("ILPIs",              "🏛️", "ilpis")
        _nav("Visitas a ILPIs",    "🔍", "visitas_ilpi")
        _nav("Visitas Institucionais", "🏢", "visitas")
        _nav("Eventos",            "📅", "eventos")

    st.markdown('<span class="nav-section-label">Gestão</span>', unsafe_allow_html=True)
    _nav("Ouvidoria",          "📣", "ouvidoria")
    _nav("Relatórios",         "📊", "relatorios")

    if nivel >= 3:
        st.markdown('<span class="nav-section-label">Administração</span>', unsafe_allow_html=True)
        _nav("Tabelas Auxiliares", "⚙️", "admin_tabelas")

    st.divider()
    if st.button("↩ Sair", use_container_width=True):
        logout()


# ── Roteamento ─────────────────────────────────────────────────────────────────
pagina = st.session_state["pagina"]

if pagina == "inicio":
    from pages import menu_principal; menu_principal.show()
elif pagina == "casos":
    from pages import casos; casos.show()
elif pagina == "usuarios":
    from pages import usuarios; usuarios.show()
elif pagina == "acompanhamentos":
    from pages import acompanhamentos; acompanhamentos.show()
elif pagina == "ilpis":
    from pages import ilpis; ilpis.show()
elif pagina == "visitas_ilpi":
    from pages import visitas_ilpi; visitas_ilpi.show()
elif pagina == "visitas":
    from pages import visitas; visitas.show()
elif pagina == "eventos":
    from pages import eventos; eventos.show()
elif pagina == "ouvidoria":
    from pages import ouvidoria; ouvidoria.show()
elif pagina == "relatorios":
    from pages import relatorios; relatorios.show()
elif pagina == "admin_tabelas":
    from pages import admin_tabelas; admin_tabelas.show()
