import streamlit as st
import pandas as pd
from api.client import get, post, put
from datetime import datetime


def show():
    st.title("🏛️ Visitas a ILPIs")
    aba = st.tabs(["Agendadas", "Realizadas", "Agendar Visita", "Registrar Realização"])

    # ── Agendadas ──────────────────────────────────────
    with aba[0]:
        if st.button("🔍 Carregar Visitas Agendadas"):
            try:
                dados = get("/visitas/ilpi", {"status": "agendada"})
                if dados:
                    df = pd.DataFrame(dados)
                    cols = ["Codigoentidade", "nomeentidade", "dtprevistavisita",
                            "motivovisita", "tecnicoresponsavel"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Código", "ILPI", "Data Prevista",
                                  "Motivo", "Técnico"][:len(df.columns)]
                    st.warning(f"📅 {len(df)} visita(s) agendada(s) aguardando realização.")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.success("Nenhuma visita agendada pendente.")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── Realizadas ─────────────────────────────────────
    with aba[1]:
        if st.button("🔍 Carregar Visitas Realizadas"):
            try:
                dados = get("/visitas/ilpi", {"status": "realizada"})
                if dados:
                    df = pd.DataFrame(dados)
                    cols = ["Codigoentidade", "nomeentidade", "dtprevistavisita",
                            "dtvisita", "tecnicoresponsavel"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Código", "ILPI", "Data Prevista",
                                  "Data Realização", "Técnico"][:len(df.columns)]
                    st.success(f"✅ {len(df)} visita(s) realizada(s).")
                    st.dataframe(df, use_container_width=True)

                    with st.expander("📄 Ver relatos"):
                        for d in dados:
                            if d.get("relato"):
                                st.markdown(f"**{d.get('nomeentidade')}** — {(d.get('dtvisita') or '')[:10]}")
                                st.text(d["relato"])
                                st.divider()
                else:
                    st.info("Nenhuma visita realizada encontrada.")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── Agendar Visita ─────────────────────────────────
    with aba[2]:
        with st.form("form_agendar_ilpi"):
            try:
                ilpis = get("/ilpis/")
                opts_ilpi = {i["NOMEILPI"]: i["CODIGOILPI"] for i in ilpis}
            except Exception:
                opts_ilpi = {}

            if opts_ilpi:
                nome_ilpi_sel = st.selectbox("ILPI*", list(opts_ilpi.keys()))
            else:
                nome_ilpi_sel = st.text_input("ILPI (nome)*")
                opts_ilpi = {}

            col1, col2 = st.columns(2)
            dt_prevista = col1.date_input("Data Prevista da Visita*")

            try:
                mot_vis = get("/tabelas/motivos-visita")
                opts_mot = [m["motivovisita"] for m in mot_vis]
            except Exception:
                opts_mot = ["Fiscalização", "Acompanhamento", "Orientação"]
            motivo = col2.selectbox("Motivo da Visita*", opts_mot)

            try:
                tecnicos = get("/tabelas/tecnicos")
                opts_tec = [t["TbNomeTecnico"] for t in tecnicos]
            except Exception:
                opts_tec = []
            tecnico = (st.selectbox("Técnico Responsável*", opts_tec)
                       if opts_tec else st.text_input("Técnico Responsável*"))

            obs = st.text_area("Observações", height=80)
            agendar = st.form_submit_button("📅 Agendar Visita", use_container_width=True)

        if agendar:
            if not opts_ilpi:
                st.error("Nenhuma ILPI cadastrada. Cadastre uma ILPI primeiro.")
            else:
                try:
                    cod_ilpi = opts_ilpi[nome_ilpi_sel]
                    post("/visitas/ilpi", {
                        "codigoilpi": cod_ilpi,
                        "nomeentidade": nome_ilpi_sel,
                        "dtprevistavisita": str(datetime.combine(dt_prevista, datetime.min.time())),
                        "motivovisita": motivo,
                        "tecnicoresponsavel": tecnico,
                        "observacoes": obs or None,
                    })
                    st.success(f"✅ Visita agendada para {nome_ilpi_sel} em {dt_prevista}!")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Registrar Realização ───────────────────────────
    with aba[3]:
        st.markdown("Selecione uma visita agendada e registre a realização.")

        try:
            agendadas = get("/visitas/ilpi", {"status": "agendada"})
        except Exception:
            agendadas = []

        if agendadas:
            opts_ag = {
                f"Cód {v['Codigoentidade']} — {v['nomeentidade']} "
                f"(prevista: {(v.get('dtprevistavisita') or '')[:10]})": v["Codigoentidade"]
                for v in agendadas
            }
            vis_sel = st.selectbox("Visita Agendada", list(opts_ag.keys()))
            cod_vis = opts_ag[vis_sel]

            with st.form("form_realizar_ilpi"):
                dt_real = st.date_input("Data de Realização*")
                relato  = st.text_area("Relatório da Visita*", height=150)
                obs_r   = st.text_area("Observações adicionais", height=80)
                realizar = st.form_submit_button("✅ Registrar Realização", use_container_width=True)

            if realizar:
                if not relato:
                    st.error("O relato da visita é obrigatório.")
                else:
                    try:
                        put(f"/visitas/ilpi/{cod_vis}/realizar", {
                            "dtvisita": str(datetime.combine(dt_real, datetime.min.time())),
                            "relato": relato,
                            "observacoes": obs_r or None,
                        })
                        st.success("✅ Visita registrada como realizada!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
        else:
            st.info("Nenhuma visita agendada pendente para registrar.")
