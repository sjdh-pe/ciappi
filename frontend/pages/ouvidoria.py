import streamlit as st
import pandas as pd
from api.client import get, put


_COLS_CASO = {
    "TbCasoNumCaso": "Nº Caso",
    "tbnomeidoso":   "Idoso",
    "TbCasoMunicipio": "Município",
    "TbCasoTecnicoResp": "Técnico",
    "TbNumDenuncia": "Nº Denúncia",
    "TbPrazoOuvidoria": "Prazo",
}


def _df_ouvidoria(dados: list, colunas: list[str]) -> pd.DataFrame:
    """Monta DataFrame já renomeado a partir das colunas informadas."""
    df = pd.DataFrame(dados)
    existentes = [c for c in colunas if c in df.columns]
    df = df[existentes].copy()
    df.columns = [_COLS_CASO.get(c, c) for c in existentes]
    for col_data in ["Prazo"]:
        if col_data in df.columns:
            df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    return df


def show():
    st.markdown("""
        <div style="padding:4px 0 16px">
            <h2 style="margin:0;color:#1a3a5c">📣 Ouvidoria</h2>
            <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                Monitoramento e controle de prazos da Ouvidoria da SJDH
            </div>
        </div>
        <hr style="border:none;border-top:2px solid #e0e9f4;margin-bottom:20px">
    """, unsafe_allow_html=True)

    aba = st.tabs(["⏳ A Vencer", "🔴 Vencidas", "📂 SJDH Ativos", "✅ Concluídas", "🔒 Encerrar"])

    # ── A Vencer ──────────────────────────────────────────────────────────────
    with aba[0]:
        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            dias = col1.number_input("Prazos nos próximos N dias (0 = todos)",
                                     min_value=0, step=5, value=30)
            buscar = col2.button("🔍 Buscar", use_container_width=True, type="primary")

        if buscar:
            with st.spinner("Buscando..."):
                try:
                    params = {"dias": dias} if dias > 0 else {}
                    dados  = get("/ouvidoria/avencer", params)
                    if dados:
                        cols = ["TbCasoNumCaso", "tbnomeidoso", "TbPrazoOuvidoria",
                                "TbNumDenuncia", "TbCasoMunicipio", "TbCasoTecnicoResp"]
                        df = _df_ouvidoria(dados, cols)
                        st.warning(f"⚠️ {len(df)} caso(s) com prazo a vencer.")
                        st.dataframe(df, use_container_width=True, hide_index=True,
                                     column_config={"Prazo": st.column_config.DatetimeColumn(
                                         "Prazo", format="DD/MM/YYYY")})
                    else:
                        st.success("✅ Nenhuma ouvidoria com prazo a vencer.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Vencidas ──────────────────────────────────────────────────────────────
    with aba[1]:
        if st.button("🔍 Buscar Vencidas", type="primary"):
            with st.spinner("Buscando..."):
                try:
                    dados = get("/ouvidoria/vencidas")
                    if dados:
                        cols = ["TbCasoNumCaso", "tbnomeidoso", "TbPrazoOuvidoria",
                                "TbNumDenuncia", "TbCasoMunicipio", "TbCasoTecnicoResp"]
                        df = _df_ouvidoria(dados, cols)
                        df.rename(columns={"Prazo": "Prazo Vencido"}, inplace=True)
                        st.error(f"🔴 {len(df)} caso(s) com prazo VENCIDO. Atenção imediata necessária!")
                        st.dataframe(df, use_container_width=True, hide_index=True,
                                     column_config={"Prazo Vencido": st.column_config.DatetimeColumn(
                                         "Prazo Vencido", format="DD/MM/YYYY")})
                    else:
                        st.success("✅ Nenhum prazo vencido.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── SJDH Ativos ───────────────────────────────────────────────────────────
    with aba[2]:
        st.markdown(
            '<div class="info-card">📋 Casos da <strong>Ouvidoria SJDH</strong> com origem em '
            '<em>OUvidoria da SJDH</em> em aberto após set/2019 (reproduz Frmambiente do Access).</div>',
            unsafe_allow_html=True
        )
        if st.button("🔍 Carregar Casos SJDH", type="primary"):
            with st.spinner("Carregando..."):
                try:
                    dados = get("/ouvidoria/ambiente")
                    if dados:
                        cols = ["TbCasoNumCaso", "tbnomeidoso", "TbCasoDtinicio",
                                "TbNumDenuncia", "TbPrazoOuvidoria", "TbCasoTecnicoResp"]
                        df = _df_ouvidoria(dados, cols)
                        if "Dt. Início" not in df.columns and "TbCasoDtinicio" in pd.DataFrame(dados).columns:
                            # rename manually since _COLS_CASO doesn't have TbCasoDtinicio
                            df = pd.DataFrame(dados)[cols].copy()
                            df.columns = ["Nº Caso", "Idoso", "Dt. Abertura",
                                          "Nº Denúncia", "Prazo", "Técnico"][:len(cols)]
                            for c in ["Dt. Abertura", "Prazo"]:
                                if c in df.columns:
                                    df[c] = pd.to_datetime(df[c], errors="coerce")
                        st.info(f"📁 {len(df)} caso(s) da Ouvidoria SJDH em aberto.")
                        st.dataframe(df, use_container_width=True, hide_index=True,
                                     column_config={
                                         "Dt. Abertura": st.column_config.DatetimeColumn("Dt. Abertura", format="DD/MM/YYYY"),
                                         "Prazo": st.column_config.DatetimeColumn("Prazo", format="DD/MM/YYYY"),
                                     })
                    else:
                        st.success("Nenhum caso SJDH em aberto.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Concluídas ────────────────────────────────────────────────────────────
    with aba[3]:
        if st.button("🔍 Carregar Concluídas", type="primary"):
            with st.spinner("Carregando..."):
                try:
                    dados = get("/ouvidoria/concluidas")
                    if dados:
                        df = pd.DataFrame(dados)
                        cols_r = ["TbCasoNumCaso", "tbnomeidoso",
                                  "TbDtEncerradoOuvidoria", "TbNumOfOuvidoria", "TbCasoMunicipio"]
                        df = df[[c for c in cols_r if c in df.columns]].copy()
                        df.columns = ["Nº Caso", "Idoso", "Dt. Encerramento",
                                      "Nº Ofício", "Município"][:len(df.columns)]
                        for c in ["Dt. Encerramento"]:
                            if c in df.columns:
                                df[c] = pd.to_datetime(df[c], errors="coerce")
                        st.success(f"✅ {len(df)} ouvidoria(s) concluída(s).")
                        st.dataframe(df, use_container_width=True, hide_index=True,
                                     column_config={"Dt. Encerramento": st.column_config.DatetimeColumn(
                                         "Dt. Encerramento", format="DD/MM/YYYY")})
                    else:
                        st.info("Nenhuma ouvidoria concluída.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Encerrar Ouvidoria ────────────────────────────────────────────────────
    with aba[4]:
        st.markdown(
            '<div class="warn-card">⚠️ Esta ação encerra formalmente a ouvidoria de um caso, '
            'registrando o número do ofício de resposta.</div>',
            unsafe_allow_html=True
        )
        with st.container(border=True):
            with st.form("form_encerra_ouvidoria"):
                col1, col2 = st.columns(2)
                num_caso   = col1.number_input("Nº do Caso *", min_value=1, step=1)
                num_oficio = col2.text_input("Nº do Ofício *", placeholder="Ex: OF-2025-001")
                salvar = st.form_submit_button("📨 Encerrar Ouvidoria", use_container_width=True, type="primary")

        if salvar:
            if not num_oficio:
                st.error("⚠️ Informe o número do ofício.")
            else:
                with st.spinner("Encerrando ouvidoria..."):
                    try:
                        put(f"/ouvidoria/{num_caso}/encerrar?num_oficio={num_oficio}", {})
                        st.success(f"✅ Ouvidoria do caso {num_caso} encerrada. Ofício: {num_oficio}")
                    except Exception as e:
                        st.error(f"Erro: {e}")
