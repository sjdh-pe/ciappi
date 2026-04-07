import streamlit as st
import pandas as pd
from api.client import get, post
from datetime import datetime
from components.styles import card_section
from components.listas import municipios, tipos_evento as _tipos_evento_lista


def show():
    st.markdown("""
        <div style="padding:4px 0 16px">
            <h2 style="margin:0;color:#1a3a5c">📅 Eventos</h2>
            <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                Registro de eventos e ações coletivas
            </div>
        </div>
        <hr style="border:none;border-top:2px solid #e0e9f4;margin-bottom:20px">
    """, unsafe_allow_html=True)

    aba = st.tabs(["📋 Listar Eventos", "➕ Cadastrar Evento"])

    # ── Listar ───────────────────────────────────────────────────────────────
    with aba[0]:
        if st.button("🔄 Carregar Eventos", type="primary", key="btn_carregar_eventos"):
            with st.spinner("Carregando..."):
                try:
                    dados = get("/eventos/")
                    if dados:
                        df = pd.DataFrame(dados)
                        cols_show = ["Codigo", "tbnomeevento", "tbtipoevento",
                                     "Tbdataprevista", "TbDataRealizacao",
                                     "TbMunicipioevento", "TbPublicoPresente"]
                        df = df[[c for c in cols_show if c in df.columns]].copy()
                        col_names = {
                            "Codigo": "Cód.", "tbnomeevento": "Evento",
                            "tbtipoevento": "Tipo", "Tbdataprevista": "Dt. Prevista",
                            "TbDataRealizacao": "Dt. Realização",
                            "TbMunicipioevento": "Município", "TbPublicoPresente": "Público",
                        }
                        df.columns = [col_names.get(c, c) for c in df.columns]
                        for col_dt in ["Dt. Prevista", "Dt. Realização"]:
                            if col_dt in df.columns:
                                df[col_dt] = pd.to_datetime(df[col_dt], errors="coerce")
                        st.success(f"✅ {len(df)} evento(s) encontrado(s).")
                        st.dataframe(
                            df, use_container_width=True, hide_index=True,
                            column_config={
                                "Cód.": st.column_config.NumberColumn("Cód.", format="%d", width="small"),
                                "Evento": st.column_config.TextColumn("Evento", width="large"),
                                "Dt. Prevista": st.column_config.DatetimeColumn("Dt. Prevista", format="DD/MM/YYYY"),
                                "Dt. Realização": st.column_config.DatetimeColumn("Dt. Realização", format="DD/MM/YYYY"),
                                "Público": st.column_config.NumberColumn("Público", format="%d", width="small"),
                            }
                        )
                    else:
                        st.info("Nenhum evento cadastrado.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Cadastrar ────────────────────────────────────────────────────────────
    with aba[1]:
        with st.container(border=True):
            card_section("Identificação")
            opts = _tipos_evento_lista()
            tipo    = st.selectbox("Tipo de Evento *", opts)
            nome_ev = st.text_input("Nome do Evento *", placeholder="Título do evento")
            objetivo = st.text_area("Objetivo", height=80,
                                    placeholder="Descreva o objetivo do evento...")

            card_section("Dados de Realização")
            col1, col2 = st.columns(2)
            dt_prevista = col1.date_input("Data Prevista *", format="DD/MM/YYYY")
            municipio   = col2.selectbox("Município *", [""] + municipios(), key="evento_mun")
            local       = st.text_input("Local do Evento", placeholder="Endereço ou nome do local")

            card_section("Público")
            col3, col4 = st.columns(2)
            publico_alvo = col3.text_input("Público-alvo", placeholder="Ex: Cuidadores, Idosos...")
            publico_est  = col4.number_input("Público Estimado", min_value=0)

            salvar = st.button("💾 Cadastrar Evento", use_container_width=True, type="primary")

        if salvar:
            if not nome_ev or not municipio:
                st.error("⚠️ Nome do evento e município são obrigatórios.")
            else:
                with st.spinner("Cadastrando..."):
                    try:
                        post("/eventos/", {
                            "tbtipoevento":     tipo,
                            "tbnomeevento":     nome_ev,
                            "Tbobjetivoevento": objetivo,
                            "Tbdataprevista":   str(datetime.combine(dt_prevista, datetime.min.time())),
                            "Tbpublicoalvo":    publico_alvo,
                            "TbPublicoEstimado": publico_est,
                            "Tblocalevento":    local,
                            "TbMunicipioevento": municipio.upper(),
                        })
                        st.success("✅ Evento cadastrado com sucesso!")
                        _tipos_evento_lista.clear()
                    except Exception as e:
                        st.error(f"Erro: {e}")
