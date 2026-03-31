# ─────────────────────────────────────────────────────────────────────────────
# SERVICE: Usuário — lógica de negócio para usuários atendidos
# ─────────────────────────────────────────────────────────────────────────────
# Regras implementadas:
#   ✓ O caso vinculado deve existir antes de cadastrar o usuário
#   ✓ Data de cadastro não pode ser futura

from sqlalchemy.orm import Session
from datetime import date
from app.models.usuario import Usuario
from app.models.caso import Caso


def criar_usuario(db: Session, data: dict) -> Usuario:
    """
    Cria um novo usuário vinculado a um caso.

    Recebe 'data' como dict (em vez de schema) porque o router chama
    data.model_dump() antes de chamar este service, para compatibilidade
    com setattr() dinâmico no atualizar_usuario.

    Validações:
      1. O caso informado deve existir no banco.
      2. A data de cadastro não pode ser maior que hoje (não pode cadastrar
         retroativamente com data futura).
    """
    # ── Valida que o caso existe ──────────────────────────────────────────────
    # data.get("tbcaso") retorna None se a chave não existir (não lança KeyError)
    caso = db.query(Caso).filter(Caso.TbCasoNumCaso == data.get("tbcaso")).first()
    if not caso:
        raise ValueError(f"Caso {data.get('tbcaso')} não está cadastrado.")

    # ── Valida data de cadastro ───────────────────────────────────────────────
    dt_cadastro = data.get("tbdtcadastro")
    if dt_cadastro and dt_cadastro.date() > date.today():
        raise ValueError("Data de cadastro não pode ser maior que a data do dia.")

    # ── Persiste o usuário ────────────────────────────────────────────────────
    # **data desempacota o dict como argumentos nomeados do construtor
    usuario = Usuario(**data)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def atualizar_usuario(db: Session, num_cadastro: int, data: dict) -> Usuario:
    """
    Atualiza os dados de um usuário existente.

    O 'data' recebido já vem filtrado com exclude_unset=True do router,
    então só contém os campos que o cliente realmente enviou.

    setattr(usuario, campo, valor) → equivale a usuario.campo = valor
    mas de forma dinâmica (quando o nome do campo é uma variável string).
    """
    usuario = db.query(Usuario).filter(Usuario.tbnumerocadastro == num_cadastro).first()
    if not usuario:
        raise ValueError("Usuário não encontrado.")

    for campo, valor in data.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


def buscar_por_nome(db: Session, nome: str) -> list[Usuario]:
    """
    Busca usuários cujo nome contenha a string informada (case-insensitive).

    .ilike(f"%{nome}%") → LIKE '%nome%' no SQL, mas sem distinção de maiúsculas.
    Útil para a barra de pesquisa na interface.
    """
    return db.query(Usuario).filter(Usuario.tbnome.ilike(f"%{nome}%")).all()
