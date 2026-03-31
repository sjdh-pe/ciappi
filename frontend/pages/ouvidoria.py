import streamlit as st
import pandas as pd
from api.client import get, put


def show():
    st.title("📣 Ouvidoria")
    aba = st.tabs(["A Vencer", "Vencidas", "SJDH — Ativos", "Concluídas", "Encerrar Ouvidoria"])

    # ── A Vencer ────────────────────────────────────────
    with aba[0]:
        dias = st.number_input("Mostrar prazos nos próximos N dias (0 = todos)", min_value=0, step=5, value=0)
        if st.button("🔍 Buscar A Vencer"):
            try:
                params = {}
                if dias > 0:
                    params["dias"] = dias
                dados = get("/ouvidoria/avencer", params)
                if dados:
                    df = pd.DataFrame(dados)
                    cols = ["TbCasoNumCaso", "tbnomeidoso", "TbPrazoOuvidoria",
                            "TbNumDenuncia", "TbCasoMunicipio", "TbCasoTecnicoResp"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Nº Caso", "Idoso", "Prazo", "Nº Denúncia",
                                  "Município", "Técnico"][:len(df.columns)]
                    st.warning(f"⚠️ {len(df)} caso(s) com prazo a vencer.")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.success("✅ Nenhuma ouvidoria com prazo a vencer.")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── Vencidas ─────────────────────────────────────────
    with aba[1]:
        if st.button("🔍 Buscar Vencidas"):
            try:
                dados = get("/ouvidoria/vencidas")
                if dados:
                    df = pd.DataFrame(dados)
                    cols = ["TbCasoNumCaso", "tbnomeidoso", "TbPrazoOuvidoria",
                            "TbNumDenuncia", "TbCasoMunicipio", "TbCasoTecnicoResp"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Nº Caso", "Idoso", "Prazo Vencido", "Nº Denúncia",
                                  "Município", "Técnico"][:len(df.columns)]
                    st.error(f"🔴 {len(df)} caso(s) com prazo VENCIDO.")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.success("✅ Nenhum prazo vencido.")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── SJDH — Ativos (Frmambiente do Access) ────────────
    with aba[2]:
        st.markdown("Casos da **Ouvidoria SJDH** com origem em *OUvidoria da SJDH* abertos após set/2019.")
        if st.button("🔍 Carregar Casos SJDH"):
            try:
                dados = get("/ouvidoria/ambiente")
                if dados:
                    df = pd.DataFrame(dados)
                    cols = ["TbCasoNumCaso", "tbnomeidoso", "TbCasoDtinicio",
                            "TbNumDenuncia", "TbPrazoOuvidoria", "TbCasoTecnicoResp"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Nº Caso", "Idoso", "Dt. Abertura",
                                  "Nº Denúncia", "Prazo", "Técnico"][:len(df.columns)]
                    st.info(f"{len(df)} caso(s) da Ouvidoria SJDH em aberto.")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.success("Nenhum caso SJDH em aberto.")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── Concluídas ──────────────────────────────────────
    with aba[3]:
        if st.button("🔍 Carregar Concluídas"):
            try:
                dados = get("/ouvidoria/concluidas")
                if dados:
                    df = pd.DataFrame(dados)
                    cols = ["TbCasoNumCaso", "tbnomeidoso",
                            "TbDtEncerradoOuvidoria", "TbNumOfOuvidoria", "TbCasoMunicipio"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Nº Caso", "Idoso", "Dt. Encerramento",
                                  "Nº Ofício", "Município"][:len(df.columns)]
                    st.success(f"{len(df)} ouvidoria(s) concluída(s).")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nenhuma ouvidoria concluída.")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── Encerrar Ouvidoria ──────────────────────────────
    with aba[4]:
        st.markdown("Encerra a ouvidoria de um caso registrando o número do ofício.")
        with st.form("form_encerra_ouvidoria"):
            num_caso  = st.number_input("Nº do Caso*", min_value=1, step=1)
            num_oficio = st.text_input("Nº do Ofício*")
            salvar = st.form_submit_button("📨 Encerrar Ouvidoria", use_container_width=True)

        if salvar:
            if not num_oficio:
                st.error("Informe o número do ofício.")
            else:
                try:
                    put(f"/ouvidoria/{num_caso}/encerrar?num_oficio={num_oficio}", {})
                    st.success(f"✅ Ouvidoria do caso {num_caso} encerrada com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")
