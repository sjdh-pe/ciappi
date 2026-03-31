#!/bin/bash

DB="CIAPPI BD.accdb"
OUTDIR="csv"

mkdir -p "$OUTDIR"

tables=(
"TbChegouPrograma"
"TbCIAPPIAcompanhamento"
"TbCIAPPICaso"
"TbCIAPPIILPI"
"TbEstado"
"TbEvento"
"TbMotivoAtendimento"
"TbMotivoEncerramento"
"TbMotivoRestauração"
"TbMotVisitaInst"
"TbMunicipio"
"TbOrgao"
"TbTecnico"
"TbTipoAcao"
"TbTipoEvento"
"tbviolbairro"
"TbVisitaInst"
"TbCIAPPIUsuario"
"TbMotivoVisita"
"TbUltMov"
)

for t in "${tables[@]}"; do
  echo "Exportando $t..."
  mdb-export "$DB" "$t" > "$OUTDIR/${t}.csv"
done

echo "Exportação concluída em $OUTDIR/"
