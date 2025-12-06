from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os

# Env vars
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PFX_PATH = os.getenv("PFX_PATH")
PFX_PASSWORD = os.getenv("PFX_PASSWORD")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

def load_certificate():
    """
    STUB: Carrega o certificado A1 (.pfx) para uso nos conectores.
    Bibliotecas sugeridas: cryptography, OpenSSL (pyopenssl).
    """
    if not PFX_PATH or not os.path.exists(PFX_PATH):
        print("WARN: Certificado A1 não encontrado no caminho especificado via PFX_PATH.")
        return None
    
    print(f"INFO: Carregando certificado de {PFX_PATH}...")
    # Exemplo stub de leitura binária
    try:
        with open(PFX_PATH, "rb") as f:
            pfx_data = f.read()
        # Aqui integraria com cryptography para extrair chave privada/cert
        # ...
        return "CERTIFICADO_CARREGADO_STUB"
    except Exception as e:
        print(f"ERROR: Falha ao carregar certificado: {e}")
        return None
