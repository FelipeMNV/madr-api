from http import HTTPStatus

from madr_api.security import create_access_token


def test_token_without_sub(client):
    token = create_access_token({})

    response = client.get(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_user_not_found(client):
    token = create_access_token({'sub': 'usuario_inexistente'})

    response = client.get(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
