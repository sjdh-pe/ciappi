import streamlit as st
import pandas as pd
import plotly.express as px
from api.client import get
from components.styles import card_section


def show():
    st.markdown("""
        <div style="padding:4px 0 20px">
            <h2 style="margin:0;color:#1a3a5c">🏠 Painel Inicial</h2>
            <div style="font-size:13px;color:#6b7c93;margin-top:4px">
                Sistema de Gestão de Casos de Proteção ao Idoso — SJDH/PE
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Métricas ───────────────────────────────────────────────────────────────
    try:
        ativos    = get("/relatorios/casos-ativos")
        parados   = get("/relatorios/casos-parados", {"dias": 60})
        av_30     = get("/ouvidoria/avencer", {"dias": 30})
        vencidas  = get("/ouvidoria/vencidas")

        total_ativos   = ativos.get("total", 0)
        total_parados  = parados.get("total", 0)
        n_av30         = len(av_30)
        n_vencidas     = len(vencidas)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📁 Casos Ativos",
                total_ativos,
            )
        with col2:
            delta_par = f"-{total_parados} parados" if total_parados else None
            st.metric(
                "⏸️ Casos Parados +60 dias",
                total_parados,
                delta=delta_par,
                delta_color="inverse",
            )
        with col3:
            st.metric(
                "📣 Ouvidoria a Vencer (30d)",
                n_av30,
                delta=f"{n_av30} casos" if n_av30 else "Nenhum",
                delta_color="inverse" if n_av30 else "normal",
            )
        with col4:
            st.metric(
                "🔴 Prazos Vencidos",
                n_vencidas,
                delta=f"URGENTE" if n_vencidas else "OK",
                delta_color="inverse" if n_vencidas else "normal",
            )

    except Exception:
        st.info("🔌 API offline. Verifique a conexão com o servidor.")
        return

    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)

    # ── Gráficos ───────────────────────────────────────────────────────────────
    col_a, col_b = st.columns([1.4, 1])

    with col_a:
        card_section("📍 Casos Ativos por Município")
        try:
            mun_data = get("/relatorios/municipio")
            if mun_data:
                df_mun = (
                    pd.DataFrame(mun_data)
                    .rename(columns={"municipio": "Município", "total": "Total"})
                    .sort_values("Total", ascending=False)
                    .head(12)
                )
                fig = px.bar(
                    df_mun, x="Município", y="Total",
                    color="Total",
                    color_continuous_scale=["#cfe2ff", "#1a3a5c"],
                    text="Total",
                )
                fig.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=280,
                    coloraxis_showscale=False,
                    xaxis_title="", yaxis_title="",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("Sem dados de municípios.")
        except Exception as e:
            st.caption(f"Erro ao carregar gráfico: {e}")

    with col_b:
        card_section("🚨 Ouvidorias Vencidas")
        try:
            if vencidas:
                df_v = pd.DataFrame(vencidas)
                cols_v = ["TbCasoNumCaso", "tbnomeidoso", "TbPrazoOuvidoria"]
                df_v = df_v[[c for c in cols_v if c in df_v.columns]]
                df_v.columns = ["Nº", "Idoso", "Prazo"][:len(df_v.columns)]
                if "Prazo" in df_v.columns:
                    df_v["Prazo"] = pd.to_datetime(df_v["Prazo"], errors="coerce").dt.strftime("%d/%m/%Y")
                st.dataframe(
                    df_v,
                    use_container_width=True,
                    height=260,
                    hide_index=True,
                    column_config={
                        "Nº": st.column_config.NumberColumn("Nº", width="small"),
                        "Idoso": st.column_config.TextColumn("Idoso"),
                        "Prazo": st.column_config.DateColumn("Prazo Vencido", format="DD/MM/YYYY"),
                    }
                )
            else:
                st.markdown("""
                    <div style="text-align:center;padding:40px 0;color:#6b7c93">
                        <div style="font-size:32px">✅</div>
                        <div>Nenhum prazo vencido</div>
                    </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.caption(f"Erro: {e}")

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    # ── Casos mais recentes ────────────────────────────────────────────────────
    card_section("🕐 Últimos Casos Ativos")
    try:
        casos_lista = ativos.get("casos", [])
        if casos_lista:
            df_rec = pd.DataFrame(casos_lista)
            cols_r = ["TbCasoNumCaso", "tbnomeidoso", "TbCasoMunicipio",
                      "TbCasoTecnicoResp", "ultima_data_acomp", "ultima_acao"]
            df_rec = df_rec[[c for c in cols_r if c in df_rec.columns]]
            df_rec.columns = ["Nº", "Idoso", "Município", "Técnico",
                              "Último Acomp.", "Última Ação"][:len(df_rec.columns)]
            st.dataframe(
                df_rec,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nº": st.column_config.NumberColumn("Nº", format="%d", width="small"),
                    "Idoso": st.column_config.TextColumn("Idoso", width="medium"),
                    "Município": st.column_config.TextColumn("Município"),
                    "Técnico": st.column_config.TextColumn("Técnico"),
                    "Último Acomp.": st.column_config.DatetimeColumn("Último Acomp.", format="DD/MM/YYYY"),
                    "Última Ação": st.column_config.TextColumn("Última Ação"),
                }
            )
    except Exception:
        pass

    # ── Rodapé ─────────────────────────────────────────────────────────────────
    st.markdown("""
        <div style="margin-top:40px;padding:12px 0;border-top:1px solid #e0e9f4;
             text-align:center;font-size:12px;color:#adb5bd">
            CIAPPI · Sistema de Proteção ao Idoso · SJDH/PE · v2.0
        </div>
    """, unsafe_allow_html=True)
