from pydantic import BaseModel, Field
from typing import Optional, Literal

class OABImportRequest(BaseModel):
    oab_num: str = Field(..., description="Número da OAB (ex: 123456)")
    oab_uf: str = Field(..., description="UF da OAB (ex: SP, MG)")
    auth_method: Literal["a1", "login"] = Field("a1", description="Método de autenticação")
    
    # Credenciais opcionais (em produção, evitar passar senha em plain-text se possível)
    login: Optional[str] = None
    senha: Optional[str] = None
    pfx_password: Optional[str] = None

class OABImportResponse(BaseModel):
    task_id: str
    message: str
    status: str
