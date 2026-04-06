# CIAPPI Backend

API REST do sistema de gerenciamento de casos do **CIAPPI** (Centro Integrado de Atenção e Proteção à Pessoa Idosa), vinculado à Secretaria de Justiça, Direitos Humanos e Funcionais (SJDH) de Pernambuco.

O sistema foi migrado de Microsoft Access para Python/FastAPI, mantendo compatibilidade com o banco de dados MySQL legado.

---

## Funcionalidades

- Cadastro e acompanhamento de casos de violação de direitos de idosos
- Registro de acompanhamentos e intervenções por caso
- Gerenciamento de perfis de idosos atendidos
- Controle de prazos da ouvidoria da SJDH
- Registro de visitas a ILPIs (Instituições de Longa Permanência para Idosos)
- Registro de visitas institucionais a órgãos parceiros
- Cadastro e acompanhamento de eventos (capacitações, reuniões, oficinas)
- Exportação de relatórios em CSV
- Controle de acesso por níveis de permissão via JWT

---

## Tecnologias

| Tecnologia | Versão | Função |
|---|---|---|
| FastAPI | 0.111.0 | Framework web |
| Uvicorn | 0.29.0 | Servidor ASGI |
| SQLAlchemy | 2.0.30 | ORM |
| PyMySQL | 1.1.0 | Driver MySQL |
| Pydantic | 2.7.1 | Validação de dados |
| python-jose | 3.3.0 | Tokens JWT |
| passlib[bcrypt] | 1.7.4 | Hash de senhas |
| Alembic | 1.13.1 | Migrações de banco |
| python-dotenv | 1.0.1 | Variáveis de ambiente |

---

## Estrutura do Projeto

```
backend/
├── app/
│   ├── main.py              # Ponto de entrada da aplicação
│   ├── database.py          # Conexão e sessão do banco de dados
│   ├── dependencies.py      # Injeção de dependências (auth, roles)
│   ├── core/
│   │   ├── config.py        # Configurações via variáveis de ambiente
│   │   └── security.py      # JWT e bcrypt
│   ├── models/              # Modelos ORM (SQLAlchemy)
│   ├── schemas/             # Schemas de validação (Pydantic)
│   ├── routers/             # Rotas agrupadas por domínio
│   └── services/            # Lógica de negócio
├── alembic/                 # Scripts de migração do banco
├── tests/                   # Testes automatizados
├── requirements.txt
└── .env
```

---

## Pré-requisitos

- Python 3.8+
- MySQL rodando e acessível
- Banco de dados `ciappi` criado com o schema correto

---

## Instalação e Execução

### 1. Clonar e acessar o diretório

```bash
cd backend
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do backend com o conteúdo abaixo:

```env
DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/ciappi
SECRET_KEY=troque-esta-chave-em-producao-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
DEV_MODE=True
```

> Para gerar uma `SECRET_KEY` segura: `openssl rand -hex 32`

### 5. Aplicar migrações

```bash
alembic upgrade head
```

### 6. Iniciar o servidor

```bash
# Desenvolvimento (com reload automático)
uvicorn app.main:app --reload

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Acessos

| URL | Descrição |
|---|---|
| `http://localhost:8000` | Endpoint raiz (health check) |
| `http://localhost:8000/docs` | Documentação Swagger (interativa) |
| `http://localhost:8000/redoc` | Documentação ReDoc |

---

## Autenticação

A API usa **JWT (Bearer Token)** com controle de acesso por nível.

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=nome_tecnico&password=senha
```

**Resposta:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "nivel": 2,
  "nome": "Nome do Técnico"
}
```

### Usando o token

Inclua o token no header de todas as requisições autenticadas:

```
Authorization: Bearer <access_token>
```

### Níveis de acesso

| Nível | Permissões |
|---|---|
| 1 | Somente leitura |
| 2 | Criar e editar casos, usuários, acompanhamentos, etc. |
| 3 | Acesso total, incluindo gerenciamento de técnicos e tabelas auxiliares |

> **DEV_MODE**: Quando `DEV_MODE=True`, requisições sem token são autenticadas automaticamente como administrador (nível 3). Desative em produção.

---

## Endpoints da API

### Casos

| Método | Endpoint | Nível | Descrição |
|---|---|---|---|
| GET | `/casos` | Qualquer | Lista casos com filtros (município, status, técnico, motivo) |
| GET | `/casos/{num_caso}` | Qualquer | Detalhes de um caso |
| POST | `/casos` | 2+ | Cria novo caso |
| PUT | `/casos/{num_caso}` | 2+ | Atualiza caso ou registra encerramento |
| PUT | `/casos/{num_caso}/restaurar` | 2+ | Reabre caso encerrado |

### Usuários (Idosos Atendidos)

| Método | Endpoint | Nível | Descrição |
|---|---|---|---|
| GET | `/usuarios` | Qualquer | Lista usuários com busca por nome |
| GET | `/usuarios/{num_cadastro}` | Qualquer | Perfil completo do usuário |
| POST | `/usuarios` | 2+ | Cadastra novo usuário |
| PUT | `/usuarios/{num_cadastro}` | 2+ | Atualiza perfil |

### Acompanhamentos

| Método | Endpoint | Nível | Descrição |
|---|---|---|---|
| GET | `/acompanhamentos/caso/{num_caso}` | Qualquer | Lista acompanhamentos de um caso |
| GET | `/acompanhamentos/{codigo}` | Qualquer | Detalhes de um acompanhamento |
| POST | `/acompanhamentos` | 2+ | Registra novo acompanhamento |
| PUT | `/acompanhamentos/{codigo}` | 2+ | Atualiza acompanhamento |

### ILPIs

| Método | Endpoint | Nível | Descrição |
|---|---|---|---|
| GET | `/ilpis` | Qualquer | Lista todas as ILPIs |
| GET | `/ilpis/{codigo}` | Qualquer | Detalhes de uma ILPI |
| POST | `/ilpis` | 2+ | Cadastra nova ILPI |
| PUT | `/ilpis/{codigo}` | 2+ | Atualiza dados da ILPI |

### Eventos

| Método | Endpoint | Nível | Descrição |
|---|---|---|---|
| GET | `/eventos` | Qualquer | Lista eventos |
| GET | `/eventos/{codigo}` | Qualquer | Detalhes de um evento |
| POST | `/eventos` | 2+ | Cria evento (fase de planejamento) |
| PUT | `/eventos/{codigo}` | 2+ | Atualiza evento ou registra resultados |

### Visitas a ILPIs

| Método | Endpoint | Nível | Descrição |
|---|---|---|---|
| GET | `/visitas/ilpi` | Qualquer | Lista visitas (filtros: `codigoilpi`, `status=agendada\|realizada`) |
| GET | `/visitas/ilpi/{codigo}` | Qualquer | Detalhes de uma visita |
| POST | `/visitas/ilpi` | 2+ | Agenda visita (fase 1) |
| PUT | `/visitas/ilpi/{codigo}/realizar` | 2+ | Registra realização da visita (fase 2) |
| PUT | `/visitas/ilpi/{codigo}` | 2+ | Edita visita agendada |

### Visitas Institucionais

| Método | Endpoint | Nível | Descrição |
|---|---|---|---|
| GET | `/visitas/inst` | Qualquer | Lista visitas institucionais |
| GET | `/visitas/inst/{codigo}` | Qualquer | Detalhes de uma visita |
| POST | `/visitas/inst` | 2+ | Registra visita institucional |
| PUT | `/visitas/inst/{codigo}` | 2+ | Atualiza visita |

### Ouvidoria

| Método | Endpoint | Nível | Descrição |
|---|---|---|---|
| GET | `/ouvidoria/avencer` | Qualquer | Casos com prazo a vencer (`?dias=N`) |
| GET | `/ouvidoria/vencidas` | Qualquer | Casos com prazo vencido |
| GET | `/ouvidoria/ambiente` | Qualquer | Todos os casos ativos de ouvidoria |
| GET | `/ouvidoria/concluidas` | Qualquer | Casos de ouvidoria concluídos |
| PUT | `/ouvidoria/{num_caso}/encerrar` | 2+ | Encerra prazo da ouvidoria manualmente |

### Tabelas Auxiliares

| Endpoint | Descrição |
|---|---|
| `/tabelas/motivos-atendimento` | Tipos de atendimento |
| `/tabelas/motivos-encerramento` | Motivos de encerramento |
| `/tabelas/motivos-restauracao` | Motivos de reabertura |
| `/tabelas/tipo-acao` | Tipos de ação |
| `/tabelas/tipo-evento` | Tipos de evento |
| `/tabelas/motivos-visita` | Motivos de visita |
| `/tabelas/origem` | Origens dos casos |
| `/tabelas/orgaos` | Órgãos parceiros |
| `/tabelas/municipios` | Municípios (somente leitura) |
| `/tabelas/tecnicos` | Técnicos do sistema |

Todas as tabelas auxiliares suportam `GET` (qualquer nível) e `POST/PUT/DELETE` (nível 3).

### Relatórios

```
GET /relatorios/...
```

Exportação de dados em formato CSV para análise e monitoramento.

---

## Migrações com Alembic

```bash
# Criar nova migração após alterar models
alembic revision --autogenerate -m "descrição da mudança"

# Aplicar migrações pendentes
alembic upgrade head

# Reverter última migração
alembic downgrade -1

# Ver histórico de migrações
alembic history
```

---

## Testes

```bash
pytest tests/
```

---

## Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|---|---|---|
| `DATABASE_URL` | URL de conexão com o MySQL | `mysql+pymysql://user:pass@localhost:3306/ciappi` |
| `SECRET_KEY` | Chave secreta para JWT | `openssl rand -hex 32` |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token em minutos | `480` (8 horas) |
| `DEV_MODE` | Modo desenvolvimento (desativa auth) | `True` / `False` |