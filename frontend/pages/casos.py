import streamlit as st
import pandas as pd
from api.client import get, post, put
from datetime import datetime


def show():
    st.title("📁 Casos")
    aba = st.tabs(["Buscar / Listar", "Novo Caso", "Atualizar / Encerrar", "Restaurar Caso"])

    # ── Buscar ──────────────────────────────────────────
    with aba[0]:
        col1, col2, col3 = st.columns(3)
        municipio = col1.text_input("Município")
        tecnico   = col2.text_input("Técnico")
        encerrado = col3.selectbox("Status", ["Todos", "Não (Ativos)", "Sim (Encerrados)"])

        if st.button("🔍 Buscar Casos", use_container_width=True):
            params = {}
            if municipio:
                params["municipio"] = municipio
            if tecnico:
                params["tecnico"] = tecnico
            if encerrado == "Não (Ativos)":
                params["encerrado"] = "Não"
            elif encerrado == "Sim (Encerrados)":
                params["encerrado"] = "Sim"
            try:
                casos = get("/casos/", params)
                if casos:
                    df = pd.DataFrame(casos)
                    cols = ["TbCasoNumCaso", "tbnomeidoso", "TbCasoMunicipio",
                            "TbCasoDtinicio", "TbCasoEncerrado", "TbCasoTecnicoResp",
                            "TbCasoMotivoAtendimento"]
                    df = df[[c for c in cols if c in df.columns]]
                    df.columns = ["Nº Caso", "Idoso", "Município", "Dt. Início",
                                  "Encerrado", "Técnico", "Motivo"][:len(df.columns)]
                    st.success(f"{len(df)} caso(s) encontrado(s).")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Nenhum caso encontrado.")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── Novo Caso ────────────────────────────────────────
    with aba[1]:
        with st.form("form_caso"):
            col1, col2 = st.columns(2)
            num_caso  = col1.number_input("Nº do Caso*", min_value=1, step=1)
            dt_inicio = col2.date_input("Data de Início*")
            nome_idoso = st.text_input("Nome do Idoso*")

            col3, col4 = st.columns(2)
            municipio_novo = col3.text_input("Município*")

            try:
                tecnicos = get("/tabelas/tecnicos")
                opts_tec = [t["TbNomeTecnico"] for t in tecnicos]
            except Exception:
                opts_tec = []
            tecnico_novo = (col4.selectbox("Técnico Responsável*", opts_tec)
                            if opts_tec else col4.text_input("Técnico Responsável*"))

            try:
                motivos = get("/tabelas/motivos-atendimento")
                opts_motivo = [m["TbDescricaoMotivo"] for m in motivos]
            except Exception:
                opts_motivo = []
            motivo = st.selectbox("Motivo do Atendimento*", opts_motivo)

            try:
                origens = get("/tabelas/origem")
                opts_origem = [o["descricaochegouprograma"] for o in origens]
            except Exception:
                opts_origem = []
            origem = st.selectbox("Como Chegou ao Programa*", opts_origem)

            ambiente = st.selectbox("Ambiente de Violência*", ["Intrafamiliar", "Extrafamiliar"])
            relato   = st.text_area("Síntese do Caso*", height=120)
            salvar   = st.form_submit_button("💾 Salvar Caso", use_container_width=True)

        if salvar:
            if not all([num_caso, nome_idoso, municipio_novo, motivo, origem, relato]):
                st.error("Todos os campos obrigatórios (*) devem ser preenchidos.")
            else:
                try:
                    post("/casos/", {
                        "TbCasoNumCaso": num_caso,
                        "TbCasoDtinicio": str(datetime.combine(dt_inicio, datetime.min.time())),
                        "tbnomeidoso": nome_idoso.upper(),
                        "TbCasoMotivoAtendimento": motivo,
                        "TbCasoChegouPrograma": origem,
                        "Tbambienteviolencia": ambiente,
                        "TbCasoRelato": relato,
                        "TbCasoMunicipio": municipio_novo.upper(),
                        "TbCasoTecnicoResp": tecnico_novo.upper() if tecnico_novo else "",
                    })
                    st.success(f"✅ Caso {num_caso} registrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    # ── Atualizar / Encerrar ───────────────────────────
    with aba[2]:
        num_busca = st.number_input("Nº do Caso para editar", min_value=1, step=1, key="busca_atu")
        col_b, col_l = st.columns([3, 1])
        if col_b.button("📂 Carregar Caso"):
            try:
                caso = get(f"/casos/{num_busca}")
                st.session_state["caso_edicao"] = caso
            except Exception:
                st.error("Caso não encontrado.")
        if col_l.button("❌ Limpar"):
            st.session_state.pop("caso_edicao", None)
            st.rerun()

        if "caso_edicao" in st.session_state:
            c = st.session_state["caso_edicao"]
            enc = c.get("TbCasoEncerrado") == "Sim"
            badge = "🔴 ENCERRADO" if enc else "🟢 ATIVO"
            st.info(f"**{c['tbnomeidoso']}** — Caso nº {c['TbCasoNumCaso']} | {badge}")

            with st.form("form_atu_caso"):
                relato_atu = st.text_area("Síntese do Caso", value=c.get("TbCasoRelato", ""), height=120)
                obs = st.text_area("Observações", value=c.get("TbObservacoes") or "", height=80)

                st.markdown("---")
                st.subheader("🔒 Encerramento")
                col1, col2 = st.columns(2)
                dt_encer = col1.date_input("Data de Encerramento", value=None)
                try:
                    mot_enc = get("/tabelas/motivos-encerramento")
                    opts_enc = {"(manter aberto)": None,
                                **{m["descricaomotivo"]: m["Código"] for m in mot_enc}}
                except Exception:
                    opts_enc = {"(sem dados)": None}
                motivo_enc = col2.selectbox("Motivo de Encerramento", list(opts_enc.keys()))

                st.markdown("---")
                st.subheader("📣 Ouvidoria")
                col3, col4 = st.columns(2)
                prazo_ouv    = col3.date_input("Prazo Ouvidoria", value=None)
                num_denuncia = col4.number_input("Nº da Denúncia", min_value=0, step=1,
                                                  value=int(c.get("TbNumDenuncia") or 0))

                salvar_atu = st.form_submit_button("💾 Salvar Alteração", use_container_width=True)

            if salvar_atu:
                dados = {"TbCasoRelato": relato_atu}
                if obs:
                    dados["TbObservacoes"] = obs
                if dt_encer:
                    dados["TbCasoDtencer"] = str(datetime.combine(dt_encer, datetime.min.time()))
                cod_enc = opts_enc.get(motivo_enc)
                if cod_enc:
                    dados["TbCasoMotivoEncerramento"] = cod_enc
                if prazo_ouv:
                    dados["TbPrazoOuvidoria"] = str(datetime.combine(prazo_ouv, datetime.min.time()))
                if num_denuncia:
                    dados["TbNumDenuncia"] = num_denuncia
                try:
                    put(f"/casos/{c['TbCasoNumCaso']}", dados)
                    st.success("✅ Alteração salva com sucesso!")
                    del st.session_state["caso_edicao"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── Restaurar Caso ───────────────────────────────────
    with aba[3]:
        st.markdown("Restaura um caso encerrado, limpando data e motivo de encerramento.")
        num_rest = st.number_input("Nº do Caso a Restaurar", min_value=1, step=1)
        if st.button("📂 Verificar Caso"):
            try:
                caso = get(f"/casos/{num_rest}")
                if caso.get("TbCasoEncerrado") == "Sim":
                    st.warning(f"Caso **{caso['tbnomeidoso']}** está ENCERRADO. Pode ser restaurado.")
                    st.session_state["caso_restaurar"] = caso
                else:
                    st.info("Este caso não está encerrado.")
                    st.session_state.pop("caso_restaurar", None)
            except Exception:
                st.error("Caso não encontrado.")

        if "caso_restaurar" in st.session_state:
            c = st.session_state["caso_restaurar"]
            with st.form("form_restaurar"):
                try:
                    mot_rest = get("/tabelas/motivos-restauracao")
                    opts_rest = {m["DescricaoRestauracao"]: m["Código"] for m in mot_rest}
                except Exception:
                    opts_rest = {"Retorno espontâneo": 1}
                motivo_rest = st.selectbox("Motivo de Restauração*", list(opts_rest.keys()))
                restaurar = st.form_submit_button("🔄 Restaurar Caso", use_container_width=True)

            if restaurar:
                try:
                    put(f"/casos/{c['TbCasoNumCaso']}/restaurar",
                        {"motivo_restauracao": opts_rest[motivo_rest]})
                    st.success(f"✅ Caso {c['TbCasoNumCaso']} restaurado com sucesso!")
                    del st.session_state["caso_restaurar"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
