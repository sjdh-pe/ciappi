"""
Funções cacheadas para buscar listas de tabelas auxiliares da API.
Usar em qualquer página: from components.listas import municipios, tecnicos, ...
"""
import streamlit as st
from api.client import get


@st.cache_data(ttl=300, show_spinner=False)
def municipios() -> list[str]:
    """Lista de municípios de Pernambuco ordenada alfabeticamente."""
    try:
        dados = get("/tabelas/municipios")
        return sorted([d["municipio"] for d in dados if d.get("municipio")])
    except Exception:
        return []


@st.cache_data(ttl=120, show_spinner=False)
def tecnicos() -> list[str]:
    try:
        return [t["TbNomeTecnico"] for t in get("/tabelas/tecnicos")]
    except Exception:
        return []


@st.cache_data(ttl=120, show_spinner=False)
def motivos_atendimento() -> dict[str, str]:
    """Retorna {descricao: str(codigo)} — o código é o que está gravado no banco."""
    try:
        return {m["TbDescricaoMotivo"]: str(m["Codigo"])
                for m in get("/tabelas/motivos-atendimento")
                if m.get("TbDescricaoMotivo")}
    except Exception:
        return {}


@st.cache_data(ttl=120, show_spinner=False)
def origens() -> list[str]:
    try:
        return [o["descricaochegouprograma"] for o in get("/tabelas/origem")]
    except Exception:
        return []


@st.cache_data(ttl=120, show_spinner=False)
def tipos_acao() -> list[str]:
    try:
        return [t["DescricaoAcao"] for t in get("/tabelas/tipo-acao")]
    except Exception:
        return ["Visita Domiciliar", "Atendimento Individual", "Encaminhamento", "Concluída para Ouvidoria"]


@st.cache_data(ttl=120, show_spinner=False)
def tipos_evento() -> list[str]:
    try:
        return [t["tipoevento"] for t in get("/tabelas/tipo-evento")]
    except Exception:
        return ["Capacitação", "Palestra", "Oficina", "Seminário"]


@st.cache_data(ttl=120, show_spinner=False)
def motivos_visita() -> list[str]:
    try:
        return [m["motivovisita"] for m in get("/tabelas/motivos-visita")]
    except Exception:
        return ["Fiscalização", "Acompanhamento", "Orientação"]


@st.cache_data(ttl=120, show_spinner=False)
def ilpis_map() -> dict:
    """Retorna {NOMEILPI: CODIGOILPI}."""
    try:
        return {i["NOMEILPI"]: i["CODIGOILPI"] for i in get("/ilpis/")}
    except Exception:
        return {}


def selectbox_municipio(label: str = "Município *", key: str = None, index: int = 0):
    """
    Selectbox padronizado de município.
    Adiciona opção vazia no topo para forçar seleção consciente.
    """
    opts = [""] + municipios()
    kwargs = {"key": key} if key else {}
    sel = st.selectbox(label, opts, index=index, **kwargs)
    return sel


def selectbox_municipio_col(col, label: str = "Município *", key: str = None, index: int = 0):
    """Mesmo que selectbox_municipio mas renderiza dentro de uma coluna Streamlit."""
    opts = [""] + municipios()
    kwargs = {"key": key} if key else {}
    return col.selectbox(label, opts, index=index, **kwargs)
