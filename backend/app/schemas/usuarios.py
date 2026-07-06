from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=3, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)


class UsuarioUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=3, max_length=120)
    senha: str | None = Field(default=None, min_length=8, max_length=128)


class UsuarioResponse(BaseModel):
    id: int
    codigo: str
    nome: str
    email: EmailStr
    criado_em: datetime
    ultimo_login: datetime | None


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1)


class AuthResponse(BaseModel):
    token: str
    nome: str
    usuario: UsuarioResponse
