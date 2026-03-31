# ─────────────────────────────────────────────────────────────────────────────
# SERVICE: Acompanhamento — lógica de negócio para acompanhamentos
# ─────────────────────────────────────────────────────────────────────────────
# Regras de negócio implementadas:
#   ✓ Caso vinculado deve existir antes de criar o acompanhamento
#   ✓ Prazo não pode ser no passado
#   ✓ Encaminhamento exige órgão de destino
#   ✓ Ação "Concluída para Ouvidoria" dispara encerramento automático da ouvidoria

from sqlalchemy.orm import Session
from datetime import date, datetime
from app.models.acompanhamento import Acompanhamento
from app.models.caso import Caso
from app.schemas.acompanhamento import AcompanhamentoCreate, AcompanhamentoUpdate

# Constante: ação que dispara o fluxo de encerramento automático da ouvidoria.
# Usar uma constante em vez da string "solta" evita erros de digitação e
# facilita buscas no código.
ACAO_CONCLUI_OUVIDORIA = "Concluída para Ouvidoria"


def criar_acompanhamento(db: Session, data: AcompanhamentoCreate) -> Acompanhamento:
    """
    Cria um acompanhamento após validar as regras de negócio.

    Gatilho especial:
      Se a ação for "Concluída para Ouvidoria", encerra automaticamente a
      ouvidoria do caso. Reproduz o comportamento do Access (FrmCadAcomp):
      ao salvar este acompanhamento, o formulário FrmEncerraOuvidoria
      era aberto automaticamente.
    """
    # ── Valida que o caso existe ──────────────────────────────────────────────
    caso = db.query(Caso).filter(Caso.TbCasoNumCaso == data.TbAcomCaso).first()
    if not caso:
        raise ValueError(f"Caso {data.TbAcomCaso} não está cadastrado.")

    # ── Valida o prazo ────────────────────────────────────────────────────────
    # O prazo é para o futuro — não faz sentido criar um prazo no passado.
    if data.TbAcompPrazo and data.TbAcompPrazo.date() < date.today():
        raise ValueError("O prazo não pode ser menor que a data do dia.")

    # ── Persiste o acompanhamento ─────────────────────────────────────────────
    acomp = Acompanhamento(**data.model_dump())
    db.add(acomp)
    db.commit()
    db.refresh(acomp)

    # ── Gatilho de ouvidoria ──────────────────────────────────────────────────
    if data.TbAcompAcao == ACAO_CONCLUI_OUVIDORIA:
        _encerrar_ouvidoria_automatico(db, caso)

    return acomp


def atualizar_acompanhamento(
    db: Session, codigo: int, data: AcompanhamentoUpdate
) -> Acompanhamento:
    """
    Atualiza um acompanhamento existente.

    Regras:
      - Se alterar a ação para "Encaminhamento", órgão deve estar preenchido.
        Verifica tanto no update quanto no valor atual do banco.
      - Se alterar para "Concluída para Ouvidoria", dispara o encerramento.
    """
    acomp = db.query(Acompanhamento).filter(Acompanhamento.tbcodigo == codigo).first()
    if not acomp:
        raise ValueError("Acompanhamento não encontrado.")

    # Pega apenas os campos que foram enviados
    updates = data.model_dump(exclude_unset=True)

    # ── Valida Encaminhamento ─────────────────────────────────────────────────
    if "TbAcompAcao" in updates and updates["TbAcompAcao"] == "Encaminhamento":
        # Usa o órgão do update OU o que já está no banco
        orgao = updates.get("TbAcompOrgao") or acomp.TbAcompOrgao
        if not orgao:
            raise ValueError("Informe o órgão para onde foi feito o encaminhamento.")

    # ── Aplica as atualizações ────────────────────────────────────────────────
    for campo, valor in updates.items():
        setattr(acomp, campo, valor)

    db.commit()
    db.refresh(acomp)

    # ── Gatilho de ouvidoria (também ao atualizar) ────────────────────────────
    nova_acao = updates.get("TbAcompAcao")
    if nova_acao == ACAO_CONCLUI_OUVIDORIA:
        caso = db.query(Caso).filter(Caso.TbCasoNumCaso == acomp.TbAcomCaso).first()
        if caso:
            _encerrar_ouvidoria_automatico(db, caso)

    return acomp


def _encerrar_ouvidoria_automatico(db: Session, caso: Caso) -> None:
    """
    Encerra automaticamente a ouvidoria do caso.

    Só age se a ouvidoria ainda estiver aberta (TbEncerradoOuvidoria != "Sim").
    O "guard clause" (if ... return) evita encerrar duas vezes o mesmo caso,
    que poderia sobrescrever a data de encerramento já registrada.

    Reproduz o FrmEncerraOuvidoria do Access que abria automaticamente
    ao salvar um acompanhamento com ação "Concluída para Ouvidoria".
    """
    # Guard: já encerrada → não faz nada
    if caso.TbEncerradoOuvidoria == "Sim":
        return

    caso.TbEncerradoOuvidoria = "Sim"
    caso.TbDtEncerradoOuvidoria = datetime.now()
    db.commit()


def listar_por_caso(db: Session, num_caso: int) -> list[type[Acompanhamento]]:
    """
    Retorna todos os acompanhamentos de um caso, ordenados do mais recente
    para o mais antigo (desc = descrescente).

    list[type[Acompanhamento]] é o type hint de retorno — lista de objetos
    da classe Acompanhamento.
    """
    return (
        db.query(Acompanhamento)
        .filter(Acompanhamento.TbAcomCaso == num_caso)
        .order_by(Acompanhamento.TbAcompdata.desc())  # mais recente primeiro
        .all()
    )
