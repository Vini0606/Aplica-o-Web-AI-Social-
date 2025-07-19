# auth/auth_routes.py (novo router de autenticação)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from models import get_db, Usuario
from auth.auth_schemas import UsuarioCreate, UsuarioLogin, Token
from auth.auth_utils import get_password_hash, verify_password, create_access_token
from auth.dependencies import get_current_active_user
from config import settings
from api.v1.schemas.user import UserCreate, UserResponse

auth_router = APIRouter(prefix="/auth", tags=["Autenticação"])

@auth_router.post("/register", response_model=UsuarioCreate)
def register_user(user_data: UsuarioCreate, db: Session = Depends(get_db)):
    db_user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = get_password_hash(user_data.senha)
    new_user = Usuario(nome=user_data.nome, email=user_data.email, senha=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_router.post("/login", response_model=Token)
async def login_for_access_token(form_data: UsuarioLogin, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == form_data.email).first()
    if not user or not verify_password(form_data.senha, user.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/master-register-user", response_model=UserResponse)
async def master_register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Permite que um usuário mestre (admin=True) registre novos usuários.
    """
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas usuários administradores podem registrar novos usuários."
        )

    db_user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registrado.")

    hashed_password = get_password_hash(user_data.senha)
    new_user = Usuario(
        nome=user_data.nome,
        email=user_data.email,
        senha=hashed_password,
        admin=user_data.admin # Permite que o master defina se o novo usuário é admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user