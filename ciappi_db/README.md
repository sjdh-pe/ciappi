# 🐬 Banco de Dados MySQL — `ciappi`

&#x20;&#x20;

Ambiente de banco de dados **MySQL 8.0** containerizado com **Docker Compose**

---

## ⚙️ Estrutura do Projeto

```
ciappi_db/
├── docker/
│   ├── docker-compose.yml                     # Orquestração Docker Compose
│   └── mysql/
│       ├── Dockerfile                         # Imagem customizada MySQL
│       ├── conf.d/
│       │   └── my.cnf                         # Configurações MySQL
│       └── init/
│           ├── 01-schema.sql                  # Criar tabelas
│           ├── 02-indexes.sql                 # Criar índices
│           └── 03-data.sql                    # Popular dados iniciais
├── arq/
│   ├── csv_fix/                               # Dados em CSV para importação
│   └── backup/                                # Backups do banco
├── fix_data.py                                # Script Python para correção de dados
├── docker-compose.yml                         # Composição principal (raiz)
├── diagrama_er.html                           # 📊 Diagrama E-R interativo
├── README.md                                  # Este arquivo 📝
└── .gitignore                                 # Arquivos ignorados pelo Git
```

---

## 🚀 Inicializando o Banco de Dados

### 1️⃣ Pré-requisitos

- **Docker Desktop** instalado e rodando
- **Docker Compose** (incluído no Docker Desktop)
- Variáveis de ambiente configuradas no `.env` da raiz do projeto (`/ciappi/.env`)

### 2️⃣ Subir o Container MySQL

Na raiz do projeto (`/ciappi`), execute:

```bash
# Opção 1: Usando Docker Compose diretamente
cd ciappi_db
docker compose up -d

# Opção 2: A partir da raiz do projeto
docker compose -f ciappi_db/docker-compose.yml up -d
```

📦 Isso fará:

✅ Baixar a imagem oficial `mysql:8.0`\
✅ Criar o banco de dados `ciappi`\
✅ Aplicar charset e timezone corretos (`utf8mb4`, `America/Recife`)\
✅ Tornar o serviço disponível na porta `3309`\
✅ Importar o schema SQL automático\
✅ Executar healthcheck para verificar integridade

### 3️⃣ Verificar o Status

```bash
# Verificar se o container está healthy
docker ps

# Deverá mostrar:
# ciappi_db-mysql-1   ... (healthy)
```

---

## 📊 Schema do Banco de Dados

O schema completo está documentado em:

```
ciappi_db/
├── schema.sql                                 # Schema completo com 19 tabelas
└── diagrama_er.html                           # Visualização interativa
```

### Tabelas Principais:
- 🔹 **TbCIAPPICaso** — Casos de denúncia/atendimento
- 👤 **tbciappiusuario** — Dados de usuários (idosos)
- 📝 **TbCIAPPIAcompanhamento** — Acompanhamentos técnicos
- 📅 **TbEvento** — Eventos relacionados aos casos
- 🏛️ **TbCIAPPIILPI** — Instituições de Longa Permanência para Idosos
- 🏢 **TbVisitaInst** — Visitas institucionais
- 🗂️ **+ 13 tabelas de referência/lookup** (Estados, Municípios, Órgãos, etc.)

---

## 🔧 Configuração do Banco

O arquivo `.env` na **raiz do projeto** (`/ciappi/.env`) contém as variáveis:

```env
# =========================================================
# 🧱 Configuração do Banco de Dados MySQL
# =========================================================
DB_HOST=localhost
DB_PORT=3309
MYSQL_ROOT_PASSWORD=ciappi_pwd
MYSQL_DATABASE=ciappi
MYSQL_USER=ciappi_urs
MYSQL_PASSWORD=ciappi_pwd

# =========================================================
# 🌍 Fuso Horário (MySQL e Sistema)
# =========================================================
TZ=America/Recife

# =========================================================
# 🔐 FastAPI & Autenticação
# =========================================================
SECRET_KEY=your_secret_key_here_very_long_and_complex
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# =========================================================
# 🔗 Conexão Backend <-> Database
# =========================================================
DATABASE_URL=mysql+pymysql://ciappi_urs:ciappi_pwd@localhost:3309/ciappi
```

> 💡 Essas variáveis são carregadas automaticamente pelo Docker Compose e pela aplicação Python.

---

## 🩺 Healthcheck

O container executa verificações automáticas de integridade:

```yaml
healthcheck:
  test: ["CMD-SHELL", "mysqladmin ping -h localhost -u root -p$$MYSQL_ROOT_PASSWORD | grep 'mysqld is alive' || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 20s
```

🔍 Verifique o status:

```bash
docker ps
```

O container estará **healthy** quando estiver pronto para receber conexões.

---

## 🧰 Comandos Docker Compose — Gerenciamento Rápido

| Comando | Descrição |
| --- | --- |
| `docker compose up -d` | Sobe o container MySQL em background |
| `docker compose down` | Para e remove o container |
| `docker compose restart` | Reinicia o banco |
| `docker compose logs -f` | Exibe os logs em tempo real |
| `docker compose exec mysql bash` | Abre terminal dentro do container |
| `docker compose exec mysql mysql -u root -p` | Abre o CLI do MySQL |
| `docker compose ps` | Verifica status dos containers |

📘 Exemplo:

```bash
# Acessar o MySQL via CLI
docker compose -f ciappi_db/docker-compose.yml exec mysql mysql -u ciappi_urs -pciappi_pwd ciappi
```

---

## 💾 Backup e Restauração

### Criar backup:

```bash
# A partir da raiz do projeto
docker compose -f ciappi_db/docker-compose.yml exec mysql \
  mysqldump -u ciappi_urs -pciappi_pwd ciappi > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar backup:

```bash
# A partir da raiz do projeto
docker compose -f ciappi_db/docker-compose.yml exec -T mysql \
  mysql -u ciappi_urs -pciappi_pwd ciappi < backup.sql
```

> 💡 O sufixo `-T` em `exec -T` desabilita a alocação de pseudo-TTY, essencial para pipes com stdin.

---

## 🕒 Timezone e Localização

- Fuso horário configurado: **America/Recife**
- Charset padrão: **utf8mb4**
- Collation: **utf8mb4\_unicode\_ci**

> 🔧 Isso garante compatibilidade total com acentuação e horários locais (inclusive para timestamps automáticos do Hibernate).

---

## 🧩 Dicas Extras

✅ **Acesso via DBeaver, DataGrip ou IntelliJ**\
Use as credenciais do `.env`:

```
Host: localhost
Port: 3309
Database: ciappi
User: ciappi_urs
Password: ciappi_pwd
```

✅ **Ver logs MySQL em tempo real**

```bash
docker compose -f ciappi_db/docker-compose.yml logs -f mysql
```

✅ **Verificar criação do banco**

```bash
docker compose -f ciappi_db/docker-compose.yml exec mysql \
  mysql -u ciappi_urs -pciappi_pwd -e "SHOW DATABASES; USE ciappi; SHOW TABLES;"
```

✅ **Conectar ao container MySQL interativamente**

```bash
docker compose -f ciappi_db/docker-compose.yml exec mysql bash
# Dentro do container:
mysql -u ciappi_urs -p ciappi
```

✅ **Resetar o banco completamente (⚠️ CUIDADO - Deleta tudo)**

```bash
docker compose -f ciappi_db/docker-compose.yml down -v
docker compose -f ciappi_db/docker-compose.yml up -d
```

---

## 📊 Diagrama de Relacionamentos (E-R)

Visualize a estrutura completa do banco de dados com o diagrama interativo:

👉 **[Abrir Diagrama de Relacionamentos](./diagrama_er.html)**

O diagrama inclui:
- Visualização de todas as 19 tabelas
- Relacionamentos entre entidades (1:N, N:1, etc.)
- Estrutura de campos e tipos de dados
- Chaves primárias e estrangeiras
- Interface com abas interativas (Visual, Tabelas, Relacionamentos)

---

## 👨‍💻 Créditos e Autor

**Autor:** [Raul Michel de França](https://github.com/raul-franca)\
**E-mail:** raul.franca@sjdh.pe.gov.br\
**Projeto:** CIAPPI - Sistema de Gestão de Casos de Proteção ao Idoso\
**Banco:** MySQL 8.0 — Docker Compose

---

📘 *Versão: 2.0 | Data: 01/04/2026 | Status: ✅ Produção*
