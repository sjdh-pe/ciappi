# CIAPPI — Mapeamento do Sistema Access para FastAPI + Frontend Python

## 1. Visão Geral do Sistema

O CIAPPI é um sistema de gestão de casos sociais da SJDH-PE voltado ao atendimento e monitoramento de **idosos em situação de vulnerabilidade**. O sistema cobre:

- Cadastro e acompanhamento de **casos**
- Cadastro de **usuários** (idosos atendidos)
- Registro de **acompanhamentos** (ações realizadas por técnicos)
- Gestão de **ILPIs** (Instituições de Longa Permanência para Idosos)
- Controle de **eventos** e formações
- Visitas institucionais
- Módulo de **ouvidoria** com prazos e encerramento
- Relatórios e painéis de monitoramento

---

## 2. Fluxo de Navegação (Mapeado do VBA)

```
[Frmentrada] — Login por técnico e senha (RecordSource: TbTecnico)
    │
    ├─ Nível 1 (monitoramento): → FrmMenuMonitoramento
    └─ Nível 2+ (acesso completo): → FrmMenuPrincipal
        │
        ├─ [BtnCaso]       → FrmMenuCaso
        │     ├─ Cadastrar Caso         → FrmCadCaso
        │     ├─ Incluir Pessoa (nova)  → FrmSelIncPessoa → FrmCadUsuarioNovo
        │     ├─ Incluir Pessoa (exist) → FrmSelIncPessoa → FrmCadUsuarioExistente
        │     ├─ Atualizar Caso         → FrmSelAtuCaso → FrmATuCaso
        │     ├─ Atualizar Pessoa       → FrmSelAtuPessoa → FrmAtuPessoa
        │     ├─ Restaurar Caso         → FrmSelRestaura → FrmRestaura
        │     └─ Ambiente violência     → Frmambiente
        │
        ├─ [BtnAcomp]      → FrmMenuAcomp
        │     ├─ Incluir Acomp          → FrmSelIncAcomp → FrmCadAcomp
        │     └─ Atualizar Acomp        → FrmSelAtuAcomp → FrmAtuAcomp
        │
        ├─ [BtnEntidade]   → FrmMenuEntidade
        │     ├─ Cadastrar ILPI         → FrmCadILPI
        │     ├─ Atualizar ILPI         → FrmSelAtuEnt → FrmAtuEnt
        │     ├─ Incluir Visita         → FrmCadVisitaEnt
        │     ├─ Atualizar Visita       → FrmSelAtuRelEnt → FrmAtuRelVisitaEnt
        │     └─ Agendar Visita         → FrmSelAgenVisita → FrmCadVisitaEnt
        │
        ├─ [BtnEventos]    → FrmMenuEvento
        │     ├─ Cadastrar Evento       → FrmCadEvento
        │     └─ Atualizar Evento       → FrmSelecionaEvento → FrmAtuEvento
        │
        ├─ [BtnVisita]     → FrmMenuVisitaInst
        │     ├─ Incluir Visita         → FrmVisitaInst
        │     └─ Atualizar Visita       → FrmSelAtuVisitaInst → FrmAtuVisitaInst
        │
        ├─ [BtnRelatorio]  → FrmMenuRelatorio
        │     ├─ Acompanhamentos        → FrmIntDataAcompanhamento → RelAcompComp
        │     ├─ Acomp. Específico      → FrmIntDataAcompEspec → FrmResultAcompEspec
        │     ├─ Eventos                → FrmIntDataEvento → RelEvento
        │     ├─ Iniciados              → FrmIntDataIniciado → RelIniciados
        │     ├─ Encerrados             → Frmencerrados → RelEncerrados
        │     ├─ Violência por tipo     → FrmIntDataViolencia → RelViolencia
        │     ├─ Violência por bairro   → FrmIntDataBairro → FrmConsultaBairro
        │     ├─ Por município          → FrmIntDataMunicipio → relmunicipioidoso
        │     ├─ Por origem             → FrmIntDataOrigem → RelOrigem
        │     ├─ Escolaridade           → FrmConEscolaridade
        │     ├─ Faixa etária           → FrmConfaixaetaria
        │     ├─ Renda                  → FrmConRenda
        │     ├─ Mobilidade             → FrmConMobilidade
        │     ├─ Encaminhamentos        → FrmConEncaminhamento
        │     ├─ Visitas Inst.          → FrmIntDataVisInst → RelVisitaInst
        │     ├─ Visitas ILPI           → FrmIntDataVisitaILPI → RelVisitaILPI
        │     ├─ Ouvidoria a vencer     → FrmCnOuvidoriaAVencer
        │     ├─ Ouvidoria concluídas   → FrmCnOuvidoriaConcluidas
        │     └─ Casos ativos           → RelCasoAtivo
        │
        ├─ [BtnMonitoramento] → FrmMenuMonitoramento
        │     └─ (subconjunto do menu relatório, acesso restrito)
        │
        └─ [BtnTabela]     → FrmMenuTabela (protegido por senha)
              ├─ Motivos Atendimento   → FrmTbMotivo      (TbMotivoAtendimento)
              ├─ Motivos Encerramento  → FrmTbMotivoEnc   (TbMotivoEncerramento)
              ├─ Motivos Visita        → FrmTbMotivoVisita(TbMotivoVisita)
              ├─ Motivos Restauração   → FrmTbMotRestauração
              ├─ Tipo de Ação          → FrmTbTipoAcao    (TbTipoAcao)
              ├─ Tipo de Evento        → FrmTbTipoEvento  (TbTipoEvento)
              ├─ Origem                → FrmTbOrigem      (TbChegouPrograma)
              ├─ Técnicos              → FrmTabTecnicos   (TbTecnico)
              └─ Órgãos                → FrmTabOrgão      (TbOrgao)
```

---

## 3. Tabelas x Formulários (RecordSource mapeado)

| Formulário                  | Tabela / Query principal              | Operação       |
|-----------------------------|---------------------------------------|----------------|
| Frmentrada                  | TbTecnico                             | Autenticação   |
| FrmCadCaso / FrmATuCaso     | TbCIAPPICaso                          | CRUD Caso      |
| FrmCadUsuarioNovo           | TbCIAPPIUsuario                       | INSERT Usuário |
| FrmCadUsuarioExistente      | TbCIAPPIUsuario                       | UPDATE Usuário |
| FrmAtuPessoa                | TbCIAPPIUsuario                       | UPDATE Usuário |
| FrmCadAcomp / FrmAtuAcomp   | TbCIAPPIAcompanhamento                | CRUD Acomp.    |
| FrmCadILPI / FrmAtuEnt      | TbCIAPPIILPI                          | CRUD ILPI      |
| FrmCadVisitaEnt             | TBAcompEntidade                       | INSERT Visita  |
| FrmAtuRelVisitaEnt          | TBAcompEntidade                       | UPDATE Visita  |
| FrmVisitaInst / FrmAtuVisitaInst | TbVisitaInst                     | CRUD VisitaInst|
| FrmCadEvento / FrmAtuEvento | TbEvento                              | CRUD Evento    |
| SubFrmAcomp                 | TbCIAPPIAcompanhamento                | Sub-listagem   |
| SubFrmUsuario               | TBCasoUsuario                         | Sub-listagem   |
| FrmConsultaBairro           | CnBairroTotal (query)                 | Consulta       |
| FrmTabTecnicos              | TbTecnico                             | CRUD Técnico   |
| FrmTabOrgão                 | TbOrgao                               | CRUD Órgão     |
| FrmTbMotivo                 | TbMotivoAtendimento                   | CRUD Tabela    |
| FrmTbMotivoEnc              | TbMotivoEncerramento                  | CRUD Tabela    |
| FrmTbMotivoVisita           | TbMotivoVisita                        | CRUD Tabela    |
| FrmTbOrigem                 | TbChegouPrograma                      | CRUD Tabela    |
| FrmTbTipoAcao               | TbTipoAcao                            | CRUD Tabela    |
| FrmTbTipoEvento             | TbTipoEvento                          | CRUD Tabela    |

---

## 4. Validações Identificadas (LostFocus → regras de negócio)

### FrmCadCaso / FrmATuCaso
- `TbCasoNumCaso` — obrigatório, único
- `TbCasoDtinicio` — obrigatório
- `tbnomeidoso` — obrigatório, convertido para MAIÚSCULAS
- `TbCasoMotivoAtendimento` — obrigatório
- `TbCasoChegouPrograma` — obrigatório
- `TbCasoRelato` — obrigatório (síntese)
- `TbCasoTecnicoResp` — obrigatório
- Encerramento: requer `TbCasoDtencer` + `TbCasoMotivoEncerramento` juntos

### FrmCadAcomp / FrmAtuAcomp
- `TbAcomCaso` — obrigatório, deve existir em TbCIAPPICaso
- `TbAcompdata` — obrigatório, não pode ser maior que hoje
- `TbAcompAcao` — obrigatório (tipo de ação)
- `TbCaraterAtendimento` — obrigatório
- `TbRelato` — obrigatório
- `TbTecnicoResponsavel` — obrigatório
- `TbAcompPrazo` — se informado, não pode ser menor que hoje
- Se ação = encaminhamento → `TbAcompOrgao` obrigatório
- Se salvar com status "ouvidoria" → abre `FrmEncerraOuvidoria`

### FrmCadUsuarioNovo / FrmAtuPessoa
- `TbCaso` — obrigatório, deve existir em TbCIAPPICaso
- `TbDtCadastro` — obrigatório, não pode ser maior que hoje
- `TbNome` — obrigatório, convertido para MAIÚSCULAS
- `TbSexo` — obrigatório
- `TbIdade` — obrigatório (ou data de nascimento)
- `TbTecnicoResponsavel` — obrigatório

### FrmCadILPI / FrmAtuEnt
- `NOMEILPI`, `RESPONSAVELILPI`, `LOGRADOURO`, `BAIRRO`, `MUNICIPIO` — obrigatórios, em MAIÚSCULAS
- `TIPOENTIDADE` — obrigatório
- `CAPACIDADEIDOSOS`, `IDOSOSRESIDENTES` — obrigatórios

### Login (Frmentrada)
- Técnico + Senha conferem na TbTecnico
- `TbNivel = 1` → abre FrmMenuMonitoramento (acesso restrito)
- `TbNivel > 1` → abre FrmMenuPrincipal (acesso completo)
- `TbStatus = "Bloqueado"` → mensagem de bloqueio

---

## 5. Estrutura Proposta para FastAPI + Frontend Python

```
ciappi_api/
├── app/
│   ├── main.py                    # FastAPI app, CORS, routers
│   ├── database.py                # SQLAlchemy engine + Session
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── caso.py                # TbCIAPPICaso
│   │   ├── usuario.py             # TbCIAPPIUsuario
│   │   ├── acompanhamento.py      # TbCIAPPIAcompanhamento
│   │   ├── ilpi.py                # TbCIAPPIILPI
│   │   ├── evento.py              # TbEvento
│   │   ├── visita_inst.py         # TbVisitaInst
│   │   ├── tecnico.py             # TbTecnico
│   │   ├── orgao.py               # TbOrgao
│   │   └── tabelas_aux.py         # TbMotivoAtendimento, TbTipoAcao, etc.
│   ├── schemas/                   # Pydantic schemas (request/response)
│   │   ├── caso.py
│   │   ├── usuario.py
│   │   ├── acompanhamento.py
│   │   ├── ilpi.py
│   │   ├── evento.py
│   │   └── auth.py
│   ├── routers/                   # Endpoints agrupados por domínio
│   │   ├── auth.py                # POST /login
│   │   ├── casos.py               # GET/POST/PUT /casos
│   │   ├── usuarios.py            # GET/POST/PUT /usuarios
│   │   ├── acompanhamentos.py     # GET/POST/PUT /acompanhamentos
│   │   ├── ilpis.py               # GET/POST/PUT /ilpis
│   │   ├── eventos.py             # GET/POST/PUT /eventos
│   │   ├── visitas.py             # GET/POST/PUT /visitas
│   │   ├── ouvidoria.py           # GET/POST/PUT /ouvidoria
│   │   ├── relatorios.py          # GET /relatorios/* (consultas)
│   │   └── tabelas.py             # GET/POST/PUT /tabelas/* (listas auxiliares)
│   ├── services/                  # Lógica de negócio (validações do VBA)
│   │   ├── caso_service.py
│   │   ├── acomp_service.py
│   │   └── auth_service.py
│   └── core/
│       ├── security.py            # JWT / autenticação
│       └── config.py              # Env vars
│
ciappi_frontend/                   # Frontend Python (Streamlit ou NiceGUI)
├── pages/
│   ├── 01_login.py
│   ├── 02_menu_principal.py
│   ├── 03_casos.py
│   ├── 04_usuarios.py
│   ├── 05_acompanhamentos.py
│   ├── 06_ilpis.py
│   ├── 07_eventos.py
│   ├── 08_visitas.py
│   ├── 09_ouvidoria.py
│   ├── 10_relatorios.py
│   └── 11_tabelas_admin.py
└── components/
    ├── forms/
    └── tables/
```

---

## 6. Endpoints FastAPI sugeridos

### Autenticação
- `POST /auth/login` — valida TbNomeTecnico + TbSenha, retorna JWT + nível de acesso

### Casos
- `GET /casos` — lista com filtros (município, status, técnico)
- `GET /casos/{num_caso}` — detalhe completo do caso
- `POST /casos` — criar novo caso
- `PUT /casos/{num_caso}` — atualizar (inclusive encerramento)
- `PUT /casos/{num_caso}/restaurar` — restaurar caso encerrado

### Usuários (pessoas atendidas)
- `GET /usuarios` — lista
- `GET /usuarios/{id}` — detalhe
- `POST /usuarios` — novo cadastro (novo ou vinculado a caso existente)
- `PUT /usuarios/{id}` — atualizar

### Acompanhamentos
- `GET /acompanhamentos` — lista por caso
- `GET /acompanhamentos/{id}` — detalhe
- `POST /acompanhamentos` — incluir
- `PUT /acompanhamentos/{id}` — atualizar

### ILPIs
- `GET /ilpis` — lista
- `GET /ilpis/{id}` — detalhe
- `POST /ilpis` — cadastrar
- `PUT /ilpis/{id}` — atualizar

### Eventos
- `GET /eventos` — lista
- `POST /eventos` — cadastrar
- `PUT /eventos/{id}` — atualizar

### Visitas
- `GET /visitas/inst` — visitas institucionais
- `GET /visitas/ilpi` — visitas a ILPIs
- `POST /visitas/inst` — registrar
- `PUT /visitas/inst/{id}` — atualizar

### Ouvidoria
- `GET /ouvidoria/avencer` — casos com prazo próximo
- `GET /ouvidoria/concluidas` — encerradas
- `PUT /ouvidoria/{caso_id}/encerrar` — encerrar

### Relatórios
- `GET /relatorios/acompanhamentos` — com filtro de período
- `GET /relatorios/violencia` — por tipo e bairro
- `GET /relatorios/encerrados` — com filtro
- `GET /relatorios/municipio` — distribuição por município
- `GET /relatorios/faixa-etaria`
- `GET /relatorios/origem`
- `GET /relatorios/eventos`

### Tabelas Auxiliares (admin)
- `GET/POST/PUT /tabelas/motivos-atendimento`
- `GET/POST/PUT /tabelas/motivos-encerramento`
- `GET/POST/PUT /tabelas/tipo-acao`
- `GET/POST/PUT /tabelas/tipo-evento`
- `GET/POST/PUT /tabelas/origem`
- `GET/POST/PUT /tabelas/tecnicos`
- `GET/POST/PUT /tabelas/orgaos`

---

## 7. Regras de Negócio Críticas (derivadas do VBA)

1. **Login por nível**: Nível 1 → acesso somente leitura/monitoramento. Nível 2+ → acesso completo.
2. **Encerramento de caso**: Requer data + motivo de encerramento preenchidos simultaneamente.
3. **Restauração de caso**: Requer motivo de restauração (tabela `TbMotivoRestauração`).
4. **Acompanhamento com encaminhamento**: Campo `TbAcompOrgao` torna-se obrigatório.
5. **Ouvidoria**: Se um acompanhamento aciona ouvidoria, abre fluxo de encerramento com prazo.
6. **Datas**: Nenhuma data de registro pode ser futura (exceto campo `Prazo`).
7. **Prazo de acompanhamento**: Se informado, deve ser ≥ hoje.
8. **Nomes em MAIÚSCULAS**: `tbnomeidoso`, `NOMEILPI`, `RESPONSAVELILPI`, `TbNome`, logradouros.
9. **Número do caso é único**: Validar antes de salvar em `TbCIAPPICaso`.
10. **Vínculo caso–usuário**: Usuário só pode ser cadastrado se o número do caso já existir.

---

## 8. Pasta de arquivos organizados

```
vba_organizado/
├── 01_entrada_navegacao/    (11 arquivos) — menus e login
├── 02_cadastros/            (9 arquivos)  — formulários de criação
├── 03_atualizacao/          (8 arquivos)  — formulários de edição
├── 04_selecao_busca/        (13 arquivos) — telas de busca/seleção antes de editar
├── 05_consulta_relatorio/   (30 arquivos) — consultas com filtro de período
├── 06_relatorios_impressos/ (23 arquivos) — relatórios Access + queries SQL
├── 07_ouvidoria/            (8 arquivos)  — módulo de ouvidoria
├── 08_subforms/             (3 arquivos)  — subformulários embarcados
├── 09_tabelas_auxiliares/   (9 arquivos)  — CRUD de listas de apoio
└── 10_outros/               (3 arquivos)  — testes/protótipos
```
