from http import HTTPStatus


def test_create_livro(token, client, romancista):
    response = client.post(
        '/livros/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'titulo': 'Dom Casmurro',
            'ano': 1899,
            'romancista_id': romancista.id,
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    data = response.json()

    assert isinstance(data['id'], int)

    assert data == {
        'id': data['id'],
        'titulo': 'Dom Casmurro',
        'ano': 1899,
        'romancista_id': romancista.id,
    }


def test_create_livro_romancista_not_found(token, client):
    response = client.post(
        '/livros/',
        headers={'Authorization': f'Bearer {token}'},
        json={'titulo': 'Dom Casmurro', 'ano': 1899, 'romancista_id': 3},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista not found'}


def test_create_livro_without_token(romancista, client):
    response = client.post(
        '/livros/',
        json={
            'titulo': 'Dom Casmurro',
            'ano': 1899,
            'romancista_id': romancista.id,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_create_livro_invalid_token(client, romancista):
    response = client.post(
        '/livros/',
        headers={'Authorization': 'Bearer invalid_token'},
        json={
            'titulo': 'Dom Casmurro',
            'ano': 1899,
            'romancista_id': romancista.id,
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_create_livro_empty_title(romancista, client, token):
    response = client.post(
        '/livros/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'titulo': '   ',
            'ano': 1899,
            'romancista_id': romancista.id,
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    errors = response.json()['detail']

    assert errors[0]['loc'] == ['body', 'titulo']
    assert 'The title cannot be empty' in errors[0]['msg']


def test_create_livro_invalid_year(client, token, romancista):
    response = client.post(
        '/livros/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'titulo': 'Dom Casmurro',
            'ano': -1899,
            'romancista_id': romancista.id,
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    errors = response.json()['detail']

    assert errors[0]['loc'] == ['body', 'ano']
    assert errors[0]['type'] == 'greater_than_equal'
