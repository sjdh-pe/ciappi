#!/bin/bash

# Carrega variáveis do .env (busca a partir do diretório pai)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a; source "$SCRIPT_DIR/../.env"; set +a

DB_NAME="$MYSQL_DATABASE"
DB_USER="$MYSQL_USER"
DB_PASS="$MYSQL_PASSWORD"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"

for file in csv/*.csv; do
  table=$(basename "$file" .csv | tr '[:upper:]' '[:lower:]')

  echo "Importando $file -> $table"

  mysql --local-infile=1 -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" <<EOF
  LOAD DATA LOCAL INFILE '$PWD/$file'
  INTO TABLE $table
  FIELDS TERMINATED BY ','
  OPTIONALLY ENCLOSED BY '"'
  LINES TERMINATED BY '\n'
  IGNORE 1 LINES;
EOF

done

echo "✅ Importação concluída!"
