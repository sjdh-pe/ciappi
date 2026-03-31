import streamlit as st
from api.client import get, post
from datetime import datetime


def show():
    st.title("🏢 Visitas Institucionais")
    aba = st.tabs(["Listar", "Registrar Visita"])

    with aba[0]:
        if st.button("Carregar Visitas"):
            try:
                dados = get("/visitas/inst")
                if dados:
                    import pandas as pd
                    df = pd.DataFrame(dados)[[
                        "codigovisita", "nomeinstituicao", "datavista", "assuntovisita"
                    ]]
                    df.columns = ["Código", "Instituição", "Data", "Assunto"]
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    with aba[1]:
        with st.form("form_visita"):
            instituicao = st.text_input("Nome da Instituição*")
            col1, col2 = st.columns(2)
            dt_visita = col1.date_input("Data da Visita*")
            responsavel = col2.text_input("Responsável pela Instituição")
            assunto = st.text_input("Assunto da Visita*")
            relatorio = st.text_area("Relatório*", height=120)
            lembrete = st.date_input("Lembrete (opcional)", value=None)
            salvar = st.form_submit_button("Registrar Visita", use_container_width=True)

        if salvar:
            if not all([instituicao, assunto, relatorio]):
                st.error("Preencha todos os campos obrigatórios.")
            else:
                try:
                    dados = {
                        "nomeinstituicao": instituicao,
                        "datavista": str(datetime.combine(dt_visita, datetime.min.time())),
                        "assuntovisita": assunto,
                        "responsavelinstituicao": responsavel,
                        "relatorio": relatorio,
                    }
                    if lembrete:
                        dados["lembrete"] = str(datetime.combine(lembrete, datetime.min.time()))
                    post("/visitas/inst", dados)
                    st.success("Visita registrada com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")
