# CIAPPI — Análise de Migração Access → Python

> Documento gerado em 30/03/2026 a partir da leitura dos arquivos VBA exportados do banco Access original e do código Python atual.

---

## 1. SQLs Encontrados no Access (RecordSource / RowSource)

Esta seção lista todas as queries SQL reais encontradas nos formulários e relatórios do Access. São os dados que o sistema consultava para exibir informações ao usuário.

---

### 1.1 Autenticação (Frmentrada)

```sql
-- RecordSource do formulário de login
SELECT TbTecnico.TbNomeTecnico, TbTecnico.TbSenha, TbTecnico.TbNivel,
       TbTecnico.TbStatus, TbTecnico.TbDataSaída
FROM TbTecnico
WHERE TbTecnico.TbStatus = "Ativo"
```

**Lógica VBA:**
- Compara nome + senha diretamente na tabela
- Se `TbNivel = 1` → abre `FrmMenuMonitoramento` (acesso restrito)
- Se `TbNivel > 1` → abre `FrmMenuPrincipal` (acesso completo)
- Se `TbStatus = "Bloqueado"` → exibe "Usuário bloqueado. Procure a Coordenação"

---

### 1.2 Casos

#### Listagem de casos ativos (para seleção/busca)
```sql
-- FrmSelAtuCaso — busca por nome do idoso entre casos abertos
SELECT TbCIAPPICaso.TbCasoNumCaso, TbCIAPPICaso.tbnomeidoso
FROM TbCIAPPICaso
WHERE TbCIAPPICaso.tbnomeidoso LIKE [txtpesq] & "*"
  AND TbCIAPPICaso.TbCasoDtencer IS NULL
ORDER BY TbCIAPPICaso.tbnomeidoso
```

#### Listagem de casos para restauração
```sql
-- FrmSelRestaura — busca casos encerrados (para restaurar)
SELECT TbCIAPPICaso.TbCasoNumCaso, TbCIAPPICaso.tbnomeidoso
FROM TbCIAPPICaso
WHERE TbCIAPPICaso.tbnomeidoso LIKE [txtpesq] & "*"
  AND TbCIAPPICaso.TbCasoDtencer IS NOT NULL
ORDER BY TbCIAPPICaso.tbnomeidoso
```

#### Consulta completa do caso
```sql
-- FrmCasoCompleto — detalhe completo de um caso
SELECT TbCIAPPICaso.TbCasoNumCaso, TbCIAPPICaso.TbCasoDtinicio,
       TbCIAPPICaso.tbnomeidoso, TbCIAPPICaso.TbCasoMotivoAtendimento,
       TbCIAPPICaso.TbCasoChegouPrograma, TbCIAPPICaso.TbCasoMotivoEncerramento,
       TbCIAPPICaso.TbCasoDtencer, TbCIAPPICaso.TbCasoTecnicoResp
FROM TbCIAPPICaso
WHERE TbCIAPPICaso.TbCasoNumCaso = [filtro por número]
```

#### RecordSource do formulário de cadastro/atualização de caso
```sql
SELECT TbCIAPPICaso.TbCasoNumCaso, TbCIAPPICaso.TbCasoDtinicio,
       TbCIAPPICaso.TbCasoMotivoAtendimento, TbCIAPPICaso.TbCasoChegouPrograma,
       TbCIAPPICaso.TbCasoRelato, TbCIAPPICaso.TbCasoTecnicoResp,
       TbCIAPPICaso.TbCasoNumInquerito, TbCIAPPICaso.TbCasoDtencer,
       TbCIAPPICaso.TbObservações, TbCIAPPICaso.TbCasoMotivoEncerramento,
       TbCIAPPICaso.TbCasoAvaliacaoUsuario, TbCIAPPICaso.tbnomeidoso,
       TbCIAPPICaso.TbCasoMunicipio, TbCIAPPICaso.Tbambienteviolencia,
       TbCIAPPICaso.TbNumDenuncia, TbCIAPPICaso.TbPrazoOuvidoria,
       TbCIAPPICaso.TbNumOfOuvidoria
FROM TbCIAPPICaso
```

---

### 1.3 Usuários (Pessoas Atendidas)

#### Busca de usuário por nome
```sql
-- FrmSelAtuPessoa
SELECT TbCIAPPIUsuario.TbCaso, TbCIAPPIUsuario.TbNome
FROM TbCIAPPIUsuario
WHERE TbCIAPPIUsuario.TbNome LIKE [txtpesq] & "*"
ORDER BY TbCIAPPIUsuario.TbNome
```

#### Busca de usuário para incluir pessoa em caso existente
```sql
-- FrmSelIncPessoa
SELECT TbCIAPPIUsuario.TbNumeroCadastro, TbCIAPPIUsuario.TbNome
FROM TbCIAPPIUsuario
WHERE TbCIAPPIUsuario.TbNome LIKE [txtpesq] & "*"
ORDER BY TbCIAPPIUsuario.TbNome
```

#### RecordSource completo do cadastro de usuário
O formulário de cadastro traz **todos os campos** de `TbCIAPPIUsuario`:

| Grupo | Campos |
|-------|--------|
| Identificação | TbNumeroCadastro, TbDtCadastro, TbNome, TbNomeSocial, TbNomePai, TbNomeMae |
| Documentos | TbCPF, TbRGNumero, TbOrgaoemissor, TbUFEmissor, TbDtExpedicao, TbCTPS, TbSerieCTPS, TbNIS |
| Dados pessoais | TbDtNascimento, TbIdade, TbSexo, TbOrientacaoSexual, TbIdentidadeSexual, TbRacaCor |
| Saúde | TbDeficiente, TbDeficiencia, TbUsuarioDrogas, TbTipoDrogas, TbHIV, TbUsoPreservativo, TbDoençaCronica, TbDoença, TbMedicamentoContínuo, TbMedicamentos, TbMonitoraSaude, TbFrequenciaExame |
| Situação social | TbEgresso, TbMoradorRua, TbSitMoradia, TbNumPessoasCasa, TbVínculoFamiliar |
| Endereço | TbLogradouro, TbNumero, TbComplemento, TbBairro, TbMunicipio, TbUF, TbCEPRes, TbPontodeReferencia, TbFone, TbCelular, Tbemail |
| Família | TbEstadoCivil, TbSituacaoConujugal, TbNumFilhos |
| Trabalho/Renda | TbOcupacao, TbSitProfissional, TbRegistroCTPS, TbPrevidencia, TbInteresseTrabalho, TbHabilidades1/2/3, TbExperiencia1/2/3, TbFaixaRenda, TbRendaFamiliar, TbBeneficioSocial |
| Educação | TbEscolaridade, TbEstudante |
| Outros | TbNacionalidade, TbNaturalidade, TbReligião, TbOutroServiço, TbTecnicoResponsavel |

---

### 1.4 Acompanhamentos

#### Busca de acompanhamento por nome do idoso
```sql
-- FrmSelAtuAComp
SELECT TbCIAPPIAcompanhamento.tbcodigo, TbCIAPPICaso.TbCasoNumCaso,
       TbCIAPPICaso.tbnomeidoso, TbCIAPPIAcompanhamento.TbAcompdata,
       TbCIAPPIAcompanhamento.TbAcompAcao
FROM TbCIAPPICaso
INNER JOIN TbCIAPPIAcompanhamento
  ON TbCIAPPICaso.TbCasoNumCaso = TbCIAPPIAcompanhamento.TbAcomCaso
WHERE TbCIAPPICaso.tbnomeidoso LIKE [txtpesq] & "*"
  AND TbCIAPPICaso.TbCasoDtencer IS NULL
ORDER BY TbCIAPPICaso.tbnomeidoso, TbCIAPPIAcompanhamento.TbAcompdata DESC
```

#### RecordSource do formulário de acompanhamento
```sql
SELECT TbCIAPPIAcompanhamento.TbAcomCaso, TbCIAPPIAcompanhamento.TbAcompdata,
       TbCIAPPIAcompanhamento.TbAcompOrgao, TbCIAPPIAcompanhamento.TbAcompAcao,
       TbCIAPPIAcompanhamento.TbAcompStatus, TbCIAPPIAcompanhamento.TbAcompPrazo,
       TbCIAPPIAcompanhamento.TbCaraterAtendimento, TbCIAPPIAcompanhamento.TbRelato,
       TbCIAPPIAcompanhamento.TbTecnicoResponsavel, TbCIAPPIAcompanhamento.tbcodigo
FROM TbCIAPPIAcompanhamento
```

#### RowSources dos combos do acompanhamento
```sql
-- Tipo de ação
SELECT TbTipoAcao.DescricaoAcao, TbTipoAcao.CodAção
FROM TbTipoAcao ORDER BY TbTipoAcao.DescricaoAcao

-- Técnico responsável
SELECT TbTecnico.TbNomeTecnico FROM TbTecnico

-- Órgão de encaminhamento
SELECT TbOrgao.TbNomeOrgao FROM TbOrgao ORDER BY TbOrgao.TbNomeOrgao
```

#### Caráter de atendimento (ValueList — hardcoded)
```
"Jurídico"; "Psicológico"; "Social"
```

---

### 1.5 ILPIs

#### Busca de ILPI por nome
```sql
-- FrmSelAtuEnt
SELECT TbCIAPPIILPI.CODIGOILPI, TbCIAPPIILPI.NOMEILPI, TbCIAPPIILPI.DATACADASTRO
FROM TbCIAPPIILPI
WHERE TbCIAPPIILPI.NOMEILPI LIKE [txtpesq] & "*"
```

#### RecordSource completo da ILPI
```sql
SELECT DATACADASTRO, NOMEILPI, RESPONSAVELILPI, DATAVISITA, MOTIVOVISITA,
       CAPACIDADEIDOSOS, IDOSOSRESIDENTES, FONEFIXO, CELULAR, LOGRADOURO,
       NUMEROIMOVEL, COMPLEMENTO, BAIRRO, MUNICIPIO, PONTODEREFERENCIA,
       TIPOENTIDADE, PERSONALIDADEJURIDICA, TIPOPUBLICO, CODIGOILPI,
       STATUS, AVALIACAO
FROM TbCIAPPIILPI
```

#### ValueLists dos combos da ILPI
```
TIPOENTIDADE:        "Centro de Convivência"; "ILPI"
PERSONALIDADEJURIDICA: "FILANTRÓPICA"; "PRIVADA"; "PÚBLICA"
TIPOPUBLICO:         "FEMININO"; "MASCULINO"; "MISTO"
STATUS:              "Em Funcionamento"; "Interditada"; "Encerrada"; "Atendimento Suspenso"
AVALIACAO:           "BOA"; "REGULAR"; "DEFICIENTE"
```

---

### 1.6 Visitas a Entidades (ILPIs)

#### Visitas agendadas (sem data de realização)
```sql
-- FrmSelAgenVisita — agendamentos pendentes
SELECT TBAcompEntidade.Codigoentidade, TBAcompEntidade.nomeentidade,
       TBAcompEntidade.dtprevistavisita, TBAcompEntidade.dtvisita
FROM TBAcompEntidade
WHERE TBAcompEntidade.dtvisita IS NULL
ORDER BY TBAcompEntidade.dtprevistavisita
```

#### Visitas realizadas (com data de realização)
```sql
-- FrmSelAtuRelEnt
SELECT TBAcompEntidade.Codigoentidade, TBAcompEntidade.nomeentidade,
       TBAcompEntidade.dtvisita
FROM TBAcompEntidade
WHERE TBAcompEntidade.nomeentidade LIKE [txtpesq] & "*"
  AND TBAcompEntidade.dtvisita IS NOT NULL
```

---

### 1.7 Visitas Institucionais

```sql
-- FrmSelAtuVisitaINst
SELECT TbVisitaInst.codigovisita, TbVisitaInst.nomeinstituicao, TbVisitaInst.datavisita
FROM TbVisitaInst
WHERE TbVisitaInst.nomeinstituicao LIKE [Forms]![FrmSelAtuvisitainst].[txtpesq] & "*"
```

---

### 1.8 Eventos

```sql
-- FrmSelecionaEvento
SELECT TbEvento.Código, TbEvento.tbnomeevento, TbEvento.Tbdataprevista
FROM TbEvento
```

#### RowSources dos combos do evento
```sql
-- Município
SELECT TbMunicipio.município FROM TbMunicipio ORDER BY município

-- Técnico
SELECT TbTecnico.CodTecnico, TbTecnico.TbNomeTecnico FROM TbTecnico ORDER BY TbNomeTecnico

-- Tipo de evento
SELECT TbTipoEvento.tipoevento FROM TbTipoEvento
```

---

### 1.9 Ouvidoria

#### Casos com prazo a vencer
```sql
-- Query: CnPrazoOuvidoriaAVencer (usada em FrmCnOuvidoriaAVencer)
SELECT TbCasoNumCaso, TbCasoDtinicio, TbPrazoOuvidoria,
       TbCasoMunicipio, TbNumDenuncia, TbCasoTecnicoResp
FROM CnPrazoOuvidoriaAVencer
ORDER BY TbPrazoOuvidoria
-- CnPrazoOuvidoriaAVencer é uma query salva no Access (não exportada diretamente)
-- Equivale a: WHERE TbPrazoOuvidoria IS NOT NULL AND TbEncerradoOuvidoria IS NULL
--             AND TbPrazoOuvidoria >= Date() -- "a vencer" (prazo futuro)
```

#### Casos com prazo vencido
```sql
-- CnPrazoOuvidoriaVencido
SELECT TbCasoNumCaso, TbCasoDtinicio, TbPrazoOuvidoria,
       TbCasoMunicipio, TbCasoTecnicoResp
FROM CnPrazoOuvidoriaVencido
ORDER BY TbPrazoOuvidoria
-- Equivale a: WHERE TbPrazoOuvidoria IS NOT NULL AND TbEncerradoOuvidoria IS NULL
--             AND TbPrazoOuvidoria < Date() -- prazo já vencido
```

#### Ouvidorias concluídas
```sql
-- CnOuvidoriaConcluidas
SELECT TbCasoNumCaso, TbCasoDtinicio, TbCasoTecnicoResp, TbCasoMunicipio
FROM CnOuvidoriaConcluidas
-- Equivale a: WHERE TbEncerradoOuvidoria = "Sim"
```

#### Casos de Ouvidoria (lista ativa — Frmambiente)
```sql
-- Frmambiente: lista casos da Ouvidoria da SJDH ainda ativos após set/2019
SELECT TbCasoNumCaso, TbCasoRelato, TbCasoDtinicio, tbnomeidoso,
       TbCasoDtencer, TbNumDenuncia, TbPrazoOuvidoria, TbNumOfOuvidoria,
       TbEncerradoOuvidoria, TbDtEncerradoOuvidoria, TbCasoChegouPrograma,
       TbCasoTecnicoResp
FROM TbCIAPPICaso
WHERE TbCIAPPICaso.TbCasoDtinicio > #9/30/2019#
  AND TbCIAPPICaso.TbCasoDtencer IS NULL
  AND TbCIAPPICaso.TbCasoChegouPrograma = "OUvidoria da SJDH"
ORDER BY TbCIAPPICaso.TbCasoDtinicio
```

> **⚠️ Gap crítico:** a query acima tem um filtro fixo de data (`> set/2019`) e filtra por `TbCasoChegouPrograma = "OUvidoria da SJDH"`. Isso não está implementado na API Python atual. O endpoint `/ouvidoria/avencer` não distingue "a vencer" de "vencido" e não faz essa filtragem por origem.

---

### 1.10 Relatórios — Queries do Access

#### Acompanhamentos por período (base das 3 queries encadeadas)
```sql
-- CnAcomp11: filtra acompanhamentos por intervalo de datas
SELECT TbAcompdata, TbCaraterAtendimento, TbAcompAcao
FROM TbCIAPPIAcompanhamento
WHERE TbAcompdata BETWEEN [dt_inicial] AND [dt_final]

-- CnAcomp12: agrega por caráter de atendimento
SELECT TbCaraterAtendimento AS Expr1,
       Count(TbCaraterAtendimento) AS ContarDeTbCaraterAtendimento
FROM CnAcomp11
GROUP BY TbCaraterAtendimento

-- CnAcomp13: agrega por tipo de ação
SELECT TbAcompAcao AS Expr1,
       Count(TbAcompAcao) AS ContarDeTbAcompAcao
FROM CnAcomp11
GROUP BY TbAcompAcao
```

#### Relatório de Casos Ativos (RelCasoAtivo)
```sql
-- RecordSource: CnCasoAtivo (query salva)
-- Colunas usadas: TbCasoNumCaso, TbCasoDtinicio, tbnomeidoso,
--                 ÚltimoDeTbAcompAcao, ÚltimoDeTbAcompdata,
--                 TbCIAPPICaso.TbCasoTecnicoResp
-- Rodapé: Count(*) — total de casos ativos
```

#### Relatório de Casos Parados (RelCasosParados)
```sql
-- RecordSource: CnParados (query salva — casos sem acomp. há N dias)
-- Colunas: TbCasoNumCaso, TbCasoDtinicio, tbnomeidoso,
--          TbCasoMotivoAtendimento, ÚltimoDeTbAcompAcao, ÚltimoDeTbAcompdata
```

#### Relatório de Casos Encerrados com Resolutividade (RelEncResol)
```sql
-- RecordSource: CnEncerradoResolutividade
-- Colunas: TbCasoNumCaso, tbnomeidoso, TbCasoDtencer, TbCasoMotivoAtendimento
```

#### Relatório de Municípios (relmunicipioidoso)
```sql
-- FrmMunicipioIdoso / FrmIntDatamunicipio → OpenReport "relmunicipioidoso"
SELECT CnMunicipio2.TbMunicipio, CnMunicipio2.SomaDeContarDeTbMunicipio
FROM CnMunicipio2
ORDER BY SomaDeContarDeTbMunicipio DESC
```

#### Relatório de Tipo de Violência por Município
```sql
-- FrmConsultaMotivo
SELECT CnTipoViolência.TbCasoMotivoAtendimento,
       Sum(CnTipoViolência.ContarDeTbCasoMotivoAtendimento) AS SomaDe...
FROM CnTipoViolência
GROUP BY CnTipoViolência.TbCasoMotivoAtendimento
ORDER BY CnTipoViolência.TbCasoMotivoAtendimento
```

#### Relatório de Violência por Bairro
```sql
-- FrmConsultaBairro (RecordSource: CnBairroTotal)
SELECT CnBairroTotal.TbBairro, CnBairroTotal.ContarDeContarDeTbBairro AS Expr1
FROM CnBairroTotal
```

#### Relatório de Origem
```sql
-- FrmIntDataOrigem → OpenReport "RelOrigem"
-- Agrupa casos por TbCasoChegouPrograma
```

#### Relatório de Encaminhamentos
```sql
-- FrmConEncaminhamento
SELECT CnUltMovimentacao.TbCasoNumCaso, CnUltMovimentacao.tbnomeidoso,
       CnUltMovimentacao.TbAcompdata, CnUltMovimentacao.TbAcompOrgao
FROM CnUltMovimentacao
ORDER BY TbAcompdata
-- CnUltMovimentacao = última movimentação de cada caso com encaminhamento
```

#### Relatório Acomp. Específico (FrmResultAcompEspec)
```sql
-- RecordSource: CnAcompEspec2
-- Colunas: TbAcompAcao, ContarDeTbAcompAcao
-- Filtro por técnico específico + período (FrmIntDataAcompEspec)
```

---

### 1.11 Tabelas Auxiliares

```sql
-- Motivos de Atendimento
SELECT TbMotivoAtendimento.Código, TbMotivoAtendimento.TbDescricaoMotivo
FROM TbMotivoAtendimento

-- Motivos de Encerramento
SELECT TbMotivoEncerramento.Código, TbMotivoEncerramento.descricaomotivo
FROM TbMotivoEncerramento ORDER BY descricaomotivo

-- Tipos de Ação
SELECT TbTipoAcao.DescricaoAcao, TbTipoAcao.CodAção
FROM TbTipoAcao

-- Tipos de Evento
SELECT TbTipoEvento.tipoevento FROM TbTipoEvento

-- Origem (Como Chegou ao Programa)
SELECT TbChegouPrograma.descricaochegouprograma FROM TbChegouPrograma

-- Técnicos
SELECT TbTecnico.TbNomeTecnico FROM TbTecnico

-- Órgãos
SELECT TbOrgao.TbNomeOrgao FROM TbOrgao ORDER BY TbNomeOrgao

-- Municípios
SELECT TbMunicipio.município FROM TbMunicipio ORDER BY município

-- Motivos de Visita
-- (TbMotivoVisita — sem SQL explícito, tabela simples)

-- Motivos de Restauração
-- (TbMotivoRestauração — sem SQL explícito, tabela simples)
```

---

## 2. Endpoints FastAPI Atuais

### Implementados

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|--------------|
| POST | `/auth/login` | Login com nome+senha, retorna JWT | Pública |
| GET | `/casos/` | Lista casos com filtros (município, encerrado, técnico) | Nível 1+ |
| GET | `/casos/{num_caso}` | Detalhe de um caso | Nível 1+ |
| POST | `/casos/` | Criar novo caso | Nível 2+ |
| PUT | `/casos/{num_caso}` | Atualizar caso (inclusive encerrar) | Nível 2+ |
| PUT | `/casos/{num_caso}/restaurar` | Restaurar caso encerrado | Nível 2+ |
| GET | `/acompanhamentos/caso/{num_caso}` | Lista acompanhamentos por caso | Nível 1+ |
| GET | `/acompanhamentos/{codigo}` | Detalhe de um acompanhamento | Nível 1+ |
| POST | `/acompanhamentos/` | Criar acompanhamento | Nível 2+ |
| PUT | `/acompanhamentos/{codigo}` | Atualizar acompanhamento | Nível 2+ |
| GET | `/usuarios/` | Lista usuários | Nível 1+ |
| GET | `/usuarios/{num_cadastro}` | Detalhe de usuário | Nível 1+ |
| POST | `/usuarios/` | Criar usuário | Nível 2+ |
| PUT | `/usuarios/{num_cadastro}` | Atualizar usuário | Nível 2+ |
| GET | `/ilpis/` | Lista ILPIs | Nível 1+ |
| GET | `/ilpis/{codigo}` | Detalhe de ILPI | Nível 1+ |
| POST | `/ilpis/` | Cadastrar ILPI | Nível 2+ |
| PUT | `/ilpis/{codigo}` | Atualizar ILPI | Nível 2+ |
| GET | `/eventos/` | Lista eventos | Nível 1+ |
| GET | `/eventos/{codigo}` | Detalhe de evento | Nível 1+ |
| POST | `/eventos/` | Criar evento | Nível 2+ |
| PUT | `/eventos/{codigo}` | Atualizar evento | Nível 2+ |
| GET | `/visitas/inst` | Lista visitas institucionais | Nível 1+ |
| GET | `/visitas/inst/{codigo}` | Detalhe de visita institucional | Nível 1+ |
| POST | `/visitas/inst` | Registrar visita institucional | Nível 2+ |
| PUT | `/visitas/inst/{codigo}` | Atualizar visita institucional | Nível 2+ |
| GET | `/ouvidoria/avencer` | Casos com prazo de ouvidoria | Nível 1+ |
| GET | `/ouvidoria/concluidas` | Ouvidorias encerradas | Nível 1+ |
| PUT | `/ouvidoria/{num_caso}/encerrar` | Encerrar ouvidoria | Nível 2+ |
| GET | `/relatorios/casos-ativos` | Casos ativos | Nível 1+ |
| GET | `/relatorios/encerrados` | Casos encerrados (filtro por período) | Nível 1+ |
| GET | `/relatorios/municipio` | Casos agrupados por município | Nível 1+ |
| GET | `/relatorios/violencia` | Casos agrupados por tipo de violência | Nível 1+ |
| GET | `/relatorios/origem` | Casos agrupados por origem | Nível 1+ |
| GET | `/relatorios/acompanhamentos` | Acompanhamentos por período | Nível 1+ |
| GET | `/relatorios/eventos` | Eventos por período | Nível 1+ |
| GET | `/tabelas/motivos-atendimento` | Lista motivos de atendimento | Nível 1+ |
| GET | `/tabelas/motivos-encerramento` | Lista motivos de encerramento | Nível 1+ |
| GET | `/tabelas/tipo-acao` | Lista tipos de ação | Nível 1+ |
| GET | `/tabelas/tipo-evento` | Lista tipos de evento | Nível 1+ |
| GET | `/tabelas/origem` | Lista origens | Nível 1+ |
| GET | `/tabelas/orgaos` | Lista órgãos | Nível 1+ |
| GET | `/tabelas/municipios` | Lista municípios | Nível 1+ |
| GET | `/tabelas/tecnicos` | Lista técnicos | Nível 1+ |
| GET | `/tabelas/motivos-visita` | Lista motivos de visita | Nível 1+ |

---

## 3. Gaps de Migração — O que falta implementar

### 3.1 Endpoints completamente ausentes

| Funcionalidade Access | Endpoint Ausente | Prioridade |
|----------------------|------------------|------------|
| Visitas a ILPIs (TBAcompEntidade) | `GET/POST/PUT /visitas/ilpi` | 🔴 Alta |
| Agendamento de visita a ILPI | `GET /visitas/ilpi/agendadas` (sem data realização) | 🔴 Alta |
| Acompanhamento específico por técnico | `GET /relatorios/acomp-por-tecnico` | 🟡 Média |
| Casos parados (sem acomp. há N dias) | `GET /relatorios/casos-parados?dias=N` | 🟡 Média |
| Casos encerrados com resolutividade | `GET /relatorios/encerrados-resolutividade` | 🟡 Média |
| Violência por bairro | `GET /relatorios/violencia-bairro?municipio=X` | 🟡 Média |
| Encaminhamentos (última movimentação) | `GET /relatorios/encaminhamentos` | 🟡 Média |
| Municípios do idoso (ranking) | `GET /relatorios/municipio-idoso` (descending) | 🟡 Média |
| Escolaridade dos atendidos | `GET /relatorios/escolaridade` | 🟢 Baixa |
| Faixa etária | `GET /relatorios/faixa-etaria` | 🟢 Baixa |
| Renda familiar | `GET /relatorios/renda` | 🟢 Baixa |
| Mobilidade | `GET /relatorios/mobilidade` | 🟢 Baixa |
| CRUD tabelas auxiliares (POST/PUT/DELETE) | `/tabelas/*` — só GET implementado | 🔴 Alta |
| Motivos de restauração (tabela aux.) | `/tabelas/motivos-restauracao` | 🟡 Média |
| Relatório visitas ILPI | `GET /relatorios/visitas-ilpi` | 🟡 Média |
| Relatório visitas institucionais | `GET /relatorios/visitas-inst` | 🟡 Média |
| Relatório de eventos | Existe mas sem filtro de período correto | 🟡 Média |
| Ouvidoria vencida (prazo < hoje) | `GET /ouvidoria/vencidas` | 🔴 Alta |
| Ouvidoria "Frmambiente" (lista SJDH) | `GET /ouvidoria/ambiente` | 🟡 Média |

### 3.2 Endpoints existentes com implementação incompleta

#### `/ouvidoria/avencer`
**Access fazia:** `WHERE TbPrazoOuvidoria IS NOT NULL AND TbEncerradoOuvidoria IS NULL AND TbPrazoOuvidoria >= Date()`
**Python faz:** `WHERE TbPrazoOuvidoria IS NOT NULL AND TbEncerradoOuvidoria IS NULL`
**Falta:** filtrar só prazos futuros (`>= hoje`). Atualmente retorna também vencidos.

#### `/relatorios/acompanhamentos`
**Access fazia:** retornava também a contagem por `TbCaraterAtendimento` (Jurídico/Psicológico/Social) e por `TbAcompAcao` (tipo de ação).
**Python faz:** retorna lista raw dos acompanhamentos.
**Falta:** agregações resumidas (contagens por caráter e por tipo de ação).

#### `/relatorios/casos-ativos`
**Access fazia:** incluía a última ação (`ÚltimoDeTbAcompAcao`) e a data do último acompanhamento (`ÚltimoDeTbAcompdata`) com contagem total.
**Python faz:** retorna apenas os campos de `TbCIAPPICaso`.
**Falta:** JOIN com `TbCIAPPIAcompanhamento` para trazer o último acompanhamento.

#### `/relatorios/violencia`
**Access fazia:** filtro por período E agrupamento por bairro (query `CnBairroTotal`).
**Python faz:** agrupa por `TbCasoMotivoAtendimento`.
**Falta:** endpoint separado para violência por bairro (campo `TbCIAPPIUsuario.TbBairro` — cruzamento com usuário).

### 3.3 Modelos incompletos no Python

#### Usuário — campos faltantes no model/schema
O modelo `TbCIAPPIUsuario` no Python provavelmente não tem todos os ~70 campos que o Access gerenciava. Os principais **campos ausentes ou não verificados**:

- `TbNomeSocial`, `TbNomePai`, `TbNomeMae`
- `TbCPF`, `TbRGNumero`, `TbOrgaoemissor`, `TbUFEmissor`, `TbDtExpedicao`
- `TbCTPS`, `TbSerieCTPS`, `TbNIS`
- `TbOrientacaoSexual`, `TbIdentidadeSexual`, `TbRacaCor`
- `TbDeficiente`, `TbDeficiencia`
- `TbUsuarioDrogas`, `TbTipoDrogas`, `TbHIV`, `TbUsoPreservativo`
- `TbDoençaCronica`, `TbDoença`, `TbMedicamentoContínuo`, `TbMedicamentos`, `TbMonitoraSaude`
- `TbEgresso`, `TbMoradorRua`, `TbSitMoradia`, `TbNumPessoasCasa`
- `TbVínculoFamiliar`, `TbSituacaoConujugal`, `TbNumFilhos`
- `TbFaixaRenda`, `TbRendaFamiliar`, `TbBeneficioSocial`
- `TbHabilidades1/2/3`, `TbExperiencia1/2/3`
- `TbOcupacao`, `TbSitProfissional`, `TbRegistroCTPS`, `TbPrevidencia`, `TbInteresseTrabalho`
- `TbEscolaridade`, `TbEstudante`, `TbFrequenciaExame`
- `TbOutroServiço`

> **Ação necessária:** verificar o `schema.sql` e o model `usuario.py` para confirmar quais campos estão no banco e quais faltam no schema Pydantic.

#### Visita ILPI — tabela `TBAcompEntidade` não migrada
O Access gerenciava visitas a ILPIs através da tabela `TBAcompEntidade` com campos:
`Codigoentidade`, `nomeentidade`, `dtprevistavisita`, `dtvisita`, e provavelmente `motivovisita`, `relato`, `tecnico`.
**No Python:** não existe model, schema, router ou service para `TBAcompEntidade`.

---

## 4. Regras de Negócio Identificadas no VBA

### 4.1 Cadastro de Caso (FrmCadCaso)
- `TbCasoNumCaso` — obrigatório e único (`DCount` antes de salvar)
- `TbCasoDtinicio` — obrigatório
- `tbnomeidoso` — obrigatório, convertido para MAIÚSCULAS
- `TbCasoMotivoAtendimento` — obrigatório
- `TbCasoChegouPrograma` — obrigatório
- `TbCasoRelato` — obrigatório (síntese não pode ficar em branco)
- `TbCasoTecnicoResp` — obrigatório
- `Tbambienteviolencia` — obrigatório (Extrafamiliar / Intrafamiliar)
- ✅ **Implementado** no `caso_service.py`

### 4.2 Atualização/Encerramento de Caso (FrmATuCaso)
- Todos os campos obrigatórios do cadastro continuam obrigatórios
- Encerramento: `TbCasoDtencer` + `TbCasoMotivoEncerramento` devem ser preenchidos juntos
- Se encerrar → cria automaticamente um acompanhamento com `TbAcompAcao = "ENCERRAMENTO DO CASO"`
- ✅ **Validação encerramento implementada** no `caso_service.py`
- ❌ **Acompanhamento automático de encerramento NÃO implementado**

### 4.3 Restauração de Caso (FrmRestaura)
- Requer `motivo_restauracao` (chave da tabela `TbMotivoRestauração`)
- Limpa `TbCasoDtencer`, `TbCasoMotivoEncerramento` e `TbCasoEncerrado`
- ✅ **Implementado** em `caso_service.py`
- ❌ Falta: tabela `TbMotivoRestauração` não tem endpoint GET

### 4.4 Cadastro de Acompanhamento (FrmCadAcomp)
- `TbAcomCaso` — obrigatório; valida se o número do caso existe na `TbCIAPPICaso`
- `TbAcompdata` — obrigatório; não pode ser > hoje
- `TbAcompAcao` — obrigatório
- `TbCaraterAtendimento` — obrigatório (Jurídico / Psicológico / Social)
- `TbRelato` — obrigatório
- `TbTecnicoResponsavel` — obrigatório
- `TbAcompPrazo` — opcional; se preenchido, não pode ser < hoje
- Se `TbAcompAcao = "Encaminhamento para outro órgão"` → `TbAcompOrgao` obrigatório
- Se `TbAcompAcao = "Concluída para Ouvidoria"` → abre `FrmEncerraOuvidoria` automaticamente
- ✅ **A maioria implementada** no `acomp_service.py`
- ❌ **Falta:** gatilho automático para Ouvidoria quando ação = "Concluída para Ouvidoria"

### 4.5 Cadastro de Usuário (FrmCadUsuarioNovo)
- `TbCaso` — obrigatório; deve existir em `TbCIAPPICaso`
- `TbDtCadastro` — obrigatório; não pode ser > hoje
- `TbNome` — obrigatório, em MAIÚSCULAS
- `TbSexo` — obrigatório
- `TbIdade` ou `TbDtNascimento` — pelo menos um obrigatório
- `TbTecnicoResponsavel` — obrigatório
- Ao salvar usuário existente em novo caso: insere em `TbCasoUsuario` (tabela de relacionamento)
- ❌ **Falta verificar** se o model e schema Python cobrem todos esses campos

### 4.6 Cadastro de ILPI (FrmCadILPI)
- `NOMEILPI`, `RESPONSAVELILPI`, `LOGRADOURO`, `BAIRRO`, `MUNICIPIO` — obrigatórios, MAIÚSCULAS
- `TIPOENTIDADE` — obrigatório
- `CAPACIDADEIDOSOS`, `IDOSOSRESIDENTES` — obrigatórios
- ✅ **Implementado** em `ilpis.py`

### 4.7 Evento (FrmCadEvento)
- `DataPrevista` não pode ser < hoje
- ✅ **Implementado parcialmente** em `eventos.py`

### 4.8 Ouvidoria
- Acesso à tela de ouvidoria (Frmambiente) protegido por senha adicional (`FrmSenhaATUOuvidoria`)
- Apenas casos com `TbCasoChegouPrograma = "OUvidoria da SJDH"` são gerenciados no módulo de ouvidoria
- Ao encerrar: preenche `TbEncerradoOuvidoria = "Sim"`, `TbDtEncerradoOuvidoria`, `TbNumOfOuvidoria`
- ✅ **Encerramento implementado** em `ouvidoria.py`
- ❌ **Falta:** distinção entre prazo a vencer vs. prazo vencido

### 4.9 Controle de Acesso por Nível
- Nível 1 (monitoramento): acesso somente leitura — relatórios de acompanhamento específico, eventos, iniciados, encerrados, visitas
- Nível 2+: acesso completo a CRUD
- Menus `FrmMenuTabela` e `FrmSenhaATUOuvidoria` têm **senha adicional** além do nível
- ✅ **Nível implementado** via `require_nivel()` no backend
- ❌ **Falta:** senha adicional para módulo de tabelas e ouvidoria

---

## 5. Queries Auxiliares Salvas no Access (Não Exportadas Diretamente)

Essas queries eram salvas no Access como objetos internos e referenciadas pelos formulários. Precisam ser recriadas como queries SQLAlchemy ou raw SQL no Python:

| Query Access | Equivalente Python necessário |
|-------------|-------------------------------|
| `CnAcomp11` | Acompanhamentos filtrados por período |
| `CnAcomp12` | `GROUP BY TbCaraterAtendimento COUNT(*)` |
| `CnAcomp13` | `GROUP BY TbAcompAcao COUNT(*)` |
| `CnCasoAtivo` | Casos ativos + último acompanhamento (JOIN) |
| `CnParados` | Casos sem acompanhamento há N dias |
| `CnEncerradoResolutividade` | Casos encerrados com motivo de encerramento |
| `CnPrazoOuvidoriaAVencer` | Casos com prazo futuro e ouvidoria aberta |
| `CnPrazoOuvidoriaVencido` | Casos com prazo passado e ouvidoria aberta |
| `CnOuvidoriaConcluidas` | Casos com ouvidoria encerrada |
| `CnEncerraOuvidoria` | Dados para o form de encerramento de ouvidoria |
| `CnTipoViolência` | Casos agrupados por tipo de violência |
| `CnBairroTotal` | Casos agrupados por bairro (via TbCIAPPIUsuario) |
| `CnMunicipiototal` | Casos agrupados por município |
| `CnMunicipio2` | Ranking de municípios (ORDER BY total DESC) |
| `CnUltMovimentacao` | Última ação de cada caso com encaminhamento |
| `CnAcompEspec2` | Acompanhamentos por técnico específico |
| `CnAcompEspec` (base) | Filtro por técnico + período |

---

## 6. Tabelas do Banco — Mapeamento Completo

| Tabela Access | Modelo Python | Status |
|--------------|---------------|--------|
| TbCIAPPICaso | `app/models/caso.py` | ✅ Implementado |
| TbCIAPPIAcompanhamento | `app/models/acompanhamento.py` | ✅ Implementado |
| TbCIAPPIUsuario | `app/models/usuario.py` | ⚠️ Parcial (campos faltantes) |
| TbCIAPPIILPI | `app/models/ilpi.py` | ✅ Implementado |
| TbEvento | `app/models/evento.py` | ✅ Implementado |
| TbVisitaInst | `app/models/visita_inst.py` | ✅ Implementado |
| TbTecnico | `app/models/tecnico.py` | ✅ Implementado |
| TbOrgao | `app/models/tabelas_aux.py` | ✅ Implementado |
| TbMotivoAtendimento | `app/models/tabelas_aux.py` | ✅ Implementado |
| TbMotivoEncerramento | `app/models/tabelas_aux.py` | ✅ Implementado |
| TbMotivoVisita | `app/models/tabelas_aux.py` | ✅ Implementado |
| TbTipoAcao | `app/models/tabelas_aux.py` | ✅ Implementado |
| TbTipoEvento | `app/models/tabelas_aux.py` | ✅ Implementado |
| TbChegouPrograma | `app/models/tabelas_aux.py` | ✅ Implementado |
| TbMunicipio | `app/models/tabelas_aux.py` | ✅ Implementado |
| TBAcompEntidade | ❌ Não existe | ❌ Falta implementar |
| TbCasoUsuario | ❌ Não existe | ❌ Verificar se necessário |
| TbMotivoRestauração | `app/models/tabelas_aux.py` | ⚠️ Modelo existe? Verificar |

---

## 7. Priorização de Tarefas de Migração

### 🔴 Crítico (bloqueia funcionalidade essencial)

1. **Tabela `TBAcompEntidade` (Visitas a ILPIs)** — o módulo Entidades do Access gerenciava agendamento e registro de visitas a ILPIs. Sem isso, um módulo inteiro está incompleto.

2. **CRUD de tabelas auxiliares (POST/PUT)** — o menu de tabelas do Access permitia CRUD completo. O Python só tem GET. Administradores não conseguem cadastrar novos motivos, tipos de ação, etc.

3. **Distinção Ouvidoria a vencer vs. vencida** — o Access tinha relatórios distintos. O endpoint `/ouvidoria/avencer` não filtra por data.

4. **Acompanhamento automático no encerramento** — o Access criava um registro em `TbCIAPPIAcompanhamento` com `TbAcompAcao = "ENCERRAMENTO DO CASO"` ao encerrar. Isso é auditoria essencial.

### 🟡 Importante (funcionalidade relevante)

5. **Relatório de Casos Ativos com último acompanhamento** — inclui JOIN com último acomp.
6. **Relatório de Casos Parados** — casos sem acomp. há N dias.
7. **Relatório de Acompanhamentos com agregações** — contagem por caráter e tipo de ação.
8. **Gatilho ouvidoria no acompanhamento** — quando tipo de ação = "Concluída para Ouvidoria".
9. **Verificar campos do modelo Usuário** — comparar `schema.sql` com campos do Access.
10. **Relatório de Encaminhamentos** — última movimentação com órgão destino.

### 🟢 Desejável (melhoria ou relatório secundário)

11. Relatório de violência por bairro
12. Relatórios de perfil (escolaridade, faixa etária, renda, mobilidade)
13. Relatório visitas institucionais e visitas ILPI
14. Senha adicional para módulo de tabelas
15. Tabela `TbMotivoRestauração` com endpoint GET
