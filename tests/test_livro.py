from http import HTTPStatus

import pytest

from madr_api.models import Livro


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


def test_read_livros(client, livro):
    response = client.get('/livros/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'livros': [
            {
                'id': livro.id,
                'titulo': livro.titulo,
                'ano': livro.ano,
                'romancista_id': livro.romancista_id,
            }
        ]
    }


def test_read_livros_empty(client):
    response = client.get(
        '/livros/',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'livros': []}


@pytest.mark.asyncio
async def test_read_livros_filter_title(client, livro, session):
    outro_livro = Livro(
        titulo='O Pequeno Principe',
        ano=1909,
        romancista_id=livro.romancista_id,
    )

    session.add(outro_livro)
    await session.commit()

    response = client.get('/livros/', params={'titulo': 'Dom Casmurro'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'livros': [
            {
                'id': livro.id,
                'titulo': livro.titulo,
                'ano': livro.ano,
                'romancista_id': livro.romancista_id,
            }
        ]
    }


@pytest.mark.asyncio
async def test_read_livros_partial_name(client, livro):
    response = client.get('/livros/', params={'titulo': 'dom'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'livros': [
            {
                'id': livro.id,
                'titulo': livro.titulo,
                'ano': livro.ano,
                'romancista_id': livro.romancista_id,
            }
        ]
    }


@pytest.mark.asyncio
async def test_read_livros_pagination(client, session, livro):

    livro_um = Livro(
        titulo='O Pequeno Principe',
        ano=1909,
        romancista_id=livro.romancista_id,
    )
    livro_dois = Livro(
        titulo='A Pequena Sereia', ano=1904, romancista_id=livro.romancista_id
    )

    session.add_all([livro_um, livro_dois])
    await session.commit()
    await session.refresh(livro_um)

    response = client.get('/livros/', params={'limit': 1, 'offset': 1})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'livros': [
            {
                'id': livro_um.id,
                'titulo': livro_um.titulo,
                'ano': livro_um.ano,
                'romancista_id': livro_um.romancista_id,
            }
        ]
    }


def test_read_livros_by_romancista_id_and_title(client, livro, romancista):
    response = client.get(
        '/livros/', params={'romancista_id': romancista.id, 'titulo': 'Dom'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'livros': [
            {
                'id': livro.id,
                'titulo': livro.titulo,
                'ano': livro.ano,
                'romancista_id': livro.romancista_id,
            }
        ]
    }


def test_read_livros_no_match(client, livro):
    response = client.get(
        '/livros/',
        params={'titulo': 'Fake Book'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'livros': []}


def test_read_livro_by_id(client, livro):
    response = client.get(f'/livros/{livro.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': livro.id,
        'titulo': livro.titulo,
        'ano': livro.ano,
        'romancista_id': livro.romancista_id,
    }


def test_read_livro_not_found(client):
    response = client.get('/livros/9999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro not found'}


def test_read_livro_invalid_id(client):
    response = client.get('/livros/abc')

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
