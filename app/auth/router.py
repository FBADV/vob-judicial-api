from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .security import create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from ..schemas.processo import Token # Assuming Token schema is there or commonly shared

router = APIRouter()

# Mock user DB
FAKE_USERS_DB = {
    "fred": {
        "username": "fred",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWrn96pzwLoOeMRug9SN1f0y1Z.qHW", # hash for "secret"
        "disabled": False,
    }
}

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
