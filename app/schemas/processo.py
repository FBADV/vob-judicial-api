from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Token ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Processo ---
class ProcessoBase(BaseModel):
    numero_cnj: str
    titulo: Optional[str] = None
    cliente_nome: Optional[str] = None
    valor_causa: Optional[str] = None

class ProcessoCreate(ProcessoBase):
    advogado_oab: str # Link via OAB to find Advogado

class ProcessoResponse(ProcessoBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Andamento ---
class AndamentoBase(BaseModel):
    data: datetime
    descricao: str
    conteudo: Optional[str] = None

class AndamentoResponse(AndamentoBase):
    id: int
    class Config:
        from_attributes = True

# --- Full Details ---
class ProcessoDetail(ProcessoResponse):
    andamentos: List[AndamentoResponse] = []
