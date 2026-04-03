import streamlit as st
import pandas as pd
import plotly.express as px
from api.client import get
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"


def _periodo_cols(key_prefix):
    col1, col2 = st.columns(2)
    dt_ini = col1.date_input("De", value=datetime.today() - timedelta(days=365), key=f"{key_prefix}_ini")
    dt_fim = col2.date_input("Até", value=datetime.today(), key=f"{key_prefix}_fim")
    return dt_ini, dt_fim


def _csv_link(endpoint: str, label: str, params: dict = None):
    """Botão de download CSV (acessa o endpoint /csv/* diretamente)."""
    import requests, streamlit as st
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if st.button(f"⬇️ Download CSV — {label}"):
        try:
            r = requests.get(f"{API_BASE}{endpoint}", headers=headers,
                             params=params, timeout=30)
            r.raise_for_status()
            st.download_button(
                label=f"Baixar {label}.csv",
                data=r.content,
                file_name=f"{label}.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Erro ao gerar CSV: {e}")


def show():
    st.markdown("""
        <div style="padding:4px 0 16px">
            <h2 style="margin:0;color:#1a3a5c">📊 Relatórios</h2>
            <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                Indicadores e análises do programa
            </div>
        </div>
        <hr style="border:none;border-top:2px solid #e0e9f4;margin-bottom:20px">
    """, unsafe_allow_html=True)

    aba = st.tabs([
        "Casos Ativos", "Casos Parados", "Encerrados",
        "Resolutividade", "Por Município", "Tipo de Violência",
        "Origem", "Acompanhamentos", "Por Técnico",
        "Encaminhamentos", "Perfil", "Eventos", "Visitas"
    ])

    # ── 0. Casos Ativos ──────────────────────────────────
    with aba[0]:
        if st.button("🔍 Gerar", key="ativos"):
            try:
                dados = get("/relatorios/casos-ativos")
                total = dados.get("total", 0)
                casos = dados.get("casos", [])
                st.metric("Total de Casos Ativos", total)
                if casos:
                    df = pd.DataFrame(casos)
                    cols = ["TbCasoNumCaso", "tbnomeidoso", "TbCasoMunicipio",
                            "TbCasoTecnicoResp", "ultima_acao", "ultima_data_acomp"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Nº Caso", "Idoso", "Município", "Técnico",
                                  "Última Ação", "Data Último Acomp."][:len(df.columns)]
                    st.dataframe(df, use_container_width=True)
                    _csv_link("/relatorios/csv/casos-ativos", "casos_ativos")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 1. Casos Parados ─────────────────────────────────
    with aba[1]:
        dias = st.number_input("Casos sem acompanhamento há pelo menos N dias",
                                min_value=1, value=30, step=5)
        if st.button("🔍 Gerar", key="parados"):
            try:
                dados = get("/relatorios/casos-parados", {"dias": dias})
                total = dados.get("total", 0)
                casos = dados.get("casos", [])
                st.metric(f"Casos Parados (≥ {dias} dias)", total)
                if casos:
                    df = pd.DataFrame(casos)
                    cols = ["TbCasoNumCaso", "tbnomeidoso", "TbCasoMunicipio",
                            "TbCasoTecnicoResp", "ultima_data_acomp", "dias_sem_acomp"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Nº Caso", "Idoso", "Município", "Técnico",
                                  "Último Acomp.", "Dias Parado"][:len(df.columns)]
                    st.dataframe(df, use_container_width=True)
                    _csv_link("/relatorios/csv/casos-parados", "casos_parados", {"dias": dias})
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 2. Encerrados ────────────────────────────────────
    with aba[2]:
        dt_ini, dt_fim = _periodo_cols("enc")
        if st.button("🔍 Gerar", key="enc"):
            try:
                dados = get("/relatorios/encerrados", {
                    "dt_ini": dt_ini.isoformat(), "dt_fim": dt_fim.isoformat()
                })
                st.metric("Casos Encerrados no Período", len(dados))
                if dados:
                    df = pd.DataFrame(dados)
                    cols = ["TbCasoNumCaso", "tbnomeidoso", "TbCasoMunicipio",
                            "TbCasoDtencer", "TbCasoTecnicoResp"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Nº Caso", "Idoso", "Município",
                                  "Dt. Encerramento", "Técnico"][:len(df.columns)]
                    st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 3. Resolutividade ────────────────────────────────
    with aba[3]:
        dt_ini, dt_fim = _periodo_cols("resol")
        if st.button("🔍 Gerar", key="resol"):
            try:
                dados = get("/relatorios/encerrados-resolutividade", {
                    "dt_ini": dt_ini.isoformat(), "dt_fim": dt_fim.isoformat()
                })
                resumo = dados.get("resumo_por_motivo", [])
                casos  = dados.get("casos", [])
                if resumo:
                    df_r = pd.DataFrame(resumo)
                    fig = px.pie(df_r, names="motivo_encerramento", values="total",
                                 title="Encerrados por Motivo (Resolutividade)")
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df_r, use_container_width=True)
                if casos:
                    st.subheader("Detalhe dos Casos")
                    st.dataframe(pd.DataFrame(casos), use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 4. Por Município ─────────────────────────────────
    with aba[4]:
        if st.button("🔍 Gerar", key="mun"):
            try:
                dados = get("/relatorios/municipio")
                if dados:
                    # API retorna [{"municipio": ..., "total": ...}] — renomear para exibição
                    df = pd.DataFrame(dados).rename(columns={"municipio": "Município", "total": "Total"})
                    fig = px.bar(df, x="Município", y="Total", title="Casos por Município")
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df, use_container_width=True)
                    _csv_link("/relatorios/csv/municipio", "municipios")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 5. Tipo de Violência ─────────────────────────────
    with aba[5]:
        dt_ini, dt_fim = _periodo_cols("vio")
        col_mun = st.text_input("Filtrar por Município (violência por bairro)", key="vio_mun")
        if st.button("🔍 Gerar", key="vio"):
            try:
                # Por tipo (pizza)
                # API retorna [{"tipo_violencia": ..., "total": ...}]
                dados_tipo = get("/relatorios/violencia", {
                    "dt_ini": dt_ini.isoformat(), "dt_fim": dt_fim.isoformat()
                })
                if dados_tipo:
                    df_t = pd.DataFrame(dados_tipo).rename(
                        columns={"tipo_violencia": "Tipo", "total": "Total"}
                    )
                    fig = px.pie(df_t, names="Tipo", values="Total", title="Tipos de Violência")
                    st.plotly_chart(fig, use_container_width=True)
                    _csv_link("/relatorios/csv/violencia", "violencia",
                              {"dt_ini": dt_ini.isoformat(), "dt_fim": dt_fim.isoformat()})

                # Por bairro (se filtrou município)
                # API retorna [{"bairro": ..., "municipio": ..., "total": ...}]
                params_bairro = {"dt_ini": dt_ini.isoformat(), "dt_fim": dt_fim.isoformat()}
                if col_mun:
                    params_bairro["municipio"] = col_mun
                dados_bairro = get("/relatorios/violencia-bairro", params_bairro)
                if dados_bairro:
                    st.subheader("Violência por Bairro")
                    df_b = pd.DataFrame(dados_bairro).rename(
                        columns={"bairro": "Bairro", "municipio": "Município", "total": "Total"}
                    )
                    fig2 = px.bar(df_b, x="Bairro", y="Total",
                                  title="Casos por Bairro de Residência")
                    st.plotly_chart(fig2, use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 6. Origem ────────────────────────────────────────
    with aba[6]:
        if st.button("🔍 Gerar", key="ori"):
            try:
                # API retorna [{"origem": ..., "total": ...}]
                dados = get("/relatorios/origem")
                if dados:
                    df = pd.DataFrame(dados).rename(columns={"origem": "Origem", "total": "Total"})
                    fig = px.bar(df, x="Origem", y="Total", title="Como Chegou ao Programa")
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 7. Acompanhamentos ───────────────────────────────
    with aba[7]:
        dt_ini, dt_fim = _periodo_cols("acomp")
        if st.button("🔍 Gerar", key="acomp"):
            try:
                dados = get("/relatorios/acompanhamentos", {
                    "dt_ini": dt_ini.isoformat(), "dt_fim": dt_fim.isoformat()
                })
                total = dados.get("total", 0)
                st.metric("Total de Acompanhamentos", total)

                col1, col2 = st.columns(2)
                por_carater = dados.get("por_carater", [])
                if por_carater:
                    df_c = pd.DataFrame(por_carater)
                    fig = px.pie(df_c, names="carater", values="total",
                                 title="Por Caráter de Atendimento")
                    col1.plotly_chart(fig, use_container_width=True)

                por_acao = dados.get("por_acao", [])
                if por_acao:
                    df_a = pd.DataFrame(por_acao)
                    fig2 = px.bar(df_a, x="acao", y="total", title="Por Tipo de Ação")
                    col2.plotly_chart(fig2, use_container_width=True)

                registros = dados.get("registros", [])
                if registros:
                    with st.expander("Ver lista completa"):
                        df_r = pd.DataFrame(registros)
                        cols = ["tbcodigo", "TbAcomCaso", "TbAcompdata",
                                "TbAcompAcao", "TbTecnicoResponsavel"]
                        df_r = df_r[[c for c in cols if c in df_r.columns]]
                        df_r.columns = ["Código", "Caso", "Data", "Ação", "Técnico"][:len(df_r.columns)]
                        st.dataframe(df_r, use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 8. Por Técnico ───────────────────────────────────
    with aba[8]:
        dt_ini, dt_fim = _periodo_cols("tec")
        try:
            tecnicos = get("/tabelas/tecnicos")
            opts_tec = [t["TbNomeTecnico"] for t in tecnicos]
        except Exception:
            opts_tec = []
        tecnico_sel = (st.selectbox("Técnico", opts_tec, key="tec_sel")
                       if opts_tec else st.text_input("Técnico", key="tec_sel"))
        if st.button("🔍 Gerar", key="tec"):
            try:
                dados = get("/relatorios/acomp-por-tecnico", {
                    "tecnico": tecnico_sel,
                    "dt_ini": dt_ini.isoformat(),
                    "dt_fim": dt_fim.isoformat(),
                })
                st.metric(f"Total de Acompanhamentos — {tecnico_sel}", dados.get("total", 0))
                por_acao = dados.get("por_acao", [])
                if por_acao:
                    df_a = pd.DataFrame(por_acao)
                    fig = px.bar(df_a, x="acao", y="total", title="Por Tipo de Ação")
                    st.plotly_chart(fig, use_container_width=True)
                registros = dados.get("registros", [])
                if registros:
                    with st.expander("Ver registros"):
                        df_r = pd.DataFrame(registros)
                        cols = ["tbcodigo", "TbAcomCaso", "TbAcompdata", "TbAcompAcao"]
                        df_r = df_r[[c for c in cols if c in df_r.columns]]
                        st.dataframe(df_r, use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 9. Encaminhamentos ───────────────────────────────
    with aba[9]:
        dt_ini, dt_fim = _periodo_cols("enc2")
        if st.button("🔍 Gerar", key="enc2"):
            try:
                dados = get("/relatorios/encaminhamentos", {
                    "dt_ini": dt_ini.isoformat(), "dt_fim": dt_fim.isoformat()
                })
                st.metric("Encaminhamentos no Período", len(dados))
                if dados:
                    df = pd.DataFrame(dados)
                    st.dataframe(df, use_container_width=True)
                    _csv_link("/relatorios/csv/encaminhamentos", "encaminhamentos",
                              {"dt_ini": dt_ini.isoformat(), "dt_fim": dt_fim.isoformat()})
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 10. Perfil dos Atendidos ─────────────────────────
    with aba[10]:
        if st.button("🔍 Gerar Perfil", key="perfil"):
            try:
                col1, col2 = st.columns(2)

                # Todos os endpoints de perfil retornam [{"<campo>": ..., "total": ...}]
                # — precisam de rename pois pd.DataFrame(data, columns=[...]) seleciona
                #   por nome de chave, não renomeia
                esc = get("/relatorios/perfil/escolaridade")
                if esc:
                    df_e = pd.DataFrame(esc).rename(columns={"escolaridade": "Escolaridade", "total": "Total"})
                    fig = px.bar(df_e, x="Escolaridade", y="Total", title="Escolaridade")
                    col1.plotly_chart(fig, use_container_width=True)

                fet = get("/relatorios/perfil/faixa-etaria")
                if fet:
                    df_f = pd.DataFrame(fet).rename(columns={"faixa_etaria": "Faixa Etária", "total": "Total"})
                    fig2 = px.pie(df_f, names="Faixa Etária", values="Total", title="Faixa Etária")
                    col2.plotly_chart(fig2, use_container_width=True)

                col3, col4 = st.columns(2)

                sexo = get("/relatorios/perfil/sexo")
                if sexo:
                    df_s = pd.DataFrame(sexo).rename(columns={"sexo": "Sexo", "total": "Total"})
                    fig3 = px.pie(df_s, names="Sexo", values="Total", title="Sexo")
                    col3.plotly_chart(fig3, use_container_width=True)

                renda = get("/relatorios/perfil/renda")
                if renda:
                    df_r = pd.DataFrame(renda).rename(columns={"faixa_renda": "Faixa de Renda", "total": "Total"})
                    fig4 = px.bar(df_r, x="Faixa de Renda", y="Total", title="Faixa de Renda")
                    col4.plotly_chart(fig4, use_container_width=True)

                raca = get("/relatorios/perfil/raca-cor")
                if raca:
                    df_rc = pd.DataFrame(raca).rename(columns={"raca_cor": "Raça/Cor", "total": "Total"})
                    fig5 = px.bar(df_rc, x="Raça/Cor", y="Total", title="Raça/Cor")
                    st.plotly_chart(fig5, use_container_width=True)

            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 11. Eventos ──────────────────────────────────────
    with aba[11]:
        dt_ini, dt_fim = _periodo_cols("ev")
        if st.button("🔍 Gerar", key="ev"):
            try:
                dados = get("/relatorios/eventos", {
                    "dt_ini": dt_ini.isoformat(), "dt_fim": dt_fim.isoformat()
                })
                st.metric("Total de Eventos", len(dados))
                if dados:
                    df = pd.DataFrame(dados)
                    cols = ["Codigo", "tbnomeevento", "tbtipoevento",
                            "TbDataRealizacao", "TbMunicipioevento", "TbPublicoPresente"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Código", "Evento", "Tipo", "Data",
                                  "Município", "Público"][:len(df.columns)]
                    st.dataframe(df, use_container_width=True)

                # API retorna [{"municipio": ..., "total": ...}]
                mun = get("/relatorios/eventos-por-municipio")
                if mun:
                    df_m = pd.DataFrame(mun).rename(columns={"municipio": "Município", "total": "Total"})
                    fig = px.bar(df_m, x="Município", y="Total", title="Eventos por Município")
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── 12. Visitas ──────────────────────────────────────
    with aba[12]:
        dt_ini, dt_fim = _periodo_cols("vis")
        tipo_vis = st.radio("Tipo de Visita", ["ILPIs", "Institucionais"])
        if st.button("🔍 Gerar", key="vis"):
            try:
                params = {"dt_ini": dt_ini.isoformat(), "dt_fim": dt_fim.isoformat()}
                endpoint = "/relatorios/visitas-ilpi" if tipo_vis == "ILPIs" else "/relatorios/visitas-inst"
                dados = get(endpoint, params)
                st.metric("Total de Visitas", len(dados))
                if dados:
                    st.dataframe(pd.DataFrame(dados), use_container_width=True)
            except Exception as e:
                st.error(f"Erro: {e}")
