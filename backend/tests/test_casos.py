"""
Testes de integração para o módulo de casos.
Usa banco SQLite in-memory configurado em conftest.py.

Regras do Access testadas:
- TbCasoNumCaso único (não pode duplicar)
- Encerramento: data + motivo juntos obrigatórios
- Restauração: limpa encerramento
- Acompanhamento automático ao encerrar
- Gatilho de ouvidoria ao acompanhar com "Concluída para Ouvidoria"
"""

CASO_BASE = {
    "TbCasoNumCaso": 1001,
    "TbCasoDtinicio": "2024-01-15T09:00:00",
    "tbnomeidoso": "Maria da Silva",
    "TbCasoMotivoAtendimento": "Violência física",
    "TbCasoChegouPrograma": "Delegacia",
    "Tbambienteviolencia": "Intrafamiliar",
    "TbCasoRelato": "Idosa sofreu agressão física pelo filho.",
    "TbCasoMunicipio": "Recife",
    "TbCasoTecnicoResp": "Ana Paula",
}


# ──────────────────────────────────────────────
# Criação de caso
# ──────────────────────────────────────────────

def test_criar_caso_sucesso(client):
    r = client.post("/casos/", json=CASO_BASE)
    assert r.status_code == 201
    data = r.json()
    assert data["TbCasoNumCaso"] == 1001
    assert data["tbnomeidoso"] == "MARIA DA SILVA"  # convertido para maiúsculas


def test_criar_caso_numero_duplicado(client):
    client.post("/casos/", json=CASO_BASE)
    r = client.post("/casos/", json=CASO_BASE)
    assert r.status_code == 400
    assert "já existe" in r.json()["detail"]


def test_detalhe_caso_existente(client):
    client.post("/casos/", json=CASO_BASE)
    r = client.get("/casos/1001")
    assert r.status_code == 200
    assert r.json()["TbCasoNumCaso"] == 1001


def test_detalhe_caso_inexistente(client):
    r = client.get("/casos/9999")
    assert r.status_code == 404


# ──────────────────────────────────────────────
# Encerramento de caso
# ──────────────────────────────────────────────

def test_encerrar_caso_sem_motivo_falha(client):
    """Encerramento sem motivo deve falhar (regra 4.2 do Access)."""
    client.post("/casos/", json=CASO_BASE)
    r = client.put("/casos/1001", json={"TbCasoDtencer": "2024-06-01T00:00:00"})
    assert r.status_code == 400
    assert "motivo" in r.json()["detail"].lower() or "encerr" in r.json()["detail"].lower()


def test_encerrar_caso_sem_data_falha(client):
    """Encerramento sem data deve falhar (regra 4.2 do Access)."""
    client.post("/casos/", json=CASO_BASE)
    r = client.put("/casos/1001", json={"TbCasoMotivoEncerramento": 1})
    assert r.status_code == 400


def test_encerrar_caso_completo(client):
    """Encerramento com data + motivo deve funcionar e criar acomp. automático."""
    client.post("/casos/", json=CASO_BASE)
    r = client.put("/casos/1001", json={
        "TbCasoDtencer": "2024-06-01T00:00:00",
        "TbCasoMotivoEncerramento": 1,
    })
    assert r.status_code == 200
    assert r.json()["TbCasoEncerrado"] == "Sim"

    # Verifica acompanhamento automático de encerramento (regra FrmATuCaso)
    acomps = client.get("/acompanhamentos/caso/1001")
    assert acomps.status_code == 200
    acoes = [a["TbAcompAcao"] for a in acomps.json()]
    assert "ENCERRAMENTO DO CASO" in acoes


# ──────────────────────────────────────────────
# Restauração de caso
# ──────────────────────────────────────────────

def test_restaurar_caso_encerrado(client):
    """Restauração deve limpar data, motivo e flag encerrado."""
    client.post("/casos/", json=CASO_BASE)
    client.put("/casos/1001", json={
        "TbCasoDtencer": "2024-06-01T00:00:00",
        "TbCasoMotivoEncerramento": 1,
    })
    r = client.put("/casos/1001/restaurar", json={"motivo_restauracao": 2})
    assert r.status_code == 200
    data = r.json()
    # Legado nunca preencheu TbCasoEncerrado; restaurar limpa para NULL
    assert data["TbCasoEncerrado"] is None
    assert data["TbCasoDtencer"] is None
    assert data["TbCasoMotivoEncerramento"] is None


# ──────────────────────────────────────────────
# Listagem e filtros
# ──────────────────────────────────────────────

def test_listar_casos_filtro_municipio(client):
    client.post("/casos/", json=CASO_BASE)
    r = client.get("/casos/?municipio=Recife")
    assert r.status_code == 200
    assert len(r.json()) == 1

    r2 = client.get("/casos/?municipio=Olinda")
    assert r2.status_code == 200
    assert len(r2.json()) == 0


def test_listar_casos_filtro_encerrado(client):
    client.post("/casos/", json=CASO_BASE)
    caso2 = {**CASO_BASE, "TbCasoNumCaso": 1002, "tbnomeidoso": "José da Silva"}
    client.post("/casos/", json=caso2)

    # Encerra o primeiro
    client.put("/casos/1001", json={
        "TbCasoDtencer": "2024-06-01T00:00:00",
        "TbCasoMotivoEncerramento": 1,
    })

    r_enc = client.get("/casos/?encerrado=Sim")
    assert r_enc.status_code == 200
    nums = [c["TbCasoNumCaso"] for c in r_enc.json()]
    assert 1001 in nums
    assert 1002 not in nums


# ──────────────────────────────────────────────
# Acompanhamentos
# ──────────────────────────────────────────────

def test_criar_acompanhamento_caso_inexistente(client):
    r = client.post("/acompanhamentos/", json={
        "TbAcomCaso": 9999,
        "TbAcompdata": "2024-03-10T10:00:00",
        "TbAcompAcao": "Visita domiciliar",
        "TbCaraterAtendimento": "Social",
        "TbRelato": "Visita realizada.",
        "TbTecnicoResponsavel": "Ana Paula",
    })
    assert r.status_code == 400
    assert "não está cadastrado" in r.json()["detail"]


def test_criar_acompanhamento_encaminhamento_sem_orgao(client):
    """Encaminhamento sem órgão deve falhar (regra do Access)."""
    client.post("/casos/", json=CASO_BASE)
    r = client.post("/acompanhamentos/", json={
        "TbAcomCaso": 1001,
        "TbAcompdata": "2024-03-10T10:00:00",
        "TbAcompAcao": "Encaminhamento",
        "TbCaraterAtendimento": "Social",
        "TbRelato": "Encaminhado.",
        "TbTecnicoResponsavel": "Ana Paula",
    })
    assert r.status_code == 422


def test_criar_acompanhamento_encaminhamento_com_orgao(client):
    client.post("/casos/", json=CASO_BASE)
    r = client.post("/acompanhamentos/", json={
        "TbAcomCaso": 1001,
        "TbAcompdata": "2024-03-10T10:00:00",
        "TbAcompAcao": "Encaminhamento",
        "TbAcompOrgao": "CREAS",
        "TbCaraterAtendimento": "Social",
        "TbRelato": "Encaminhado ao CREAS.",
        "TbTecnicoResponsavel": "Ana Paula",
    })
    assert r.status_code == 201


def test_acompanhamento_conclui_ouvidoria_automaticamente(client):
    """Ação 'Concluída para Ouvidoria' deve encerrar a ouvidoria do caso."""
    client.post("/casos/", json=CASO_BASE)

    # Define prazo de ouvidoria no caso
    client.put("/casos/1001", json={"TbPrazoOuvidoria": "2025-01-01T00:00:00"})

    # Cria acompanhamento com a ação gatilho
    r = client.post("/acompanhamentos/", json={
        "TbAcomCaso": 1001,
        "TbAcompdata": "2024-03-10T10:00:00",
        "TbAcompAcao": "Concluída para Ouvidoria",
        "TbCaraterAtendimento": "Social",
        "TbRelato": "Ouvidoria concluída.",
        "TbTecnicoResponsavel": "Ana Paula",
    })
    assert r.status_code == 201

    # Ouvidoria deve constar como concluída
    concluidas = client.get("/ouvidoria/concluidas")
    assert concluidas.status_code == 200
    nums = [c["TbCasoNumCaso"] for c in concluidas.json()]
    assert 1001 in nums
