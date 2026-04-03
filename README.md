# CIAPPI — Sistema de Gestão de Casos de Proteção ao Idoso

O **CIAPPI** (Centro Integrado de Atenção e Prevenção à Violência contra a Pessoa Idosa) é um sistema desenvolvido para a **Secretaria de Justiça e Direitos Humanos de Pernambuco (SJDH/PE)**. Gerencia denúncias, acompanhamentos técnicos, visitas institucionais, ouvidoria e eventos relacionados à proteção da pessoa idosa.

---

## Arquitetura

O sistema é dividido em três camadas:

- **Backend (API):** FastAPI (Python 3.12) — RESTful, autenticação OAuth2/JWT, validação Pydantic, ORM SQLAlchemy com migrações Alembic.
- **Frontend (Painel):** Streamlit (Python 3.12) — dashboards, formulários dinâmicos e exportação de relatórios.
- **Banco de Dados:** MySQL 8.0 em container Docker com 19 tabelas mapeadas.

```
ciappi/
├── backend/
│   └── app/
│       ├── main.py            # Inicialização da API e registro de routers
│       ├── models/            # Modelos ORM (SQLAlchemy)
│       ├── schemas/           # Schemas de validação (Pydantic)
│       ├── routers/           # Grupos de endpoints da API
│       ├── services/          # Camada de regras de negócio
│       ├── dependencies.py    # DI: sessão DB, usuário logado, verificação de nível
│       └── core/config.py     # Configurações via .env (pydantic-settings)
├── frontend/
│   ├── app.py                 # Ponto de entrada Streamlit
│   ├── auth/login.py          # Login e gerenciamento de sessão
│   ├── pages/                 # 11 páginas do painel
│   ├── components/            # Estilos CSS e componentes reutilizáveis
│   └── api/client.py          # Cliente HTTP para comunicação com o backend
├── ciappi_db/
│   ├── docker-compose.yml     # Configuração do container MySQL
│   └── diagrama_er.html       # Diagrama E-R interativo (19 tabelas)
├── alembic/                   # Migrações do banco de dados
├── EXEMPLO.env                # Template de variáveis de ambiente
├── Makefile                   # Automação de tarefas
└── QUICKSTART.md              # Guia de início rápido
```

---

## Funcionalidades


| Módulo                    | Descrição                                                                                              |
| :------------------------- | :------------------------------------------------------------------------------------------------------- |
| **Casos**                  | Cadastro e gestão de atendimentos — pessoa idosa, agressor, tipificação de violência e encerramento |
| **Acompanhamentos**        | Histórico cronológico de intervenções técnicas com prazos e encaminhamentos                         |
| **Usuários / Idosos**     | Cadastro completo da pessoa atendida (contato, endereço, perfil)                                        |
| **ILPIs**                  | Registro de Instituições de Longa Permanência para Idosos                                             |
| **Visitas a ILPIs**        | Visitas de acompanhamento com ciclo de vida: agendada → realizada                                       |
| **Visitas Institucionais** | Fiscalizações técnicas em órgãos parceiros                                                          |
| **Ouvidoria**              | Monitoramento de denúncias externas com controle de prazos (a vencer / vencidas / concluídas)          |
| **Eventos**                | Agendamento e registro de atividades da equipe                                                           |
| **Relatórios**            | Exportação CSV e estatísticas por município, tipo de violência e período                           |
| **Tabelas Auxiliares**     | Administração de dados de referência (motivos, tipos, órgãos, municípios)                          |

---

## Níveis de Acesso


| Nível | Perfil        | Permissões                                                  |
| :----: | :------------ | :----------------------------------------------------------- |
|   1   | Consulta      | Visualização de relatórios, ouvidoria e dashboards        |
|   2   | Operador      | CRUD completo de casos, usuários, visitas e acompanhamentos |
|   3   | Administrador | Gerenciamento de técnicos e tabelas auxiliares              |

---

## API Endpoints

A documentação interativa está disponível em `/docs` (Swagger) ou `/redoc` quando o backend estiver rodando.

### Autenticação (`/auth`)


| Método | Endpoint      | Descrição                                          |
| :------ | :------------ | :--------------------------------------------------- |
| `POST`  | `/auth/login` | Login OAuth2 — retorna token JWT e nível de acesso |

### Casos (`/casos`)


| Método | Endpoint                | Descrição                                                                |
| :------ | :---------------------- | :------------------------------------------------------------------------- |
| `GET`   | `/casos/`               | Lista casos com filtros (município, status, técnico, tipo de violência) |
| `POST`  | `/casos/`               | Cria novo caso                                                             |
| `PUT`   | `/casos/{id}`           | Atualiza caso existente                                                    |
| `PATCH` | `/casos/{id}/restaurar` | Restaura caso arquivado                                                    |

### Usuários / Idosos (`/usuarios`)


| Método | Endpoint         | Descrição                                              |
| :------ | :--------------- | :------------------------------------------------------- |
| `GET`   | `/usuarios/`     | Lista pessoas atendidas com busca por nome e paginação |
| `POST`  | `/usuarios/`     | Cadastra nova pessoa                                     |
| `PUT`   | `/usuarios/{id}` | Atualiza dados cadastrais                                |

### ILPIs (`/ilpis`)


| Método | Endpoint      | Descrição          |
| :------ | :------------ | :------------------- |
| `GET`   | `/ilpis/`     | Lista instituições |
| `POST`  | `/ilpis/`     | Cadastra nova ILPI   |
| `PUT`   | `/ilpis/{id}` | Atualiza ILPI        |

### Visitas (`/visitas`)


| Método        | Endpoint         | Descrição                       |
| :------------- | :--------------- | :-------------------------------- |
| `GET/POST/PUT` | `/visitas/ilpi/` | Gestão de visitas a ILPIs        |
| `GET/POST/PUT` | `/visitas/inst/` | Gestão de visitas institucionais |

### Ouvidoria (`/ouvidoria`)


| Método | Endpoint          | Descrição                                   |
| :------ | :---------------- | :-------------------------------------------- |
| `GET`   | `/ouvidoria/`     | Lista denúncias com filtro de status e prazo |
| `POST`  | `/ouvidoria/`     | Registra nova denúncia                       |
| `PUT`   | `/ouvidoria/{id}` | Atualiza denúncia                            |

### Outros módulos

- **`/acompanhamentos`** — Histórico de intervenções por caso
- **`/eventos`** — Agendamento e registro de eventos
- **`/relatorios`** — Geração e exportação de relatórios
- **`/tabelas`** — CRUD das tabelas auxiliares (somente Admin)

---

## Como Executar

Para configurar o ambiente, instalar dependências e rodar o projeto, acesse o guia de início rápido:

**[PASSO A PASSO NO QUICKSTART.md](./QUICKSTART.md)**

### Resumo rápido

```bash
# Configurar ambiente completo
make setup

# Subir banco de dados (Docker)
make up

# Rodar backend e frontend em terminais separados
make run-backend
make run-frontend
```

**Acessos:**

- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:8000`
- Documentação API: `http://localhost:8000/docs`

### Comandos úteis

```bash
make status           # Status do container MySQL
make logs             # Logs do banco de dados
make mysql            # Shell interativo do MySQL
make backup           # Gerar dump do banco
make restore FILE=... # Restaurar backup
make clean            # Remover volumes e resetar ambiente

make migrate          # Aplicar migrações pendentes
make migrate-status   # Verificar revisão atual
make migrate-new MSG="descricao"  # Criar nova migração
```

---

## Configuração do Ambiente

Copie `EXEMPLO.env` para `.env` e ajuste as variáveis:

```env
# Banco de dados
MYSQL_HOST=localhost
MYSQL_PORT=3309
MYSQL_USER=ciappi
MYSQL_PASSWORD=...
MYSQL_DATABASE=ciappi_db

# Autenticação JWT
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Ambiente
ENVIRONMENT=development
TZ=America/Recife
```

---

## Tecnologias


| Camada          | Tecnologia                                 |
| :-------------- | :----------------------------------------- |
| Linguagem       | Python 3.12                                |
| API             | FastAPI + Uvicorn                          |
| Interface       | Streamlit                                  |
| Banco de Dados  | MySQL 8.0 (Docker)                         |
| ORM             | SQLAlchemy 2.0                             |
| Migrações     | Alembic                                    |
| Autenticação  | OAuth2 + JWT (python-jose, passlib/bcrypt) |
| Visualizações | Plotly                                     |
| Automação     | Makefile + Shell Scripts                   |

---

## Diagrama E-R

Acesse o diagrama interativo com as 19 tabelas do banco de dados, seus relacionamentos, campos e tipos:

**[📊 Visualizar Diagrama E-R Completo](./ciappi_db/diagrama_er.html)**

---

## Informações de Revisão e Autoria

| Campo | Informação |
| :--- | :--- |
| **Projeto** | CIAPPI - Sistema de Gestão de Casos de Proteção ao Idoso |
| **Versão** | 2.0 |
| **Data de Revisão** | 02 de Abril de 2026 |
| **Instituição** | SUPTI - SJDH-PE |
| **Desenvolvedor** | Raul Michel de França |
| **E-mail** | raul.franca@sjdh.pe.gov.br |
| **GitHub** | [raul-franca](https://github.com/raul-franca) |
| **Status** | ✅ Produção |

---

*CIAPPI — Sistema de Proteção ao Idoso — Desenvolvido por **Raul Michel de França** | **SUPTI - SJDH-PE***
