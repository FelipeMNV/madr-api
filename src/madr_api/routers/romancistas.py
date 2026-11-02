from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr_api.models import Romancista, User
from madr_api.schemas import (
    FilterPage,
    RomancistaCreate,
    RomancistaList,
    RomancistaPublic,
)
from madr_api.security import get_current_user, get_session
from madr_api.utils import normalizar_nome

router = APIRouter(prefix='/romancista', tags=['romancistas'])
T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=RomancistaPublic
)
async def create_romancista(
    romancista: RomancistaCreate, session: T_Session, current_user: CurrentUser
):
    nome_normalizado = normalizar_nome(romancista.nome)

    db_romancista = Romancista(nome=nome_normalizado)

    try:
        session.add(db_romancista)
        await session.commit()
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Romancista already exists',
        )

    await session.refresh(db_romancista)
    return db_romancista


@router.get('/', response_model=RomancistaList)
async def read_romancistas(
    session: T_Session,
    filter_page: Annotated[FilterPage, Query()],
    nome: str | None = None,
):
    query = select(Romancista)
    if nome:
        nome_normalizado = normalizar_nome(nome)

        query = query.where(Romancista.nome.ilike(f'%{nome_normalizado}%'))

    query = (
        query
        .order_by(Romancista.id)
        .limit(filter_page.limit)
        .offset(filter_page.offset)
    )

    romancistas = await session.scalars(query)

    return {'romancistas': romancistas.all()}


@router.get('/{romancista_id}', response_model=RomancistaPublic)
async def read_romancista_id(
    session: T_Session,
    romancista_id: int,
):
    romancista = await session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )
    if not romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista not found',
        )

    return romancista


@router.put('/{romancista_id}', response_model=RomancistaPublic)
async def update_romancista(
    romancista_id: int,
    session: T_Session,
    romancista: RomancistaCreate,
    current_user: CurrentUser,
):
    romancista_db = await session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not romancista_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista not found',
        )

    nome_normalizado = normalizar_nome(romancista.nome)

    romancista_db.nome = nome_normalizado

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Romancista already exists',
        )
    await session.refresh(romancista_db)
    return romancista_db


@router.delete(
    '/{romancista_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_romancista(
    romancista_id: int,
    session: T_Session,
    current_user: CurrentUser,
):
    romancista_db = await session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not romancista_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista not found',
        )

    try:
        await session.delete(romancista_db)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Cannot delete romancista with associated books',
        )
