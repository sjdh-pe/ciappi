# CHECKLIST DE MIGRAÇÃO — CIAPPI Access → Python/FastAPI

> Atualizado em: 31/03/2026
> Prioridade atual: **Backend**

---

## ✅ JÁ FEITO (sessões anteriores)

### Infraestrutura
- [x] Projeto FastAPI criado com estrutura `app/routers`, `app/models`, `app/schemas`, `app/services`
- [x] Banco MySQL configurado via SQLAlchemy (`app/database.py`)
- [x] Variáveis de ambiente com `pydantic-settings` (`app/core/config.py`)
- [x] Modo DEV_MODE para desenvolvimento sem JWT (`app/dependencies.py`)
- [x] CORS configurado para Streamlit (`http://localhost:8501`)
- [x] `Makefile` com comandos `run-backend`, `run-frontend`, `setup`
- [x] `QUICKSTART.md` e `setup.sh`
- [x] Documentação `ANALISE_MIGRACAO.md` com mapeamento completo do Access

### Auth (`/auth`)
- [x] `POST /auth/login` — login nome+senha, retorna JWT
- [x] Lógica VBA replicada: usuário bloqueado → erro 403
- [x] Controle de nível (`require_nivel`) em todos os endpoints protegidos
- [x] Nível 1 = somente leitura, Nível 2+ = CRUD, Nível 3 = administração

### Casos (`/casos`)
- [x] `GET /casos/` — lista com filtros (município, encerrado, técnico)
- [x] `GET /casos/{num_caso}` — detalhe
- [x] `POST /casos/` — criação (valida número único, campos obrigatórios, MAIÚSCULAS)
- [x] `PUT /casos/{num_caso}` — atualização + encerramento (data + motivo juntos)
- [x] `PUT /casos/{num_caso}/restaurar` — restauração (limpa encerramento)
- [x] **Regra VBA:** ao encerrar cria acompanhamento automático `"ENCERRAMENTO DO CASO"`

### Acompanhamentos (`/acompanhamentos`)
- [x] `GET /acompanhamentos/caso/{num_caso}` — lista por caso, desc por data
- [x] `GET /acompanhamentos/{codigo}` — detalhe
- [x] `POST /acompanhamentos/` — criação (valida caso existente, prazo, encaminhamento)
- [x] `PUT /acompanhamentos/{codigo}` — atualização

### Usuários (`/usuarios`)
- [x] `GET /usuarios/` — lista (filtro por nome)
- [x] `GET /usuarios/{num_cadastro}` — detalhe
- [x] `POST /usuarios/` — criação (valida caso, data cadastro)
- [x] `PUT /usuarios/{num_cadastro}` — atualização

### ILPIs (`/ilpis`)
- [x] `GET /ilpis/` — lista
- [x] `GET /ilpis/{codigo}` — detalhe
- [x] `POST /ilpis/` — cadastro (campos obrigatórios, MAIÚSCULAS)
- [x] `PUT /ilpis/{codigo}` — atualização

### Eventos (`/eventos`)
- [x] `GET /eventos/` — lista
- [x] `GET /eventos/{codigo}` — detalhe
- [x] `POST /eventos/` — criação
- [x] `PUT /eventos/{codigo}` — atualização com dados de realização

### Visitas (`/visitas`)
- [x] `GET /visitas/inst` — lista visitas institucionais
- [x] `GET /visitas/inst/{codigo}` — detalhe
- [x] `POST /visitas/inst` — registrar visita institucional
- [x] `PUT /visitas/inst/{codigo}` — atualizar visita institucional
- [x] `GET /visitas/ilpi` — lista visitas a ILPIs (com filtro status)
- [x] `GET /visitas/ilpi/{codigo}` — detalhe
- [x] `POST /visitas/ilpi` — agendar visita a ILPI
- [x] `PUT /visitas/ilpi/{codigo}/realizar` — registrar realização
- [x] `PUT /visitas/ilpi/{codigo}` — atualizar visita a ILPI

### Ouvidoria (`/ouvidoria`)
- [x] `GET /ouvidoria/avencer` — prazos futuros (filtro por N dias)
- [x] `GET /ouvidoria/vencidas` — prazos já vencidos
- [x] `GET /ouvidoria/ambiente` — casos da Ouvidoria SJDH após set/2019
- [x] `GET /ouvidoria/concluidas` — ouvidorias encerradas
- [x] `PUT /ouvidoria/{num_caso}/encerrar` — encerrar ouvidoria com nº ofício

### Relatórios (`/relatorios`)
- [x] `GET /relatorios/casos-ativos` — com JOIN do último acompanhamento
- [x] `GET /relatorios/encerrados` — filtro por período
- [x] `GET /relatorios/municipio` — ranking de casos por município
- [x] `GET /relatorios/violencia` — agrupado por tipo de violência
- [x] `GET /relatorios/origem` — agrupado por origem
- [x] `GET /relatorios/acompanhamentos` — lista + contagem por caráter + contagem por ação
- [x] `GET /relatorios/eventos` — filtro por período

### Tabelas Auxiliares (`/tabelas`)
- [x] CRUD completo: motivos-atendimento, motivos-encerramento, motivos-restauracao
- [x] CRUD completo: tipo-acao, tipo-evento, motivos-visita, origem, orgaos
- [x] Somente leitura: municipios
- [x] CRUD técnicos (desativa ao invés de deletar)

### Models SQLAlchemy
- [x] `TbCIAPPICaso`, `TbCIAPPIAcompanhamento`, `TbCIAPPIUsuario`
- [x] `TbCIAPPIILPI`, `TbEvento`, `TbVisitaInst`, `TBAcompEntidade`
- [x] `TbTecnico`, `TbOrgao`, tabelas auxiliares completas
- [x] Migration SQL: `001_criar_TBAcompEntidade.sql`

---

## ✅ FEITO NESTA SESSÃO (31/03/2026)

### Novos Relatórios implementados
- [x] `GET /relatorios/casos-parados?dias=N` — casos ativos sem acomp. há N dias (CnParados do Access)
- [x] `GET /relatorios/encerrados-resolutividade` — casos encerrados agrupados por motivo + detalhe (CnEncerradoResolutividade)
- [x] `GET /relatorios/encaminhamentos` — última movimentação de encaminhamento por caso (CnUltMovimentacao)
- [x] `GET /relatorios/acomp-por-tecnico?tecnico=X` — acompanhamentos por técnico + resumo por ação (CnAcompEspec)
- [x] `GET /relatorios/violencia-bairro` — violência por bairro de residência do idoso (CnBairroTotal)
- [x] `GET /relatorios/municipio-idoso` — ranking municípios de residência dos idosos (CnMunicipio2)
- [x] `GET /relatorios/visitas-ilpi` — relatório de visitas a ILPIs por período
- [x] `GET /relatorios/visitas-inst` — relatório de visitas institucionais por período

### Relatórios melhorados
- [x] `/relatorios/casos-ativos` — agora inclui `ultima_acao` e `ultima_data_acomp` (JOIN com acompanhamento) + total
- [x] `/relatorios/acompanhamentos` — agora retorna: lista + `por_carater` (CnAcomp12) + `por_acao` (CnAcomp13) + total

### Schemas Pydantic criados (routers deixaram de usar `dict`)
- [x] `app/schemas/usuario.py` — `UsuarioCreate`, `UsuarioUpdate`, `UsuarioOut` (todos os ~70 campos mapeados)
- [x] `app/schemas/visita_inst.py` — `VisitaInstCreate`, `VisitaInstUpdate`, `VisitaInstOut`

### Validações de negócio adicionadas
- [x] `app/schemas/evento.py` — `Tbdataprevista` não pode ser < hoje (regra FrmCadEvento do Access)
- [x] Routers `usuarios.py` e `visitas.py` (inst) atualizados para usar schemas tipados com `response_model`

### Gatilho de Ouvidoria implementado
- [x] `app/services/acomp_service.py` — quando `TbAcompAcao = "Concluída para Ouvidoria"`, encerra automaticamente a ouvidoria do caso (`TbEncerradoOuvidoria = "Sim"`, `TbDtEncerradoOuvidoria = now()`) — reproduz o comportamento do `FrmEncerraOuvidoria` do Access

### Testes
- [x] `backend/tests/conftest.py` — fixture com banco SQLite in-memory, injeção de dependência, técnico padrão para DEV_MODE
- [x] `backend/tests/test_casos.py` — 13 testes reais cobrindo:
  - criação de caso (sucesso, número duplicado, detalhe, 404)
  - encerramento (sem data falha, sem motivo falha, completo cria acomp automático)
  - restauração (limpa campos)
  - filtros (município, encerrado)
  - acompanhamentos (caso inexistente, encaminhamento sem órgão, com órgão)
  - gatilho ouvidoria (Concluída para Ouvidoria → encerra automaticamente)

---

## ✅ FEITO NA SESSÃO 2 (31/03/2026 — tarde)

### Backend — Validações e Schemas
- [x] `app/schemas/caso.py` — `Tbambienteviolencia` agora é **obrigatório** e validado (`Intrafamiliar` / `Extrafamiliar`)
- [x] `app/schemas/caso.py` — `CasoOut` expandido com campos de ouvidoria (`TbEncerradoOuvidoria`, `TbNumOfOuvidoria`, etc.)
- [x] `app/routers/usuarios.py` — **paginação** com `skip`/`limit` (padrão 50, máx 500)

### Backend — Relatórios adicionados
- [x] `GET /relatorios/perfil/escolaridade` — distribuição por escolaridade
- [x] `GET /relatorios/perfil/faixa-etaria` — faixas `<65`, `65-74`, `75-84`, `≥85`
- [x] `GET /relatorios/perfil/renda` — faixa de renda familiar
- [x] `GET /relatorios/perfil/sexo` — distribuição por sexo
- [x] `GET /relatorios/perfil/raca-cor` — distribuição por raça/cor
- [x] `GET /relatorios/perfil/mobilidade` — situação de moradia + morador de rua + benefício social
- [x] `GET /relatorios/eventos-por-municipio` — ranking de eventos por município

### Backend — Export CSV
- [x] `GET /relatorios/csv/casos-ativos` — download CSV
- [x] `GET /relatorios/csv/casos-parados?dias=N` — download CSV
- [x] `GET /relatorios/csv/encaminhamentos` — download CSV
- [x] `GET /relatorios/csv/municipio` — download CSV
- [x] `GET /relatorios/csv/violencia` — download CSV

### Backend — Alembic
- [x] `backend/alembic.ini` — configuração do Alembic
- [x] `backend/alembic/env.py` — carrega todos os models automaticamente (autogenerate)
- [x] `backend/alembic/script.py.mako` — template de migration
- [x] `backend/alembic/versions/001_baseline_schema.py` — baseline da migration
- [x] `Makefile` — comandos `make migrate`, `make migrate-new MSG=...`, `make migrate-status`, `make test`

### Frontend — Páginas atualizadas
- [x] `frontend/pages/casos.py` — campo `Tbambienteviolencia` no formulário, busca com filtro de técnico, aba "Restaurar Caso" com motivos, campos de ouvidoria na edição
- [x] `frontend/pages/acompanhamentos.py` — caráter correto (Social/Jurídico/Psicológico), exibe info do caso no topo, aba "Editar Acompanhamento", feedback do gatilho de ouvidoria
- [x] `frontend/pages/ouvidoria.py` — 5 abas: A Vencer / Vencidas / SJDH Ativos / Concluídas / Encerrar
- [x] `frontend/pages/relatorios.py` — 13 abas com todos os novos relatórios, gráficos Plotly, botões CSV
- [x] `frontend/pages/visitas_ilpi.py` — **Nova página**: Agendadas / Realizadas / Agendar / Registrar Realização
- [x] `frontend/app.py` — menu atualizado com "Visitas a ILPIs"

---

## ⏳ AINDA FALTA

### 🔴 Alta Prioridade

- [ ] **Rodar os testes** — instalar `pytest` + `httpx` no venv e executar `make test`
- [ ] **Tabela `TbCasoUsuario`** — verificar se o fluxo de incluir usuário em caso existente precisa desta tabela de relacionamento

### 🟡 Prioridade Média

- [ ] **Frontend — Usuários** — adicionar formulário completo de cadastro (muitos campos; criar wizard em abas)
- [ ] **Frontend — Admin Tabelas** — interface de gestão das tabelas auxiliares (CRUD visual)
- [ ] **Senha adicional para módulo de tabelas** — `FrmSenhaATUTabela` do Access (nível 3 + senha extra)
- [ ] **Senha adicional para módulo de Ouvidoria** — `FrmSenhaATUOuvidoria` do Access
- [ ] **Testes de integração** para Acompanhamentos, Usuários, ILPIs, Visitas, Ouvidoria

### 🟢 Baixa Prioridade / Desejável

- [ ] **Export XLSX** dos relatórios (complementar ao CSV já disponível)
- [ ] **Testes de carga** — verificar performance com volume real do banco (>10k casos)
- [ ] **Documentação OpenAPI** — revisar `summary`/`description` dos endpoints no Swagger

---

## 📋 Resumo do Estado Atual

| Módulo | Backend | Testes | Frontend |
|--------|---------|--------|----------|
| Auth | ✅ Completo | ✅ test_auth.py | ✅ Completo |
| Casos | ✅ Completo | ✅ test_casos.py | ✅ Completo |
| Acompanhamentos | ✅ Completo | ✅ (em test_casos) | ✅ Completo |
| Usuários | ✅ Completo | ❌ Falta | ⚠️ Leitura OK, cadastro pendente |
| ILPIs | ✅ Completo | ❌ Falta | ✅ Completo |
| Visitas Inst. | ✅ Completo | ❌ Falta | ✅ Completo |
| Visitas ILPI | ✅ Completo | ❌ Falta | ✅ Completo |
| Eventos | ✅ Completo | ❌ Falta | ✅ Completo |
| Ouvidoria | ✅ Completo | ✅ (em test_casos) | ✅ Completo |
| Relatórios | ✅ Completo | ❌ Falta | ✅ Completo |
| Tabelas Aux. | ✅ Completo | ❌ Falta | ⚠️ Parcial |

---

## 🗂️ Todos os Arquivos Alterados (acumulado)

| Arquivo | O que mudou |
|---------|------------|
| `backend/app/schemas/caso.py` | `Tbambienteviolencia` obrigatório + `CasoOut` expandido |
| `backend/app/schemas/usuario.py` | **Novo** — UsuarioCreate/Update/Out (70+ campos) |
| `backend/app/schemas/visita_inst.py` | **Novo** — VisitaInstCreate/Update/Out |
| `backend/app/schemas/evento.py` | Validação data_prevista |
| `backend/app/routers/relatorios.py` | 16 novos endpoints + exports CSV + perfil |
| `backend/app/routers/usuarios.py` | Schemas tipados + paginação |
| `backend/app/routers/visitas.py` | VisitaInst com schemas tipados |
| `backend/app/services/acomp_service.py` | Gatilho automático de ouvidoria |
| `backend/alembic.ini` | **Novo** — Alembic config |
| `backend/alembic/env.py` | **Novo** — env do Alembic |
| `backend/alembic/script.py.mako` | **Novo** — template migration |
| `backend/alembic/versions/001_baseline_schema.py` | **Novo** — baseline migration |
| `backend/tests/conftest.py` | **Novo** — fixture SQLite in-memory |
| `backend/tests/test_casos.py` | **Novo** — 13 testes de integração |
| `frontend/pages/casos.py` | Restaurar, campo ambiente, busca por técnico |
| `frontend/pages/acompanhamentos.py` | Caráter correto, info do caso, editar acomp |
| `frontend/pages/ouvidoria.py` | 5 abas (vencidas, SJDH, ambiente) |
| `frontend/pages/relatorios.py` | 13 abas com todos os novos relatórios + CSV |
| `frontend/pages/visitas_ilpi.py` | **Nova** — página completa de visitas a ILPIs |
| `frontend/app.py` | Menu com "Visitas a ILPIs" |
| `Makefile` | Comandos Alembic + testes |
