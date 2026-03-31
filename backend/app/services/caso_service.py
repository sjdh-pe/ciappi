# ─────────────────────────────────────────────────────────────────────────────
# SERVICE: Caso — lógica de negócio para casos
# ─────────────────────────────────────────────────────────────────────────────
# Contém todas as regras que governam o ciclo de vida de um caso:
# criação, atualização, encerramento automático e restauração.
#
# Regras de negócio implementadas aqui:
#   ✓ Número de caso deve ser único
#   ✓ Encerramento exige data + motivo juntos (não aceita apenas um)
#   ✓ Ao encerrar, cria automaticamente um acompanhamento de "ENCERRAMENTO DO CASO"
#   ✓ Restauração limpa os campos de encerramento

from sqlalchemy.orm import Session
from datetime import datetime
from app.models.caso import Caso
from app.models.acompanhamento import Acompanhamento
from app.schemas.caso import CasoCreate, CasoUpdate


def caso_existe(db: Session, num_caso: int) -> bool:
    """
    Verifica se já existe um caso com este número.
    Retorna True/False — útil para validar antes de inserir.
    """
    return db.query(Caso).filter(Caso.TbCasoNumCaso == num_caso).first() is not None


def criar_caso(db: Session, data: CasoCreate) -> Caso:
    """
    Cria um novo caso no banco.

    Passo a passo:
      1. Verifica se o número já existe (caso seja duplicata, lança ValueError)
      2. Cria o objeto Caso com os dados validados pelo schema
         → data.model_dump() converte o schema Pydantic em dict Python
         → Caso(**dict) desempacota o dict como kwargs do construtor
      3. db.add(caso) → marca o objeto para ser inserido (ainda não foi ao banco)
      4. db.commit()  → executa o INSERT no banco de dados
      5. db.refresh() → recarrega o objeto do banco (pega o ID gerado, etc.)
    """
    if caso_existe(db, data.TbCasoNumCaso):
        raise ValueError(f"Número de caso {data.TbCasoNumCaso} já existe.")

    caso = Caso(**data.model_dump())
    db.add(caso)
    db.commit()
    db.refresh(caso)
    return caso


def atualizar_caso(db: Session, num_caso: int, data: CasoUpdate) -> Caso:
    """
    Atualiza os dados de um caso existente.

    model_dump(exclude_unset=True) retorna apenas os campos que foram
    REALMENTE enviados pelo cliente — campos com default None que não
    foram enviados não aparecem, evitando sobrescrever dados acidentalmente.

    Lógica de encerramento:
      Para encerrar um caso, data + motivo devem ser enviados juntos.
      Enviar só um deles é um erro de negócio — a API retorna HTTP 400.
      Quando encerra pela primeira vez → cria acompanhamento automático.
    """
    caso = db.query(Caso).filter(Caso.TbCasoNumCaso == num_caso).first()
    if not caso:
        raise ValueError("Caso não encontrado.")

    # Pega apenas os campos que foram enviados na requisição
    updates = data.model_dump(exclude_unset=True)

    # ── Regra: encerrar exige data + motivo juntos ────────────────────────────
    # Combina o valor do update (se enviado) com o valor atual do banco
    encerra_dt = updates.get("TbCasoDtencer") or caso.TbCasoDtencer
    encerra_mot = updates.get("TbCasoMotivoEncerramento") or caso.TbCasoMotivoEncerramento

    if (encerra_dt and not encerra_mot) or (encerra_mot and not encerra_dt):
        raise ValueError("Para encerrar o caso informe a Data e o Motivo de encerramento juntos.")

    # ── Aplica as atualizações no objeto ──────────────────────────────────────
    # setattr(objeto, "campo", valor) é o equivalente dinâmico de objeto.campo = valor
    # Usamos aqui porque os nomes dos campos estão em variáveis (strings)
    for campo, valor in updates.items():
        setattr(caso, campo, valor)

    # ── Detecta se está encerrando AGORA (não estava encerrado antes) ─────────
    ja_estava_encerrado = caso.TbCasoEncerrado == "Sim"
    encerrando_agora = encerra_dt and encerra_mot and not ja_estava_encerrado

    # Marca o caso como encerrado
    if encerra_dt and encerra_mot:
        caso.TbCasoEncerrado = "Sim"

    db.commit()
    db.refresh(caso)

    # ── Cria acompanhamento automático ao encerrar ────────────────────────────
    # Reproduz o comportamento do VBA no Access (FrmATuCaso):
    # ao salvar um encerramento, o sistema criava um registro de acompanhamento.
    if encerrando_agora:
        _registrar_acomp_encerramento(db, caso)

    return caso


def _registrar_acomp_encerramento(db: Session, caso: Caso) -> None:
    """
    Função privada (nome com _) — cria automaticamente um acompanhamento
    ao encerrar um caso.

    Por que privada? Porque só deve ser chamada internamente por atualizar_caso().
    A convenção _ no início do nome sinaliza "uso interno" em Python.

    Reproduz o comportamento do VBA:
      Rs1("TbAcompAcao") = "ENCERRAMENTO DO CASO"
    """
    acomp = Acompanhamento(
        TbAcomCaso=caso.TbCasoNumCaso,
        TbAcompdata=datetime.now(),
        TbAcompAcao="ENCERRAMENTO DO CASO",
        TbCaraterAtendimento="Social",
        TbRelato="Caso encerrado automaticamente pelo sistema.",
        TbTecnicoResponsavel=caso.TbCasoTecnicoResp or "SISTEMA",
    )
    db.add(acomp)
    db.commit()


def restaurar_caso(db: Session, num_caso: int, motivo_restauracao: int) -> Caso:
    """
    Reabre um caso encerrado, limpando todos os campos de encerramento.
    O motivo_restauracao é registrado em TbMotivoRestauracao (para auditoria),
    mas não é armazenado diretamente no caso — apenas libera o fluxo.
    """
    caso = db.query(Caso).filter(Caso.TbCasoNumCaso == num_caso).first()
    if not caso:
        raise ValueError("Caso não encontrado.")

    # Limpa os campos de encerramento → caso volta a "em aberto"
    caso.TbCasoEncerrado = "Não"
    caso.TbCasoDtencer = None
    caso.TbCasoMotivoEncerramento = None

    db.commit()
    db.refresh(caso)
    return caso


def listar_casos(
    db: Session,
    municipio: str = None,
    encerrado: str = None,
    tecnico: str = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Lista casos com filtros opcionais e paginação.

    .ilike() → comparação case-insensitive com wildcard (%municipio%)
    .offset(skip).limit(limit) → paginação: pula 'skip' registros,
    retorna no máximo 'limit' registros.
    """
    q = db.query(Caso)

    # Cada filtro é adicionado condicionalmente — se não foi passado, é ignorado
    if municipio:
        q = q.filter(Caso.TbCasoMunicipio.ilike(f"%{municipio}%"))
    if encerrado is not None:
        q = q.filter(Caso.TbCasoEncerrado == encerrado)
    if tecnico:
        q = q.filter(Caso.TbCasoTecnicoResp.ilike(f"%{tecnico}%"))

    return q.offset(skip).limit(limit).all()
