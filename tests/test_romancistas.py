from http import HTTPStatus


def test_create_romancista(client, user, token):
    response = client.post(
        '/romancista/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'machado de assis'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'nome': 'machado de assis',
    }


def test_create_duplicate_romancista(client, token, romancista):
    response = client.post(
        '/romancista/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'MACHADO   DE   ASSIS'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Romancista already exists'}


def test_create_romancista_without_token(client):
    response = client.post('/romancista/', json={'nome': 'machado de assis'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_create_romancista_invalid_token(client):
    response = client.post(
        '/romancista/',
        headers={'Authorization': 'Bearer invalidtoken'},
        json={'nome': 'machado de assis'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_create_romancista_normalization(client, token):
    response = client.post(
        '/romancista/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': '  MACHADO    DE    ASSIS  '},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['nome'] == 'machado de assis'


def test_create_romancista_empty_name(client, token):
    response = client.post(
        '/romancista/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': '  '},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert 'The name cannot be empty' in response.json()['detail'][0]['msg']
