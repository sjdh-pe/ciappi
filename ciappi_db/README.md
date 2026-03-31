# 🐬 Banco de Dados MySQL — `ciappi`

&#x20;&#x20;

Ambiente de banco de dados **MySQL 8.0** containerizado com **Docker Compose**

---

## ⚙️ Estrutura do Projeto

```
db-MySQL/
├── docker/
│   └── mysql/
│       └── init/           
├── docker-compose.yml                         # Orquestração Docker
├── .env                                       # Variáveis de ambiente
├── Makefile                                   # Comandos rápidos
└── README.md                                  # Este arquivo 📝
```

---

## 🚀 Subindo o Banco de Dados

### 1️⃣ Subir com Docker Compose

```bash
make up
```

ou, se preferir manualmente:

```bash
docker compose up -d
```

📦 Isso fará:

- Baixar a imagem oficial `mysql:8.0`;
- Criar o banco `ciappi`;
- Aplicar charset e timezone corretos (`utf8mb4`, `America/Recife`);
- Tornar o serviço disponível na porta `3309`.

---
## Crie o esquema da base

```bash
    mdb-schema "CIAPPI BD.accdb" mysql > schema.sql
```

---
## 🧾 Arquivo `.env`

As variáveis de ambiente ficam centralizadas no `.env`:

```env
# =============================
# 🌍 Timezone
# =============================
TZ=America/Recife

# =============================
# 🗄️ Banco de Dados
# =============================
MYSQL_ROOT_PASSWORD=ciappi_pwd
MYSQL_DATABASE=ciappi
MYSQL_USER=ciappi_urs
MYSQL_PASSWORD=ciappi_pwd

# =============================
# 🌐 Porta externa
# =============================
DB_PORT=3309
```

> 💡 Essas variáveis são carregadas automaticamente pelo `docker-compose.yml`.

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

## 🧰 Makefile — Comandos Rápidos

| Comando        | Descrição                                      |
| -------------- | ---------------------------------------------- |
| `make up`      | Sobe o container MySQL                         |
| `make down`    | Para e remove o container                      |
| `make restart` | Reinicia o banco                               |
| `make logs`    | Exibe os logs em tempo real                    |
| `make bash`    | Abre terminal dentro do container              |
| `make mysql`   | Abre o CLI do MySQL                            |
| `make clean`   | Remove volumes e dados persistidos             |
| `make reset`   | Remove completamente o volume e recria o banco |

📘 Exemplo:

```bash
make mysql
```

> Acessa o banco direto via terminal.

---

## 💾 Backup e Restauração

### Criar backup:

```bash
docker exec db-ciappi mysqldump -u ciappi_urs -pciappi_pwd ciappi > backup.sql
```

### Restaurar backup:

```bash
docker exec -i db-ciappi mysql -u ciappi_urs -pciappi_pwd ciappi < backup.sql
```

---

## 🕒 Timezone e Localização

- Fuso horário configurado: **America/Recife**
- Charset padrão: **utf8mb4**
- Collation: **utf8mb4\_unicode\_ci**

> 🔧 Isso garante compatibilidade total com acentuação e horários locais (inclusive para timestamps automáticos do Hibernate).

---

## 🧩 Dicas Extras

✅ **Acesso via DBeaver ou IntelliJ**\
Use as credenciais do `.env`:

```
Host: localhost
Port: 3309
Database: ciappi
User: ciappi_urs
Password: ciappi_pwd
```

✅ **Ver logs MySQL**

```bash
make logs
```

✅ **Verificar criação do banco**

```bash
docker exec -it db-ciappi mysql -u ciappi_urs -pciappi_pwd -e "SHOW DATABASES;"
```

---

## 👨‍💻 Créditos e Autor

**Autor:** [Raul Michel de França](https://github.com/raul-franca)\
**E-mail** [raul.franca@sjdh.pe.gov.br](mailto:raul.franca@sjdh.pe.gov.br)\
**Projeto:**  DB ciappi\
**Banco:** MySQL 8.0 — Docker Compose.

---

📘 *Versão: 25/2026 — Ambiente padronizado para desenvolvimento*
