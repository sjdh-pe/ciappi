"""
Estilos CSS globais e utilitários visuais para o CIAPPI.
Importar em app.py via: from components.styles import apply_global_css
"""
import streamlit as st


def apply_global_css():
    st.markdown("""
    <style>
    /* ── Esconde navegação automática do Streamlit (pages/) ──────── */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    section[data-testid="stSidebarNav"] { display: none !important; }

    /* ── Sidebar ─────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a3a5c 0%, #0d2137 100%) !important;
    }

    /* Texto da sidebar: branco puro para máximo contraste no fundo escuro */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] caption { color: #ffffff !important; }

    [data-testid="stSidebar"] .stButton > button {
        background: transparent;
        border: none;
        border-radius: 6px;
        color: #ffffff !important;
        font-size: 14px;
        text-align: left;
        padding: 7px 14px;
        width: 100%;
        transition: background 0.15s;
        cursor: pointer;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.15) !important;
        color: #ffffff !important;
    }
    .nav-active > div > div > button {
        background: rgba(255,255,255,0.22) !important;
        font-weight: 700 !important;
        border-left: 3px solid #90caf9 !important;
        color: #ffffff !important;
    }
    .nav-section-label {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: rgba(255,255,255,0.55) !important;
        padding: 14px 0 4px 4px;
        display: block;
    }

    /* ── Metrics ─────────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        border: 1px solid #e0e9f4;
        border-radius: 12px;
        padding: 18px 20px 14px !important;
        box-shadow: 0 2px 8px rgba(13,33,55,0.07);
    }
    [data-testid="stMetricLabel"] { font-size: 13px !important; }
    [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700 !important; }

    /* ── Tabs ────────────────────────────────────────────────────── */
    [data-testid="stTabs"] [data-baseweb="tab"] {
        font-size: 14px;
        padding: 8px 18px;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        font-weight: 600 !important;
        border-bottom: 3px solid #1a3a5c !important;
    }

    /* ── Buttons principais ──────────────────────────────────────── */
    .stButton > button[kind="primary"] {
        background: #1a3a5c !important;
        border: none;
        font-weight: 600;
        color: #ffffff !important;
    }

    /* ── Status badges (cores explícitas para ambos os modos) ────── */
    .badge-ativo  { background:#d4edda; color:#155724 !important; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-enc    { background:#f8d7da; color:#721c24 !important; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-alerta { background:#fff3cd; color:#856404 !important; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }

    /* ── Cards informativos (cor de texto explícita) ─────────────── */
    .info-card {
        background: #1e3a5a;
        border: 1px solid #2d5a8a;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #dce8f5 !important;
    }
    .warn-card {
        background: #3a2e00;
        border: 1px solid #7a6000;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #ffd970 !important;
    }
    .danger-card {
        background: #3a1a1a;
        border: 1px solid #7a3030;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #f8a0a0 !important;
    }

    /* ── Sidebar divider ─────────────────────────────────────────── */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.15) !important;
    }

    /* ── card_section title (funciona em dark mode via inherit) ──── */
    .section-title {
        font-size: 14px;
        font-weight: 700;
        border-left: 4px solid #4a9adc;
        padding-left: 10px;
        margin: 16px 0 8px;
        opacity: 0.9;
    }
    </style>
    """, unsafe_allow_html=True)


def badge(texto: str, tipo: str = "ativo") -> str:
    """Retorna HTML de um badge colorido. tipo: ativo | enc | alerta"""
    cls = {"ativo": "badge-ativo", "enc": "badge-enc", "alerta": "badge-alerta"}.get(tipo, "badge-ativo")
    return f'<span class="{cls}">{texto}</span>'


def card_section(titulo: str):
    """Subheader estilizado de seção — usa classe CSS para funcionar em dark e light mode."""
    st.markdown(f'<div class="section-title">{titulo}</div>', unsafe_allow_html=True)
