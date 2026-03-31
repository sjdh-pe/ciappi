# 🛡️ CIAPPI — Sistema de Gestão de Casos de Proteção ao Idoso

O **CIAPPI** (Centro Integrado de Atenção e Prevenção à Violência contra a Pessoa Idosa) é um sistema robusto desenvolvido para a **Secretaria de Justiça e Direitos Humanos de Pernambuco (SJDH/PE)**. Ele visa gerenciar denúncias, acompanhamentos técnicos, visitas institucionais e eventos relacionados à proteção da pessoa idosa.

---

## 🏛️ Arquitetura do Projeto

O sistema é dividido em três camadas principais, garantindo escalabilidade e facilidade de manutenção:

- **Backend (API):** Desenvolvido em **FastAPI (Python 3.12)**. Segue o padrão RESTful, com autenticação via JWT, validação de dados com Pydantic e ORM SQLAlchemy.
- **Frontend (Painel):** Desenvolvido em **Streamlit (Python 3.12)**. Oferece uma interface intuitiva para os técnicos, com dashboards, formulários dinâmicos e exportação de relatórios.
- **Banco de Dados:** **MySQL 8.0** rodando em container **Docker**, garantindo isolamento e consistência de dados.

---

## 🔌 API Endpoints (Resumo)

A API possui documentação interativa automática disponível em `/docs` (Swagger) ou `/redoc`.

### 🔐 Autenticação (`/auth`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/auth/login` | Realiza o login e retorna o Token JWT e nível de acesso. |

### 📁 Casos (`/casos`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/casos/` | Lista casos com filtros (município, encerrado, técnico). |
| `POST` | `/casos/` | Cria um novo caso de denúncia/atendimento. |
| `PUT` | `/casos/{id}` | Atualiza informações de um caso existente. |
| `PATCH` | `/casos/{id}/restaurar` | Restaura um caso arquivado/excluído. |

### 👤 Usuários e Técnicos (`/usuarios`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/usuarios/` | Lista técnicos e usuários cadastrados no sistema. |

### 🏛️ ILPIs e Instituições (`/ilpis`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/ilpis/` | Gerencia o cadastro de Instituições de Longa Permanência para Idosos. |

### 📊 Relatórios e Ouvidoria
O sistema possui módulos especializados para `/ouvidoria` (denúncias externas), `/visitas` (fiscalização de ILPIs), `/eventos` e `/acompanhamentos`.

---

## 💻 Frontend (Interface do Usuário)

O frontend foi desenhado para ser produtivo e direto ao ponto.

### Funcionalidades Principais:
- **Painel Inicial:** Indicadores em tempo real (Casos Ativos, Ouvidorias a Vencer).
- **Gestão de Casos:** Cadastro completo da pessoa idosa, agressor e tipificação da violência.
- **Acompanhamentos:** Registro cronológico de todas as intervenções feitas pelos técnicos.
- **Ouvidoria:** Controle de prazos e respostas para denúncias vindas de canais externos.
- **Relatórios:** Geração de estatísticas por município, tipo de violência e período.
- **Visitas Institucionais:** Formulários de fiscalização técnica em ILPIs com registro de irregularidades.

### Níveis de Acesso:
1. **Consulta (Nível 1):** Acesso a relatórios, ouvidoria e painéis básicos.
2. **Técnico (Nível 2+):** Permissão total para edição de casos, acompanhamentos e tabelas administrativas.

---

## 🚀 Como Executar

Para configurar o ambiente, instalar dependências e rodar o projeto em 5 minutos, acesse o nosso guia de início rápido:

👉 **[PASSO A PASSO NO QUICKSTART.md](./QUICKSTART.md)**

---

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.12
- **Framework Web:** FastAPI
- **Interface:** Streamlit
- **Banco de Dados:** MySQL 8.0 (Docker)
- **Autenticação:** OAuth2 com JWT (Passlib & Jose)
- **Gestão de Ambiente:** Makefile & Shell Scripts

---
*CIAPPI — Sistema de Proteção ao Idoso — SJDH/PE*
