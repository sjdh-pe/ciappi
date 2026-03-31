import streamlit as st
from api.client import get, post, put


def show():
    st.title("🏛️ ILPIs — Instituições de Longa Permanência")
    aba = st.tabs(["Listar", "Cadastrar", "Atualizar"])

    with aba[0]:
        if st.button("Carregar ILPIs"):
            try:
                dados = get("/ilpis/")
                if dados:
                    import pandas as pd
                    df = pd.DataFrame(dados)[[
                        "CODIGOILPI", "NOMEILPI", "MUNICIPIO",
                        "CAPACIDADEIDOSOS", "IDOSOSRESIDENTES", "STATUS"
                    ]]
                    df.columns = ["Código", "Nome", "Município", "Capacidade", "Residentes", "Status"]
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    with aba[1]:
        with st.form("form_ilpi"):
            nome = st.text_input("Nome da ILPI*")
            col1, col2 = st.columns(2)
            responsavel = col1.text_input("Responsável*")
            tipo = col2.selectbox("Tipo de Entidade*", ["Pública", "Privada", "Filantrópica"])
            col3, col4 = st.columns(2)
            capacidade = col3.number_input("Capacidade*", min_value=0)
            residentes = col4.number_input("Residentes Atuais*", min_value=0)
            logradouro = st.text_input("Logradouro*")
            col5, col6 = st.columns(2)
            bairro = col5.text_input("Bairro*")
            municipio = col6.text_input("Município*")
            status = st.selectbox("Status", ["Ativo", "Inativo"])
            salvar = st.form_submit_button("Cadastrar ILPI", use_container_width=True)

        if salvar:
            try:
                post("/ilpis/", {
                    "NOMEILPI": nome.upper(),
                    "RESPONSAVELILPI": responsavel.upper(),
                    "TIPOENTIDADE": tipo,
                    "CAPACIDADEIDOSOS": capacidade,
                    "IDOSOSRESIDENTES": residentes,
                    "LOGRADOURO": logradouro.upper(),
                    "BAIRRO": bairro.upper(),
                    "MUNICIPIO": municipio.upper(),
                    "STATUS": status,
                })
                st.success("ILPI cadastrada com sucesso!")
            except Exception as e:
                st.error(f"Erro: {e}")

    with aba[2]:
        codigo = st.number_input("Código da ILPI", min_value=1, step=1)
        if st.button("Carregar"):
            try:
                st.session_state["ilpi_edicao"] = get(f"/ilpis/{codigo}")
            except Exception:
                st.error("ILPI não encontrada.")

        if "ilpi_edicao" in st.session_state:
            i = st.session_state["ilpi_edicao"]
            st.info(f"Editando: **{i['NOMEILPI']}**")
            with st.form("form_atu_ilpi"):
                col1, col2 = st.columns(2)
                capacidade = col1.number_input("Capacidade", value=i.get("CAPACIDADEIDOSOS", 0))
                residentes = col2.number_input("Residentes", value=i.get("IDOSOSRESIDENTES", 0))
                status = st.selectbox("Status", ["Ativo", "Inativo"],
                                      index=0 if i.get("STATUS") == "Ativo" else 1)
                salvar = st.form_submit_button("Salvar", use_container_width=True)
            if salvar:
                try:
                    put(f"/ilpis/{i['CODIGOILPI']}", {
                        "CAPACIDADEIDOSOS": capacidade,
                        "IDOSOSRESIDENTES": residentes,
                        "STATUS": status,
                    })
                    st.success("ILPI atualizada!")
                    del st.session_state["ilpi_edicao"]
                except Exception as e:
                    st.error(f"Erro: {e}")
