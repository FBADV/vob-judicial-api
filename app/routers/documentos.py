from fastapi import APIRouter, Depends, HTTPException
from ..auth.security import get_current_user

router = APIRouter()

@router.get("/{doc_id}/resumo")
def ver_resumo_documento(doc_id: int, current_user: str = Depends(get_current_user)):
    """
    Retorna o resumo (gerado por IA/ML) de um documento específico.
    """
    # Stub response
    if doc_id == 0:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    return {
        "doc_id": doc_id,
        "resumo": "Este documento trata-se de uma petição inicial solicitando danos morais...",
        "generated_at": "2023-10-27T10:00:00Z"
    }
