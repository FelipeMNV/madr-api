from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr_api.models import Livro, Romancista, User
from madr_api.schemas import LivroCreate, LivroPublic
from madr_api.security import get_current_user, get_session

router = APIRouter(prefix='/livros', tags=['livros'])
T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=LivroPublic)
async def create_livro(
    livro: LivroCreate, session: T_Session, current_user: CurrentUser
):
    romancista_db = await session.scalar(
        select(Romancista).where(Romancista.id == livro.romancista_id)
    )
    if not romancista_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Romancista not found'
        )

    db_livro = Livro(
        titulo=livro.titulo, ano=livro.ano, romancista_id=livro.romancista_id
    )

    session.add(db_livro)
    await session.commit()
    await session.refresh(db_livro)

    return db_livro
