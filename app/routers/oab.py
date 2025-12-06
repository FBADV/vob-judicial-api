from fastapi import APIRouter, Depends, HTTPException
from ..auth.security import get_current_user
from ..schemas.oab import OABImportRequest, OABImportResponse
from ..worker import job_importar_processos

router = APIRouter()

@router.post("/importar", response_model=OABImportResponse)
def importar_por_oab(request: OABImportRequest, current_user: str = Depends(get_current_user)):
    """
    Inicia um job em background (Celery) para varrer tribunais buscando processos dessa OAB.
    """
    # Prepara credenciais para o worker
    credenciais = {
        "auth_method": request.auth_method,
        "login": request.login,
        "senha": request.senha,
        "pfx_password": request.pfx_password
    }

    # Dispara a task no Celery
    task = job_importar_processos.delay(request.oab_num, request.oab_uf, credenciais)
    
    return OABImportResponse(
        task_id=task.id,
        message=f"Importação iniciada para OAB {request.oab_num}/{request.oab_uf}",
        status="queued"
    )

