from http import HTTPStatus
from unittest.mock import AsyncMock

from sqlalchemy.exc import IntegrityError

from madr_api.schemas import AccountPublic
from madr_api.security import verify_password_hash


def test_create_users(client):
    response = client.post(
        '/users/',
        json={
            'username': 'felipe',
            'email': 'felipe@example.com',
            'password': 'senha123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'felipe',
        'email': 'felipe@example.com',
    }


def test_user_already_exists_username(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': user.email,
            'password': 'secretpassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_user_already_exists_email(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'other_username',
            'email': user.email,
            'password': 'secretpassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_user_password_hash(user):
    assert user.password != user.clean_password
    assert verify_password_hash(user.clean_password, user.password)


def test_create_user_integrity_error(client, session):
    session.commit = AsyncMock(
        side_effect=IntegrityError(
            statement='INSERT INTO users',
            params={},
            orig=Exception('duplicate key'),
        )
    )
    session.rollback = AsyncMock()

    response = client.post(
        '/users/',
        json={
            'username': 'novo_usuario',
            'email': 'novo@example.com',
            'password': 'novopassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}

    session.rollback.assert_awaited_once()


def test_read_users(token, client, user):
    user_schema = AccountPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_read_users_without_token(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_read_users_invalid_token(client):
    response = client.get(
        '/users/',
        headers={'Authorization': 'Bearer token_invalido'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
