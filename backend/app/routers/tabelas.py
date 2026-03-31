from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_nivel
from app.models.tabelas_aux import (
    MotivoAtendimento, MotivoEncerramento, MotivoRestauracao,
    TipoAcao, TipoEvento, ChegouPrograma, Orgao, Municipio, MotivoVisita
)
from app.models.tecnico import Tecnico

router = APIRouter(prefix="/tabelas", tags=["Tabelas Auxiliares"])


# ── Schemas inline para tabelas simples ──────────────────────

class DescricaoIn(BaseModel):
    descricao: str


class OrgaoIn(BaseModel):
    TbNomeOrgao: str
    TbSiglaOrgao: Optional[str] = None


class TecnicoIn(BaseModel):
    TbNomeTecnico: str
    TbSenha: str
    TbNivel: Optional[int] = 1
    TbStatus: Optional[str] = "Ativo"


class TecnicoUpdate(BaseModel):
    TbSenha: Optional[str] = None
    TbNivel: Optional[int] = None
    TbStatus: Optional[str] = None


# ── Utilitário ────────────────────────────────────────────────

def _get_or_404(db, model, pk_col, pk_val, label="Registro"):
    obj = db.query(model).filter(pk_col == pk_val).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{label} não encontrado")
    return obj


# ── Motivos de Atendimento ────────────────────────────────────

@router.get("/motivos-atendimento")
def listar_motivos_atendimento(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(MotivoAtendimento).all()


@router.post("/motivos-atendimento", status_code=201)
def criar_motivo_atendimento(data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = MotivoAtendimento(TbDescricaoMotivo=data.descricao)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/motivos-atendimento/{codigo}")
def atualizar_motivo_atendimento(codigo: int, data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, MotivoAtendimento, MotivoAtendimento.Codigo, codigo, "Motivo de atendimento")
    obj.TbDescricaoMotivo = data.descricao
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/motivos-atendimento/{codigo}", status_code=204)
def excluir_motivo_atendimento(codigo: int, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, MotivoAtendimento, MotivoAtendimento.Codigo, codigo, "Motivo de atendimento")
    db.delete(obj)
    db.commit()


# ── Motivos de Encerramento ───────────────────────────────────

@router.get("/motivos-encerramento")
def listar_motivos_encerramento(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(MotivoEncerramento).all()


@router.post("/motivos-encerramento", status_code=201)
def criar_motivo_encerramento(data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = MotivoEncerramento(descricaomotivo=data.descricao)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/motivos-encerramento/{codigo}")
def atualizar_motivo_encerramento(codigo: int, data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, MotivoEncerramento, MotivoEncerramento.Codigo, codigo, "Motivo de encerramento")
    obj.descricaomotivo = data.descricao
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/motivos-encerramento/{codigo}", status_code=204)
def excluir_motivo_encerramento(codigo: int, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, MotivoEncerramento, MotivoEncerramento.Codigo, codigo, "Motivo de encerramento")
    db.delete(obj)
    db.commit()


# ── Motivos de Restauração ────────────────────────────────────

@router.get("/motivos-restauracao")
def listar_motivos_restauracao(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(MotivoRestauracao).all()


@router.post("/motivos-restauracao", status_code=201)
def criar_motivo_restauracao(data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = MotivoRestauracao(DescricaoRestauracao=data.descricao)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/motivos-restauracao/{codigo}")
def atualizar_motivo_restauracao(codigo: int, data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, MotivoRestauracao, MotivoRestauracao.Codigo, codigo, "Motivo de restauração")
    obj.DescricaoRestauracao = data.descricao
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/motivos-restauracao/{codigo}", status_code=204)
def excluir_motivo_restauracao(codigo: int, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, MotivoRestauracao, MotivoRestauracao.Codigo, codigo, "Motivo de restauração")
    db.delete(obj)
    db.commit()


# ── Tipos de Ação ─────────────────────────────────────────────

@router.get("/tipo-acao")
def listar_tipo_acao(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(TipoAcao).all()


@router.post("/tipo-acao", status_code=201)
def criar_tipo_acao(data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = TipoAcao(DescricaoAcao=data.descricao)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tipo-acao/{codigo}")
def atualizar_tipo_acao(codigo: int, data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, TipoAcao, TipoAcao.CodAcao, codigo, "Tipo de ação")
    obj.DescricaoAcao = data.descricao
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tipo-acao/{codigo}", status_code=204)
def excluir_tipo_acao(codigo: int, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, TipoAcao, TipoAcao.CodAcao, codigo, "Tipo de ação")
    db.delete(obj)
    db.commit()


# ── Tipos de Evento ───────────────────────────────────────────

@router.get("/tipo-evento")
def listar_tipo_evento(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(TipoEvento).all()


@router.post("/tipo-evento", status_code=201)
def criar_tipo_evento(data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = TipoEvento(tipoevento=data.descricao)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tipo-evento/{codigo}")
def atualizar_tipo_evento(codigo: int, data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, TipoEvento, TipoEvento.codigo, codigo, "Tipo de evento")
    obj.tipoevento = data.descricao
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tipo-evento/{codigo}", status_code=204)
def excluir_tipo_evento(codigo: int, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, TipoEvento, TipoEvento.codigo, codigo, "Tipo de evento")
    db.delete(obj)
    db.commit()


# ── Motivos de Visita ─────────────────────────────────────────

@router.get("/motivos-visita")
def listar_motivos_visita(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(MotivoVisita).all()


@router.post("/motivos-visita", status_code=201)
def criar_motivo_visita(data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = MotivoVisita(motivovisita=data.descricao)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/motivos-visita/{codigo}")
def atualizar_motivo_visita(codigo: int, data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, MotivoVisita, MotivoVisita.Codigo, codigo, "Motivo de visita")
    obj.motivovisita = data.descricao
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/motivos-visita/{codigo}", status_code=204)
def excluir_motivo_visita(codigo: int, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, MotivoVisita, MotivoVisita.Codigo, codigo, "Motivo de visita")
    db.delete(obj)
    db.commit()


# ── Origem (Como Chegou ao Programa) ─────────────────────────

@router.get("/origem")
def listar_origem(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(ChegouPrograma).all()


@router.post("/origem", status_code=201)
def criar_origem(data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = ChegouPrograma(descricaochegouprograma=data.descricao)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/origem/{codigo}")
def atualizar_origem(codigo: int, data: DescricaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, ChegouPrograma, ChegouPrograma.Codigo, codigo, "Origem")
    obj.descricaochegouprograma = data.descricao
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/origem/{codigo}", status_code=204)
def excluir_origem(codigo: int, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, ChegouPrograma, ChegouPrograma.Codigo, codigo, "Origem")
    db.delete(obj)
    db.commit()


# ── Órgãos ────────────────────────────────────────────────────

@router.get("/orgaos")
def listar_orgaos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Orgao).order_by(Orgao.TbNomeOrgao).all()


@router.post("/orgaos", status_code=201)
def criar_orgao(data: OrgaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = Orgao(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/orgaos/{codigo}")
def atualizar_orgao(codigo: int, data: OrgaoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, Orgao, Orgao.CodigoOrgao, codigo, "Órgão")
    obj.TbNomeOrgao = data.TbNomeOrgao
    if data.TbSiglaOrgao is not None:
        obj.TbSiglaOrgao = data.TbSiglaOrgao
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/orgaos/{codigo}", status_code=204)
def excluir_orgao(codigo: int, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, Orgao, Orgao.CodigoOrgao, codigo, "Órgão")
    db.delete(obj)
    db.commit()


# ── Municípios (somente leitura) ──────────────────────────────

@router.get("/municipios")
def listar_municipios(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Municipio).order_by(Municipio.municipio).all()


# ── Técnicos ──────────────────────────────────────────────────

@router.get("/tecnicos")
def listar_tecnicos(db: Session = Depends(get_db), _=Depends(require_nivel(2))):
    return db.query(Tecnico).filter(Tecnico.TbStatus != "Inativo").all()


@router.post("/tecnicos", status_code=201)
def criar_tecnico(data: TecnicoIn, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = Tecnico(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tecnicos/{codigo}")
def atualizar_tecnico(codigo: int, data: TecnicoUpdate, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    obj = _get_or_404(db, Tecnico, Tecnico.CodTecnico, codigo, "Técnico")
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(obj, campo, valor)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tecnicos/{codigo}", status_code=204)
def excluir_tecnico(codigo: int, db: Session = Depends(get_db), _=Depends(require_nivel(3))):
    """Desativa o técnico em vez de excluir, preservando o histórico."""
    obj = _get_or_404(db, Tecnico, Tecnico.CodTecnico, codigo, "Técnico")
    obj.TbStatus = "Inativo"
    db.commit()
