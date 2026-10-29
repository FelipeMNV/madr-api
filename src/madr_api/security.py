from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr_api.database import get_session
from madr_api.models import User
from madr_api.settings import Settings

oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/token')
pwd_context = PasswordHash.recommended()
settings = Settings()


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password_hash(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire})

    encoded_jwt = encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)

    return encoded_jwt


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_schema),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject_user = payload.get('sub')
        if not subject_user:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await session.scalar(
        select(User).where(User.username == subject_user)
    )
    if not user:
        raise credentials_exception

    return user
