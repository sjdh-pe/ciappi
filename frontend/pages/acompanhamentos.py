import streamlit as st
import pandas as pd
from api.client import get, post, put
from datetime import datetime


def show():
    st.title("📋 Acompanhamentos")
    aba = st.tabs(["Ver por Caso", "Novo Acompanhamento", "Editar Acompanhamento"])

    # ── Ver por Caso ────────────────────────────────────
    with aba[0]:
        num_caso = st.number_input("Nº do Caso", min_value=1, step=1)
        if st.button("🔍 Buscar Acompanhamentos"):
            try:
                try:
                    caso = get(f"/casos/{num_caso}")
                    enc = caso.get("TbCasoEncerrado") == "Sim"
                    badge = "🔴 ENCERRADO" if enc else "🟢 ATIVO"
                    st.info(
                        f"**{caso['tbnomeidoso']}** — Caso nº {num_caso} | {badge} | "
                        f"Técnico: {caso.get('TbCasoTecnicoResp', '')}"
                    )
                except Exception:
                    pass

                acomps = get(f"/acompanhamentos/caso/{num_caso}")
                if acomps:
                    df = pd.DataFrame(acomps)
                    cols_disp = ["tbcodigo", "TbAcompdata", "TbAcompAcao",
                                 "TbCaraterAtendimento", "TbTecnicoResponsavel",
                                 "TbAcompStatus", "TbAcompPrazo"]
                    df = df[[c for c in cols_disp if c in df.columns]]
                    df.columns = ["Código", "Data", "Ação", "Caráter",
                                  "Técnico", "Status", "Prazo"][:len(df.columns)]
                    st.success(f"{len(df)} acompanhamento(s).")
                    st.dataframe(df, use_container_width=True)

                    with st.expander("📄 Ver relatos completos"):
                        for a in acomps:
                            dt = (a.get("TbAcompdata") or "")[:10]
                            st.markdown(f"**{dt} — {a['TbAcompAcao']}** "
                                        f"({a.get('TbCaraterAtendimento', '')}) | "
                                        f"Técnico: {a.get('TbTecnicoResponsavel', '')}")
                            if a.get("TbAcompOrgao"):
                                st.markdown(f"📌 Órgão: {a['TbAcompOrgao']}")
                            if a.get("TbAcompPrazo"):
                                st.markdown(f"⏰ Prazo: {a['TbAcompPrazo'][:10]}")
                            st.text(a.get("TbRelato", ""))
                            st.divider()
                else:
                    st.info("Nenhum acompanhamento encontrado para este caso.")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── Novo Acompanhamento ─────────────────────────────
    with aba[1]:
        with st.form("form_acomp"):
            col1, col2 = st.columns(2)
            num_caso_inc = col1.number_input("Nº do Caso*", min_value=1, step=1)
            data_acomp   = col2.date_input("Data da Ação*")

            try:
                tipos = get("/tabelas/tipo-acao")
                opts_tipo = [t["DescricaoAcao"] for t in tipos]
            except Exception:
                opts_tipo = ["Visita Domiciliar", "Atendimento Individual",
                             "Encaminhamento", "Concluída para Ouvidoria"]
            tipo_acao = st.selectbox("Tipo de Ação*", opts_tipo)

            # Caráter correto conforme o Access: Social / Jurídico / Psicológico
            carater = st.selectbox("Caráter do Atendimento*", ["Social", "Jurídico", "Psicológico"])

            orgao = st.text_input("Órgão de Encaminhamento (obrigatório se ação = Encaminhamento)")

            col3, col4 = st.columns(2)
            prazo  = col3.date_input("Prazo (opcional)", value=None)
            status = col4.selectbox("Status", ["", "Pendente", "Concluído", "Em andamento"])

            relato = st.text_area("Relatório*", height=150)

            try:
                tecnicos = get("/tabelas/tecnicos")
                opts_tec = [t["TbNomeTecnico"] for t in tecnicos]
            except Exception:
                opts_tec = []
            tecnico = (st.selectbox("Técnico Responsável*", opts_tec)
                       if opts_tec else st.text_input("Técnico Responsável*"))

            salvar = st.form_submit_button("💾 Salvar Acompanhamento", use_container_width=True)

        if salvar:
            if not relato:
                st.error("O campo Relatório é obrigatório.")
            elif tipo_acao == "Encaminhamento" and not orgao:
                st.error("Informe o órgão quando a ação for 'Encaminhamento'.")
            else:
                try:
                    dados = {
                        "TbAcomCaso": num_caso_inc,
                        "TbAcompdata": str(datetime.combine(data_acomp, datetime.min.time())),
                        "TbAcompAcao": tipo_acao,
                        "TbCaraterAtendimento": carater,
                        "TbRelato": relato,
                        "TbTecnicoResponsavel": tecnico,
                    }
                    if orgao:
                        dados["TbAcompOrgao"] = orgao
                    if prazo:
                        dados["TbAcompPrazo"] = str(datetime.combine(prazo, datetime.min.time()))
                    if status:
                        dados["TbAcompStatus"] = status
                    post("/acompanhamentos/", dados)
                    st.success("✅ Acompanhamento registrado com sucesso!")
                    if tipo_acao == "Concluída para Ouvidoria":
                        st.info("ℹ️ A ouvidoria deste caso foi encerrada automaticamente.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Editar Acompanhamento ───────────────────────────
    with aba[2]:
        cod_acomp = st.number_input("Código do Acompanhamento", min_value=1, step=1)
        if st.button("📂 Carregar"):
            try:
                a = get(f"/acompanhamentos/{cod_acomp}")
                st.session_state["acomp_edicao"] = a
            except Exception:
                st.error("Acompanhamento não encontrado.")

        if "acomp_edicao" in st.session_state:
            a = st.session_state["acomp_edicao"]
            st.info(f"Caso nº {a['TbAcomCaso']} | {(a.get('TbAcompdata') or '')[:10]} | {a['TbAcompAcao']}")
            with st.form("form_edit_acomp"):
                novo_relato = st.text_area("Relatório", value=a.get("TbRelato", ""), height=150)
                status_opts = ["", "Pendente", "Concluído", "Em andamento"]
                cur_status = a.get("TbAcompStatus") or ""
                idx = status_opts.index(cur_status) if cur_status in status_opts else 0
                novo_status = st.selectbox("Status", status_opts, index=idx)
                novo_prazo  = st.date_input("Novo Prazo (opcional)", value=None)
                salvar_e = st.form_submit_button("💾 Salvar", use_container_width=True)

            if salvar_e:
                dados = {"TbRelato": novo_relato}
                if novo_status:
                    dados["TbAcompStatus"] = novo_status
                if novo_prazo:
                    dados["TbAcompPrazo"] = str(datetime.combine(novo_prazo, datetime.min.time()))
                try:
                    put(f"/acompanhamentos/{cod_acomp}", dados)
                    st.success("✅ Acompanhamento atualizado!")
                    del st.session_state["acomp_edicao"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
