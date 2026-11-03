from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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

    @field_validator('nome')
    @classmethod
    def validar_nomes(cls, nome: str) -> str:
        if not nome.strip():
            raise ValueError('The name cannot be empty')
        return nome


class RomancistaPublic(BaseModel):
    id: int
    nome: str


class LivroCreate(BaseModel):
    titulo: str
    ano: int = Field(ge=1)
    romancista_id: int = Field(gt=0)

    @field_validator('titulo')
    @classmethod
    def validar_titulo(cls, titulo: str) -> str:
        if not titulo.strip():
            raise ValueError('The title cannot be empty')

        return titulo


class LivroPublic(LivroCreate):
    id: int


class LivroList(BaseModel):
    livros: list[LivroPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)


class UserList(BaseModel):
    users: list[AccountPublic]


class RomancistaList(BaseModel):
    romancistas: list[RomancistaPublic]
