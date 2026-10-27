from pydantic import BaseModel, EmailStr, Field


class AccountCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class AccountPublic(BaseModel):
    id: int
    email: EmailStr
    username: str


class RomancistaCreate(BaseModel):
    nome: str


class RomancistaPublic(BaseModel):
    id: int
    nome: str


class LivroCreate(BaseModel):
    titulo: str
    ano: int = Field(ge=1)
    romancista_id: int
