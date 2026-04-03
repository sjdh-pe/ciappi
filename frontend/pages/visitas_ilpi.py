import streamlit as st
import pandas as pd
from api.client import get, post, put
from datetime import datetime
from components.styles import card_section
from components.listas import ilpis_map as _ilpis, motivos_visita as _motivos_visita, tecnicos as _tecnicos


def _fmt_date(val):
    if val:
        return str(val)[:10]
    return "—"


def show():
    st.markdown("""
        <div style="padding:4px 0 16px">
            <h2 style="margin:0;color:#1a3a5c">🔍 Visitas a ILPIs</h2>
            <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                Agendamento e registro de visitas às ILPIs
            </div>
        </div>
        <hr style="border:none;border-top:2px solid #e0e9f4;margin-bottom:20px">
    """, unsafe_allow_html=True)

    aba = st.tabs(["📅 Agendadas", "✅ Realizadas", "➕ Agendar", "📝 Registrar Realização"])

    # ── Agendadas ────────────────────────────────────────────────────────────
    with aba[0]:
        if st.button("🔄 Carregar Agendadas", type="primary"):
            with st.spinner("Carregando..."):
                try:
                    dados = get("/visitas/ilpi", {"status": "agendada"})
                    if dados:
                        df = pd.DataFrame(dados)
                        cols = ["Codigoentidade", "nomeentidade", "dtprevistavisita",
                                "motivovisita", "tecnicoresponsavel"]
                        df = df[[c for c in cols if c in df.columns]].copy()
                        df.columns = ["Cód.", "ILPI", "Data Prevista", "Motivo", "Técnico"][:len(df.columns)]
                        if "Data Prevista" in df.columns:
                            df["Data Prevista"] = pd.to_datetime(df["Data Prevista"], errors="coerce")
                        st.warning(f"📅 {len(df)} visita(s) agendada(s) aguardando realização.")
                        st.dataframe(df, use_container_width=True, hide_index=True,
                                     column_config={"Data Prevista": st.column_config.DatetimeColumn(
                                         "Data Prevista", format="DD/MM/YYYY")})
                    else:
                        st.success("✅ Nenhuma visita agendada pendente.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Realizadas ───────────────────────────────────────────────────────────
    with aba[1]:
        if st.button("🔄 Carregar Realizadas", type="primary"):
            with st.spinner("Carregando..."):
                try:
                    dados = get("/visitas/ilpi", {"status": "realizada"})
                    if dados:
                        df = pd.DataFrame(dados)
                        cols = ["Codigoentidade", "nomeentidade", "dtprevistavisita",
                                "dtvisita", "tecnicoresponsavel"]
                        df = df[[c for c in cols if c in df.columns]].copy()
                        df.columns = ["Cód.", "ILPI", "Data Prevista",
                                      "Data Realização", "Técnico"][:len(df.columns)]
                        for c in ["Data Prevista", "Data Realização"]:
                            if c in df.columns:
                                df[c] = pd.to_datetime(df[c], errors="coerce")
                        st.success(f"✅ {len(df)} visita(s) realizada(s).")
                        st.dataframe(df, use_container_width=True, hide_index=True,
                                     column_config={
                                         "Data Prevista": st.column_config.DatetimeColumn("Data Prevista", format="DD/MM/YYYY"),
                                         "Data Realização": st.column_config.DatetimeColumn("Data Realização", format="DD/MM/YYYY"),
                                     })
                        with st.expander("📄 Ver relatos das visitas"):
                            for d in dados:
                                if d.get("relato"):
                                    st.markdown(
                                        f"<div style='border:1px solid #e0e9f4;border-radius:8px;"
                                        f"padding:12px 16px;margin-bottom:8px'>"
                                        f"<strong>{d.get('nomeentidade','')}</strong> — "
                                        f"{_fmt_date(d.get('dtvisita'))}</div>",
                                        unsafe_allow_html=True
                                    )
                                    st.text(d["relato"])
                    else:
                        st.info("Nenhuma visita realizada encontrada.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Agendar ──────────────────────────────────────────────────────────────
    with aba[2]:
        with st.container(border=True):
            opts_ilpi = _ilpis()
            if opts_ilpi:
                nome_ilpi_sel = st.selectbox("ILPI *", list(opts_ilpi.keys()))
            else:
                st.warning("Nenhuma ILPI cadastrada. Cadastre uma ILPI primeiro.")
                nome_ilpi_sel = None

            col1, col2 = st.columns(2)
            dt_prevista = col1.date_input("Data Prevista *")
            opts_mot = _motivos_visita()
            motivo = col2.selectbox("Motivo da Visita *", opts_mot)

            opts_tec = _tecnicos()
            tecnico = (st.selectbox("Técnico Responsável *", opts_tec)
                       if opts_tec else st.text_input("Técnico Responsável *"))
            obs = st.text_area("Observações", height=70)
            agendar = st.button("📅 Agendar Visita", use_container_width=True, type="primary")

        if agendar:
            if not nome_ilpi_sel or not opts_ilpi:
                st.error("⚠️ Selecione uma ILPI.")
            else:
                with st.spinner("Agendando..."):
                    try:
                        cod_ilpi = opts_ilpi[nome_ilpi_sel]
                        post("/visitas/ilpi", {
                            "codigoilpi":       cod_ilpi,
                            "nomeentidade":     nome_ilpi_sel,
                            "dtprevistavisita": str(datetime.combine(dt_prevista, datetime.min.time())),
                            "motivovisita":     motivo,
                            "tecnicoresponsavel": tecnico,
                            "observacoes":      obs or None,
                        })
                        st.success(f"✅ Visita agendada para {nome_ilpi_sel} em {dt_prevista}!")
                        from components.listas import ilpis_map
                        ilpis_map.clear()
                    except Exception as e:
                        st.error(f"Erro: {e}")

    # ── Registrar Realização ─────────────────────────────────────────────────
    with aba[3]:
        with st.spinner("Carregando visitas agendadas..."):
            try:
                agendadas = get("/visitas/ilpi", {"status": "agendada"})
            except Exception:
                agendadas = []

        if agendadas:
            opts_ag = {
                f"{v.get('nomeentidade','')} — prevista: {_fmt_date(v.get('dtprevistavisita'))} (cód {v['Codigoentidade']})": v["Codigoentidade"]
                for v in agendadas
            }
            with st.container(border=True):
                vis_sel = st.selectbox("Selecione a Visita Agendada", list(opts_ag.keys()))
                cod_vis = opts_ag[vis_sel]

            with st.form("form_realizar_ilpi"):
                card_section("Dados da Realização")
                dt_real = st.date_input("Data de Realização *")
                relato  = st.text_area("Relatório da Visita *", height=140,
                                       placeholder="Descreva o que foi observado durante a visita...")
                obs_r   = st.text_area("Observações adicionais", height=70)
                realizar = st.form_submit_button("✅ Registrar Realização", use_container_width=True, type="primary")

            if realizar:
                if not relato:
                    st.error("⚠️ O relato da visita é obrigatório.")
                else:
                    with st.spinner("Registrando..."):
                        try:
                            put(f"/visitas/ilpi/{cod_vis}/realizar", {
                                "dtvisita":    str(datetime.combine(dt_real, datetime.min.time())),
                                "relato":      relato,
                                "observacoes": obs_r or None,
                            })
                            st.success("✅ Visita registrada como realizada!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
        else:
            st.info("Nenhuma visita agendada pendente para registrar.")
