import streamlit as st
import pandas as pd
from api.client import get, post, put
from datetime import datetime
from components.styles import card_section
from components.listas import tecnicos as _tecnicos_lista, tipos_acao as _tipos_acao_lista


def _status_color(status: str) -> str:
    mapa = {
        "Concluído": "#d4edda", "Pendente": "#fff3cd", "Em andamento": "#cfe2ff"
    }
    return mapa.get(status, "#f0f0f0")


def show():
    st.markdown("""
        <div style="padding:4px 0 16px">
            <h2 style="margin:0;color:#1a3a5c">📋 Acompanhamentos</h2>
            <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                Registro de ações e acompanhamentos por caso
            </div>
        </div>
        <hr style="border:none;border-top:2px solid #e0e9f4;margin-bottom:20px">
    """, unsafe_allow_html=True)

    aba = st.tabs(["🔍 Ver por Caso", "➕ Novo Acompanhamento", "✏️ Editar"])

    # ── Ver por Caso ─────────────────────────────────────────────────────────
    with aba[0]:
        with st.container(border=True):
            col_n, col_b = st.columns([2, 1])
            num_caso = col_n.number_input("Número do Caso", min_value=1, step=1,
                                          label_visibility="collapsed", placeholder="Nº do Caso")
            buscar = col_b.button("🔍 Buscar", use_container_width=True, type="primary")

        if buscar:
            with st.spinner("Carregando acompanhamentos..."):
                try:
                    # Dados do caso
                    try:
                        caso = get(f"/casos/{num_caso}")
                        enc = caso.get("TbCasoEncerrado") == "Sim"
                        badge = ('<span style="background:#f8d7da;color:#721c24;padding:2px 8px;'
                                 'border-radius:12px;font-size:12px">🔴 Encerrado</span>'
                                 if enc else
                                 '<span style="background:#d4edda;color:#155724;padding:2px 8px;'
                                 'border-radius:12px;font-size:12px">🟢 Ativo</span>')
                        st.markdown(
                            f"""<div style="background:#f8fbff;border:1px solid #cfe2ff;
                                border-radius:10px;padding:12px 18px;margin:8px 0">
                                <strong>{caso['tbnomeidoso']}</strong> &nbsp; {badge}
                                <span style="color:#6b7c93;font-size:13px;margin-left:12px">
                                    Técnico: {caso.get('TbCasoTecnicoResp','')}
                                </span>
                            </div>""",
                            unsafe_allow_html=True
                        )
                    except Exception:
                        pass

                    acomps = get(f"/acompanhamentos/caso/{num_caso}")
                    if acomps:
                        df = pd.DataFrame(acomps)
                        cols_disp = ["tbcodigo", "TbAcompdata", "TbAcompAcao",
                                     "TbCaraterAtendimento", "TbTecnicoResponsavel",
                                     "TbAcompStatus", "TbAcompPrazo"]
                        df = df[[c for c in cols_disp if c in df.columns]].copy()
                        df.columns = ["Código", "Data", "Ação", "Caráter",
                                      "Técnico", "Status", "Prazo"][:len(df.columns)]

                        for col_data in ["Data", "Prazo"]:
                            if col_data in df.columns:
                                df[col_data] = pd.to_datetime(df[col_data], errors="coerce")

                        st.success(f"✅ {len(df)} acompanhamento(s) encontrado(s).")
                        st.dataframe(
                            df, use_container_width=True, hide_index=True,
                            column_config={
                                "Código": st.column_config.NumberColumn("Cód.", format="%d", width="small"),
                                "Data": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY"),
                                "Ação": st.column_config.TextColumn("Ação", width="medium"),
                                "Caráter": st.column_config.TextColumn("Caráter", width="small"),
                                "Técnico": st.column_config.TextColumn("Técnico"),
                                "Status": st.column_config.TextColumn("Status", width="small"),
                                "Prazo": st.column_config.DatetimeColumn("Prazo", format="DD/MM/YYYY"),
                            }
                        )

                        with st.expander("📄 Ver relatos completos"):
                            for a in acomps:
                                dt  = (a.get("TbAcompdata") or "")[:10]
                                sts = a.get("TbAcompStatus") or ""
                                sts_color = _status_color(sts)
                                st.markdown(
                                    f"""<div style="border:1px solid #e0e9f4;border-radius:8px;
                                        padding:12px 16px;margin-bottom:10px">
                                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                                            <strong>{dt}</strong>
                                            <span style="background:#f0f5fb;padding:2px 8px;border-radius:12px;font-size:12px">
                                                {a.get('TbAcompAcao','')}</span>
                                            <span style="background:{sts_color};padding:2px 8px;border-radius:12px;font-size:12px">
                                                {sts or 'Sem status'}</span>
                                            <span style="color:#6b7c93;font-size:12px">
                                                👤 {a.get('TbTecnicoResponsavel','')}</span>
                                        </div>
                                        {"<div style='font-size:12px;color:#6b7c93;margin-bottom:6px'>📌 Órgão: " + a['TbAcompOrgao'] + "</div>" if a.get('TbAcompOrgao') else ""}
                                        {"<div style='font-size:12px;color:#6b7c93;margin-bottom:6px'>⏰ Prazo: " + (a.get('TbAcompPrazo') or '')[:10] + "</div>" if a.get('TbAcompPrazo') else ""}
                                    </div>""",
                                    unsafe_allow_html=True
                                )
                                st.text(a.get("TbRelato", ""))
                    else:
                        st.info("Nenhum acompanhamento registrado para este caso.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Novo Acompanhamento ──────────────────────────────────────────────────
    with aba[1]:
        with st.container(border=True):
            card_section("Vínculo e Data")
            col1, col2 = st.columns(2)
            num_caso_inc = col1.number_input("Nº do Caso *", min_value=1, step=1)
            data_acomp   = col2.date_input("Data da Ação *")

            card_section("Classificação da Ação")
            col3, col4 = st.columns(2)
            opts_tipo = _tipos_acao_lista()
            tipo_acao = col3.selectbox("Tipo de Ação *", opts_tipo)
            carater   = col4.selectbox("Caráter do Atendimento *", ["Social", "Jurídico", "Psicológico"])

            orgao = st.text_input("Órgão de Encaminhamento",
                                  placeholder="Obrigatório se ação = Encaminhamento")

            card_section("Prazo e Status")
            col5, col6 = st.columns(2)
            prazo  = col5.date_input("Prazo (opcional)", value=None)
            status = col6.selectbox("Status", ["", "Pendente", "Em andamento", "Concluído"])

            card_section("Relatório")
            relato = st.text_area("Relatório *", height=140,
                                  placeholder="Descreva a ação realizada...")

            opts_tec = _tecnicos_lista()
            tecnico = (st.selectbox("Técnico Responsável *", opts_tec)
                       if opts_tec else st.text_input("Técnico Responsável *"))

            salvar = st.button("💾 Salvar Acompanhamento", use_container_width=True, type="primary")

        if salvar:
            if not relato:
                st.error("⚠️ O campo Relatório é obrigatório.")
            elif tipo_acao == "Encaminhamento" and not orgao:
                st.error("⚠️ Informe o órgão quando a ação for 'Encaminhamento'.")
            else:
                with st.spinner("Salvando..."):
                    try:
                        dados = {
                            "TbAcomCaso":           num_caso_inc,
                            "TbAcompdata":          str(datetime.combine(data_acomp, datetime.min.time())),
                            "TbAcompAcao":          tipo_acao,
                            "TbCaraterAtendimento": carater,
                            "TbRelato":             relato,
                            "TbTecnicoResponsavel": tecnico,
                        }
                        if orgao:  dados["TbAcompOrgao"]  = orgao
                        if prazo:  dados["TbAcompPrazo"]  = str(datetime.combine(prazo, datetime.min.time()))
                        if status: dados["TbAcompStatus"] = status
                        post("/acompanhamentos/", dados)
                        st.success("✅ Acompanhamento registrado com sucesso!")
                        if tipo_acao == "Concluída para Ouvidoria":
                            st.info("ℹ️ A ouvidoria deste caso foi encerrada automaticamente.")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

    # ── Editar Acompanhamento ────────────────────────────────────────────────
    with aba[2]:
        with st.container(border=True):
            col_c, col_b2 = st.columns([2, 1])
            cod_acomp = col_c.number_input("Código do Acompanhamento", min_value=1, step=1,
                                           label_visibility="collapsed")
            if col_b2.button("📂 Carregar", use_container_width=True):
                with st.spinner("Carregando..."):
                    try:
                        st.session_state["acomp_edicao"] = get(f"/acompanhamentos/{cod_acomp}")
                    except Exception:
                        st.error("Acompanhamento não encontrado.")

        if "acomp_edicao" in st.session_state:
            a = st.session_state["acomp_edicao"]
            dt_str = (a.get("TbAcompdata") or "")[:10]
            st.markdown(
                f"""<div style="background:#f8fbff;border:1px solid #cfe2ff;border-radius:10px;
                    padding:12px 18px;margin:8px 0">
                    Caso nº <strong>{a['TbAcomCaso']}</strong> &nbsp;·&nbsp;
                    <strong>{a.get('TbAcompAcao','')}</strong> &nbsp;·&nbsp;
                    {dt_str}
                </div>""",
                unsafe_allow_html=True
            )
            with st.form("form_edit_acomp"):
                novo_relato = st.text_area("Relatório", value=a.get("TbRelato", ""), height=140)
                col_s, col_p = st.columns(2)
                status_opts = ["", "Pendente", "Em andamento", "Concluído"]
                cur_status = a.get("TbAcompStatus") or ""
                idx = status_opts.index(cur_status) if cur_status in status_opts else 0
                novo_status = col_s.selectbox("Status", status_opts, index=idx)
                novo_prazo  = col_p.date_input("Novo Prazo (opcional)", value=None)
                salvar_e = st.form_submit_button("💾 Salvar Alterações", use_container_width=True, type="primary")

            if salvar_e:
                dados = {"TbRelato": novo_relato}
                if novo_status: dados["TbAcompStatus"] = novo_status
                if novo_prazo:  dados["TbAcompPrazo"] = str(datetime.combine(novo_prazo, datetime.min.time()))
                with st.spinner("Salvando..."):
                    try:
                        put(f"/acompanhamentos/{cod_acomp}", dados)
                        st.success("✅ Acompanhamento atualizado!")
                        del st.session_state["acomp_edicao"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
