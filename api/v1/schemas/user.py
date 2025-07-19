# api/v1/schemas/user.py
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    nome: str = Field(..., description="Nome do usuário")
    email: str = Field(..., description="Email do usuário")
    senha: str = Field(..., description="Senha do usuário")
    admin: bool = False # Permite que o master crie outros admins se desejar

class UserResponse(BaseModel):
    id: int
    nome: str
    email: str
    ativo: bool
    admin: bool

    class Config:
        from_attributes = True # ou orm_mode = True para Pydantic V1