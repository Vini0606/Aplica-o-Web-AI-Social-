# auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext # Importar para hash de senhas
from datetime import datetime, timedelta # Importar para expiração do token
from typing import Optional # Importar para tipo opcional

from models import Usuario, get_db # Importe Usuario e get_db do seu models.py
from config import settings # Importe suas configurações para acessar SECRET_KEY e ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Suas configurações JWT (vindo de settings)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Contexto para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funções Auxiliares de Autenticação (anteriormente em auth_handler.py) ---

def verify_password(plain_password: str, hashed_password: str):
    """Verifica se uma senha em texto simples corresponde a um hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(SECRET_KEY), algorithm=str(ALGORITHM))
    return encoded_jwt

# --- Função get_user (anteriormente em auth_handler.py ou indefinida) ---

def get_user(db: Session, email: str):
    """Busca um usuário pelo email no banco de dados."""
    return db.query(Usuario).filter(Usuario.email == email).first()

# --- Função de Dependência do FastAPI ---

async def get_current_active_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Verifica o token JWT e retorna o usuário ativo associado.
    Usado como dependência nas rotas protegidas.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[str(ALGORITHM)])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=email) # Agora get_user está definida no mesmo arquivo
    if user is None:
        raise credentials_exception
    if not user.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return user