from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr_api.models import Livro, Romancista, User
from madr_api.schemas import FilterPage, LivroCreate, LivroList, LivroPublic
from madr_api.security import get_current_user, get_session
from madr_api.utils import normalizar_texto

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


@router.get('/', status_code=HTTPStatus.OK, response_model=LivroList)
async def read_livros(
    session: T_Session,
    filter_page: Annotated[FilterPage, Query()],
    titulo: str | None = None,
    romancista_id: int | None = None,
):
    query = select(Livro)
    if romancista_id is not None:
        query = query.where(Livro.romancista_id == romancista_id)

    if titulo:
        titulo_filtro = normalizar_texto(titulo)

        if titulo_filtro:
            query = query.where(Livro.titulo.ilike(f'%{titulo_filtro}%'))

    query = (
        query
        .order_by(Livro.id)
        .limit(filter_page.limit)
        .offset(filter_page.offset)
    )
    livros = await session.scalars(query)

    return {'livros': livros.all()}


@router.get('/{livro_id}', response_model=LivroPublic)
async def read_livro_id(
    session: T_Session,
    livro_id: int,
):
    livro = await session.scalar(select(Livro).where(Livro.id == livro_id))
    if not livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro not found',
        )

    return livro


@router.put('/{livro_id}', response_model=LivroPublic)
async def update_livro(
    livro_id: int,
    session: T_Session,
    current_user: CurrentUser,
    livro: LivroCreate,
):

    livro_db = await session.scalar(select(Livro).where(Livro.id == livro_id))

    if not livro_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Livro not found'
        )

    romancista_db = await session.scalar(
        select(Romancista).where(Romancista.id == livro.romancista_id)
    )

    if not romancista_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista not found',
        )

    livro_db.titulo = normalizar_texto(livro.titulo)
    livro_db.ano = livro.ano
    livro_db.romancista_id = livro.romancista_id

    await session.commit()
    await session.refresh(livro_db)

    return livro_db


@router.delete(
    '/{livro_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_livro(
    livro_id: int, session: T_Session, current_user: CurrentUser
):
    livro_db = await session.scalar(select(Livro).where(Livro.id == livro_id))

    if not livro_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Livro not found'
        )

    await session.delete(livro_db)
    await session.commit()
