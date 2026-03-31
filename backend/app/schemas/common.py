# ─────────────────────────────────────────────────────────────────────────────
# COMMON.PY — Tipos e utilitários compartilhados entre schemas
# ─────────────────────────────────────────────────────────────────────────────
# Centraliza o tipo ZeroDatetime para evitar repetição em todos os schemas.
#
# Por que existe esse problema?
# O banco Access/MySQL legado armazena datas vazias como "0000-00-00 00:00:00"
# em vez de NULL. O Python não consegue criar um datetime com mês 0,
# então precisamos converter esse valor para None ANTES da validação de tipo.
#
# BeforeValidator dentro de Annotated é mais confiável que field_validator
# mode="before" para esse caso, porque roda antes de qualquer tentativa
# de coerção de tipo pelo Pydantic — inclusive ao ler objetos ORM.

from datetime import datetime
from typing import Optional, Annotated
from pydantic import BeforeValidator


def _parse_zero_date(v):
    """Converte datas zeradas do legado Access/MySQL para None."""
    if v in ("0000-00-00 00:00:00", "0000-00-00"):
        return None
    return v


# Tipo reutilizável: Optional[datetime] com sanitização automática de datas zeradas.
# Use este tipo em qualquer campo datetime que pode ter "0000-00-00 00:00:00".
ZeroDatetime = Annotated[Optional[datetime], BeforeValidator(_parse_zero_date)]
