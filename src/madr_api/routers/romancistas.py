from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr_api.models import Romancista, User
from madr_api.schemas import RomancistaCreate, RomancistaPublic
from madr_api.security import get_current_user, get_session

router = APIRouter(prefix='/romancista', tags=['romancistas'])
T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=RomancistaPublic
)
async def create_romancista(
    romancista: RomancistaCreate, session: T_Session, current_user: CurrentUser
):
    nome_normalizado = ' '.join(romancista.nome.split()).lower()

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
