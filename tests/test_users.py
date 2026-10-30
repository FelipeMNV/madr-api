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


def test_update_user(user, client, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'newpassword',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': user.id,
    }

    login_response = client.post(
        '/auth/token',
        data={'username': 'bob', 'password': 'newpassword'},
    )

    assert login_response.status_code == HTTPStatus.OK
    assert user.password != 'newpassword'
    assert verify_password_hash('newpassword', user.password)


def test_update_user_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'bobnewpassword',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}


def test_update_user_without_token(client, user):
    response = client.put(
        f'users/{user.id}',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'bobpassword',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_user_invalid_token(client, user):
    response = client.put(
        f'users/{user.id}',
        headers={'Authorization': 'Bearer invalido'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'bobpassword',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_update_user_duplicate_email(client, user, token, other_user):
    response = client.put(
        f'users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'felipe',
            'email': other_user.email,
            'password': 'felipepassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_update_user_duplicate_username(client, user, token, other_user):
    response = client.put(
        f'users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            'email': 'felipe@example.com',
            'password': 'felipepassword',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}
