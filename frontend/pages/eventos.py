import streamlit as st
from api.client import get, post
from datetime import datetime


def show():
    st.title("📅 Eventos")
    aba = st.tabs(["Listar", "Cadastrar"])

    with aba[0]:
        if st.button("Carregar Eventos"):
            try:
                dados = get("/eventos/")
                if dados:
                    import pandas as pd
                    df = pd.DataFrame(dados)
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    with aba[1]:
        with st.form("form_evento"):
            try:
                tipos = get("/tabelas/tipo-evento")
                opts = [t["tipoevento"] for t in tipos]
            except Exception:
                opts = ["Capacitação", "Palestra", "Oficina"]
            tipo = st.selectbox("Tipo de Evento*", opts)
            nome_ev = st.text_input("Nome do Evento")
            objetivo = st.text_area("Objetivo", height=80)
            col1, col2 = st.columns(2)
            dt_prevista = col1.date_input("Data Prevista")
            municipio = col2.text_input("Município")
            publico_alvo = st.text_input("Público-alvo")
            publico_est = st.number_input("Público Estimado", min_value=0)
            local = st.text_input("Local do Evento")
            salvar = st.form_submit_button("Cadastrar Evento", use_container_width=True)

        if salvar:
            try:
                post("/eventos/", {
                    "tbtipoevento": tipo,
                    "tbnomeevento": nome_ev,
                    "Tbobjetivoevento": objetivo,
                    "Tbdataprevista": str(datetime.combine(dt_prevista, datetime.min.time())),
                    "Tbpublicoalvo": publico_alvo,
                    "TbPublicoEstimado": publico_est,
                    "Tblocalevento": local,
                    "TbMunicipioevento": municipio,
                })
                st.success("Evento cadastrado com sucesso!")
            except Exception as e:
                st.error(f"Erro: {e}")
