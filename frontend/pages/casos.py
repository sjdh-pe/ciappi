import streamlit as st
import pandas as pd
from api.client import get, post, put
from datetime import datetime
from components.styles import card_section
from components.listas import (
    municipios, tecnicos as _tecnicos_lista,
    motivos_atendimento as _motivos_lista,
    origens as _origens_lista,
)


def _badge_status(enc: bool) -> str:
    if enc:
        return '<span style="background:#f8d7da;color:#721c24;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">🔴 Encerrado</span>'
    return '<span style="background:#d4edda;color:#155724;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">🟢 Ativo</span>'


def show():
    _header("📁 Casos", "Gestão de casos de proteção ao idoso")

    aba = st.tabs(["🔍 Buscar / Listar", "➕ Novo Caso", "✏️ Atualizar / Encerrar", "🔄 Restaurar"])

    # ── Buscar ──────────────────────────────────────────────────────────────────
    with aba[0]:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            opts_mun  = ["(Todos)"] + municipios()
            municipio_sel = col1.selectbox("Município", opts_mun, key="busca_mun")
            municipio = "" if municipio_sel == "(Todos)" else municipio_sel
            tecnico   = col2.text_input("Técnico", placeholder="Nome do técnico")

            col3, col4 = st.columns(2)
            opts_vio  = ["(Todos)"] + _motivos_lista()
            vio_sel   = col3.selectbox("Tipo de Violência", opts_vio, key="busca_vio")
            encerrado = col4.selectbox("Status", ["Todos", "Ativos", "Encerrados"])
            buscar = st.button("🔍 Buscar Casos", use_container_width=True, type="primary")

        if buscar:
            params = {}
            if municipio: params["municipio"] = municipio
            if tecnico:   params["tecnico"]   = tecnico
            if vio_sel != "(Todos)": params["motivo"] = vio_sel
            if encerrado == "Ativos":       params["encerrado"] = "Não"
            elif encerrado == "Encerrados": params["encerrado"] = "Sim"

            with st.spinner("Buscando casos..."):
                try:
                    casos = get("/casos/", params)
                    if casos:
                        df = pd.DataFrame(casos)
                        cols = ["TbCasoNumCaso", "tbnomeidoso", "TbCasoMunicipio",
                                "TbCasoDtinicio", "TbCasoEncerrado",
                                "TbCasoTecnicoResp", "TbCasoMotivoAtendimento"]
                        df = df[[c for c in cols if c in df.columns]].copy()
                        df.columns = ["Nº", "Idoso", "Município", "Dt. Início",
                                      "Encerrado", "Técnico", "Tipo de Violência"][:len(df.columns)]

                        # Formata datas
                        for col_data in ["Dt. Início"]:
                            if col_data in df.columns:
                                df[col_data] = pd.to_datetime(df[col_data], errors="coerce")

                        st.success(f"✅ {len(df)} caso(s) encontrado(s).")
                        st.dataframe(
                            df, use_container_width=True, hide_index=True,
                            column_config={
                                "Nº": st.column_config.NumberColumn("Nº", format="%d", width="small"),
                                "Idoso": st.column_config.TextColumn("Idoso", width="large"),
                                "Município": st.column_config.TextColumn("Município"),
                                "Dt. Início": st.column_config.DatetimeColumn(
                                    "Dt. Início", format="DD/MM/YYYY"),
                                "Encerrado": st.column_config.TextColumn("Status", width="small"),
                                "Técnico": st.column_config.TextColumn("Técnico"),
                                "Tipo de Violência": st.column_config.TextColumn("Tipo de Violência"),
                            }
                        )
                    else:
                        st.info("Nenhum caso encontrado com os filtros aplicados.")
                except Exception as e:
                    st.error(f"Erro ao buscar: {e}")

    # ── Novo Caso ───────────────────────────────────────────────────────────────
    with aba[1]:
        with st.container(border=True):
            card_section("Identificação")
            col1, col2 = st.columns(2)
            num_caso   = col1.number_input("Nº do Caso *", min_value=1, step=1)
            dt_inicio  = col2.date_input("Data de Início *")
            nome_idoso = st.text_input("Nome do Idoso *", placeholder="Nome completo")

            card_section("Localização e Responsável")
            col3, col4 = st.columns(2)
            opts_mun_new = municipios()
            municipio_novo = col3.selectbox("Município *", [""] + opts_mun_new, key="novo_caso_mun")
            opts_tec = _tecnicos_lista()
            tecnico_novo = (col4.selectbox("Técnico Responsável *", opts_tec)
                            if opts_tec else col4.text_input("Técnico Responsável *"))

            card_section("Classificação")
            col5, col6 = st.columns(2)
            opts_motivo = _motivos_lista()
            motivo  = col5.selectbox("Tipo de Violência *", [""] + opts_motivo, key="novo_caso_vio")
            opts_origem = _origens_lista()
            origem  = col6.selectbox("Como Chegou ao Programa *", opts_origem)
            ambiente = st.selectbox("Ambiente de Violência *", ["Intrafamiliar", "Extrafamiliar"])

            card_section("Relato")
            relato = st.text_area("Síntese do Caso *", height=130,
                                  placeholder="Descreva a situação do caso...")

            salvar = st.button("💾 Salvar Caso", use_container_width=True, type="primary")

        if salvar:
            if not all([nome_idoso, municipio_novo, motivo, origem, relato]):
                st.error("⚠️ Todos os campos obrigatórios (*) devem ser preenchidos.")
            else:
                with st.spinner("Salvando..."):
                    try:
                        post("/casos/", {
                            "TbCasoNumCaso":            num_caso,
                            "TbCasoDtinicio":           str(datetime.combine(dt_inicio, datetime.min.time())),
                            "tbnomeidoso":              nome_idoso.upper(),
                            "TbCasoMotivoAtendimento":  motivo,
                            "TbCasoChegouPrograma":     origem,
                            "Tbambienteviolencia":      ambiente,
                            "TbCasoRelato":             relato,
                            "TbCasoMunicipio":          municipio_novo.upper(),
                            "TbCasoTecnicoResp":        tecnico_novo.upper() if tecnico_novo else "",
                        })
                        st.success(f"✅ Caso {num_caso} registrado com sucesso!")
                        _tecnicos_lista.clear()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

    # ── Atualizar / Encerrar ─────────────────────────────────────────────────
    with aba[2]:
        with st.container(border=True):
            col_n, col_b, col_l = st.columns([2, 1, 1])
            num_busca = col_n.number_input("Nº do Caso", min_value=1, step=1, key="busca_atu",
                                           label_visibility="collapsed")
            if col_b.button("📂 Carregar", use_container_width=True):
                with st.spinner("Carregando..."):
                    try:
                        caso = get(f"/casos/{num_busca}")
                        st.session_state["caso_edicao"] = caso
                    except Exception:
                        st.error("Caso não encontrado.")
            if col_l.button("✕ Limpar", use_container_width=True):
                st.session_state.pop("caso_edicao", None)
                st.rerun()

        if "caso_edicao" in st.session_state:
            c   = st.session_state["caso_edicao"]
            enc = c.get("TbCasoEncerrado") == "Sim"

            st.markdown(
                f"""<div style="background:#f8fbff;border:1px solid #cfe2ff;border-radius:10px;
                     padding:14px 18px;margin:12px 0">
                    <strong style="font-size:16px">{c['tbnomeidoso']}</strong>
                    &nbsp;&nbsp;{_badge_status(enc)}
                    <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                        Caso nº {c['TbCasoNumCaso']} · {c.get('TbCasoMunicipio','')} ·
                        Técnico: {c.get('TbCasoTecnicoResp','')}
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

            with st.form("form_atu_caso"):
                card_section("📝 Relato")
                relato_atu = st.text_area("Síntese do Caso", value=c.get("TbCasoRelato", ""), height=110)
                obs = st.text_area("Observações", value=c.get("TbObservacoes") or "", height=70)

                col_enc, col_ouv = st.columns(2)

                with col_enc:
                    card_section("🔒 Encerramento")
                    dt_encer = st.date_input("Data de Encerramento", value=None, key="dt_enc_form")
                    try:
                        mot_enc = get("/tabelas/motivos-encerramento")
                        opts_enc = {"(manter aberto)": None,
                                    **{m["descricaomotivo"]: m["Código"] for m in mot_enc}}
                    except Exception:
                        opts_enc = {"(sem dados)": None}
                    motivo_enc = st.selectbox("Motivo de Encerramento", list(opts_enc.keys()))

                with col_ouv:
                    card_section("📣 Ouvidoria")
                    prazo_ouv    = st.date_input("Prazo Ouvidoria", value=None, key="prazo_ouv_form")
                    num_denuncia = st.number_input("Nº da Denúncia", min_value=0, step=1,
                                                   value=int(c.get("TbNumDenuncia") or 0))

                salvar_atu = st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary")

            if salvar_atu:
                dados = {"TbCasoRelato": relato_atu}
                if obs:          dados["TbObservacoes"] = obs
                if dt_encer:     dados["TbCasoDtencer"] = str(datetime.combine(dt_encer, datetime.min.time()))
                cod_enc = opts_enc.get(motivo_enc)
                if cod_enc:      dados["TbCasoMotivoEncerramento"] = cod_enc
                if prazo_ouv:    dados["TbPrazoOuvidoria"] = str(datetime.combine(prazo_ouv, datetime.min.time()))
                if num_denuncia: dados["TbNumDenuncia"] = num_denuncia
                with st.spinner("Salvando..."):
                    try:
                        put(f"/casos/{c['TbCasoNumCaso']}", dados)
                        st.success("✅ Alterações salvas com sucesso!")
                        del st.session_state["caso_edicao"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

    # ── Restaurar Caso ───────────────────────────────────────────────────────
    with aba[3]:
        st.markdown(
            '<div class="info-card">♻️ Restaura um caso encerrado, limpando data e motivo de encerramento.</div>',
            unsafe_allow_html=True
        )
        with st.container(border=True):
            col_n2, col_v = st.columns([2, 1])
            num_rest = col_n2.number_input("Nº do Caso a Restaurar", min_value=1, step=1,
                                           label_visibility="collapsed")
            if col_v.button("📂 Verificar", use_container_width=True):
                with st.spinner("Verificando..."):
                    try:
                        caso = get(f"/casos/{num_rest}")
                        if caso.get("TbCasoEncerrado") == "Sim":
                            st.session_state["caso_restaurar"] = caso
                        else:
                            st.info("ℹ️ Este caso não está encerrado.")
                            st.session_state.pop("caso_restaurar", None)
                    except Exception:
                        st.error("Caso não encontrado.")

        if "caso_restaurar" in st.session_state:
            c = st.session_state["caso_restaurar"]
            st.markdown(
                f'<div class="warn-card">⚠️ Caso <strong>{c["tbnomeidoso"]}</strong> '
                f'(nº {c["TbCasoNumCaso"]}) está ENCERRADO. Selecione o motivo de restauração.</div>',
                unsafe_allow_html=True
            )
            with st.form("form_restaurar"):
                try:
                    mot_rest = get("/tabelas/motivos-restauracao")
                    opts_rest = {m["DescricaoRestauracao"]: m["Código"] for m in mot_rest}
                except Exception:
                    opts_rest = {"Retorno espontâneo": 1}
                motivo_rest = st.selectbox("Motivo de Restauração *", list(opts_rest.keys()))
                restaurar = st.form_submit_button("🔄 Restaurar Caso", use_container_width=True, type="primary")

            if restaurar:
                with st.spinner("Restaurando..."):
                    try:
                        put(f"/casos/{c['TbCasoNumCaso']}/restaurar",
                            {"motivo_restauracao": opts_rest[motivo_rest]})
                        st.success(f"✅ Caso {c['TbCasoNumCaso']} restaurado com sucesso!")
                        del st.session_state["caso_restaurar"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
