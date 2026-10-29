from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AccountCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class AccountPublic(BaseModel):
    id: int
    email: EmailStr
    username: str
    model_config = ConfigDict(from_attributes=True)


class RomancistaCreate(BaseModel):
    nome: str


class RomancistaPublic(BaseModel):
    id: int
    nome: str


class LivroCreate(BaseModel):
    titulo: str
    ano: int = Field(ge=1)
    romancista_id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)


class UserList(BaseModel):
    users: list[AccountPublic]
