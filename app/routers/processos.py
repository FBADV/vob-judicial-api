from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..connectors.connector_pje import PJeConnector
from ..connectors.connector_esaj import ESajConnector
from ..models import Processo, Advogado, Andamento
from ..schemas.processo import ProcessoCreate, ProcessoResponse, ProcessoDetail
from ..auth.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ProcessoResponse])
def listar_processos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    processos = db.query(Processo).offset(skip).limit(limit).all()
    return processos

@router.post("/cadastrar", response_model=ProcessoResponse)

def cadastrar_processo(processo: ProcessoCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Verifica duplicidade
    db_processo = db.query(Processo).filter(Processo.numero_cnj == processo.numero_cnj).first()
    if db_processo:
        raise HTTPException(status_code=400, detail="Processo já cadastrado")
    
    # Busca/Cria advogado (simplificado)
    adv = db.query(Advogado).filter(Advogado.oab == processo.advogado_oab).first()
    if not adv:
        adv = Advogado(oab=processo.advogado_oab, nome="Advogado Desconhecido") # Stub name
        db.add(adv)
        db.commit()
        db.refresh(adv)

    novo_processo = Processo(
        numero_cnj=processo.numero_cnj,
        titulo=processo.titulo,
        cliente_nome=processo.cliente_nome,
        valor_causa=processo.valor_causa,
        advogado_id=adv.id
    )
    db.add(novo_processo)
    db.commit()
    db.refresh(novo_processo)
    return novo_processo

@router.get("/{processo_id}", response_model=ProcessoDetail)
def consultar_processo(processo_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    processo = db.query(Processo).filter(Processo.id == processo_id).first()
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return processo
