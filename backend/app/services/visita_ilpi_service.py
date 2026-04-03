# ─────────────────────────────────────────────────────────────────────────────
# SERVICE: VisitaILPI — lógica de negócio para visitas a ILPIs
# ─────────────────────────────────────────────────────────────────────────────
# Gerencia o ciclo de vida de uma visita:
#   1. Agendamento  → cria a visita sem data de realização
#   2. Realização   → preenche data e relato quando a visita acontece
#   3. Atualização  → edições gerais
#   4. Listagem     → com filtros por ILPI e status

from sqlalchemy.orm import Session
from app.models.visita_ilpi import VisitaILPI
from app.models.ilpi import ILPI
from app.schemas.visita_ilpi import VisitaILPICreate, VisitaILPIUpdate, VisitaILPIRealizar


def agendar_visita(db: Session, data: VisitaILPICreate) -> VisitaILPI:
    """
    Agenda uma visita a uma ILPI.
    Valida que a ILPI existe antes de criar — evita registros órfãos.
    A visita é criada sem dtvisita (None), indicando que ainda não aconteceu.
    """
    # Verifica se a ILPI existe
    ilpi = db.query(ILPI).filter(ILPI.CODIGOILPI == data.codigoilpi).first()
    if not ilpi:
        raise ValueError(f"ILPI com código {data.codigoilpi} não encontrada.")

    visita = VisitaILPI(**data.model_dump())
    db.add(visita)
    db.commit()
    db.refresh(visita)
    return visita


def realizar_visita(db: Session, codigo: int, data: VisitaILPIRealizar) -> VisitaILPI:
    """
    Registra a realização de uma visita previamente agendada.

    Validações:
      - A visita deve existir
      - A visita não pode já ter sido realizada (dtvisita já preenchida)
        → Evitar sobrescrever um relatório já salvo acidentalmente.

    Só atualiza motivovisita e observacoes se foram enviados
    (campos opcionais que podem ser refinados no momento da realização).
    """
    visita = db.query(VisitaILPI).filter(VisitaILPI.Codigoentidade == codigo).first()
    if not visita:
        raise ValueError("Visita não encontrada.")
    if visita.dtvisita:
        # Guard clause: impede "realizar" uma visita que já foi realizada
        raise ValueError("Esta visita já foi realizada.")

    # Preenche os campos de realização
    visita.dtvisita = data.dtvisita
    visita.relato = data.relato

    # Atualiza campos opcionais apenas se foram enviados (if data.campo)
    if data.motivovisita:
        visita.motivovisita = data.motivovisita
    if data.observacoes:
        visita.observacoes = data.observacoes

    db.commit()
    db.refresh(visita)
    return visita


def atualizar_visita(db: Session, codigo: int, data: VisitaILPIUpdate) -> VisitaILPI:
    """
    Atualização genérica de qualquer campo da visita.
    Usa exclude_unset=True para só alterar o que foi enviado.
    """
    visita = db.query(VisitaILPI).filter(VisitaILPI.Codigoentidade == codigo).first()
    if not visita:
        raise ValueError("Visita não encontrada.")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(visita, campo, valor)

    db.commit()
    db.refresh(visita)
    return visita


def listar_visitas(
    db: Session,
    codigoilpi: int = None,
    apenas_agendadas: bool = False,
    apenas_realizadas: bool = False,
):
    """
    Lista visitas com filtros opcionais.

    Filtros:
      codigoilpi      → filtra por ILPI específica
      apenas_agendadas → dtvisita IS NULL (sem data = não realizadas ainda)
      apenas_realizadas → dtvisita IS NOT NULL (com data = já realizadas)

    .is_(None)      → WHERE dtvisita IS NULL (SQL)
    .isnot(None)    → WHERE dtvisita IS NOT NULL (SQL)
    Não use == None ou != None em SQLAlchemy — use .is_ e .isnot para gerar
    o SQL correto com IS NULL / IS NOT NULL.
    """
    q = db.query(VisitaILPI)

    if codigoilpi:
        q = q.filter(VisitaILPI.codigoilpi == codigoilpi)
    if apenas_agendadas:
        q = q.filter(VisitaILPI.dtvisita.is_(None))    # visitas pendentes
    if apenas_realizadas:
        q = q.filter(VisitaILPI.dtvisita.isnot(None))  # visitas concluídas

    # Ordena da mais recente para a mais antiga
    return q.order_by(VisitaILPI.dtprevistavisita.desc()).all()
