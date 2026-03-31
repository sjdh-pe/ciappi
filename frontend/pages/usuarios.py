import streamlit as st
from api.client import get
from datetime import datetime


def show():
    st.title("👤 Usuários (Idosos Atendidos)")
    aba = st.tabs(["Buscar por Nome", "Detalhe"])

    with aba[0]:
        nome = st.text_input("Nome do Idoso")
        if st.button("Buscar"):
            try:
                dados = get("/usuarios/", {"nome": nome} if nome else {})
                if dados:
                    import pandas as pd
                    df = pd.DataFrame(dados)[[
                        "tbnumerocadastro", "tbnome", "tbcaso",
                        "tbidade", "tbsexo", "tbmunicipio"
                    ]]
                    df.columns = ["Nº Cadastro", "Nome", "Caso", "Idade", "Sexo", "Município"]
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nenhum usuário encontrado.")
            except Exception as e:
                st.error(f"Erro: {e}")

    with aba[1]:
        num = st.number_input("Nº do Cadastro", min_value=1, step=1)
        if st.button("Carregar"):
            try:
                u = get(f"/usuarios/{num}")
                col1, col2 = st.columns(2)
                col1.markdown(f"**Nome:** {u.get('tbnome', '')}")
                col1.markdown(f"**CPF:** {u.get('tbcpf', '')}")
                col1.markdown(f"**Sexo:** {u.get('tbsexo', '')}")
                col1.markdown(f"**Idade:** {u.get('tbidade', '')}")
                col1.markdown(f"**Município:** {u.get('tbmunicipio', '')}")
                col2.markdown(f"**Caso:** {u.get('tbcaso', '')}")
                col2.markdown(f"**Renda:** {u.get('tbfaixarenda', '')}")
                col2.markdown(f"**Deficiência:** {u.get('tbdeficiencia', '')}")
                col2.markdown(f"**Mora com:** {u.get('tbcomquemmora', '')}")
            except Exception as e:
                st.error(f"Erro: {e}")
