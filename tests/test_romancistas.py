from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from madr_api.models import Romancista


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


@pytest.mark.asyncio
async def test_romancista_case_insensitive_unique(session, romancista):
    duplicado = Romancista(nome='MACHADO DE ASSIS')

    session.add(duplicado)

    with pytest.raises(IntegrityError):
        await session.commit()

    await session.rollback()


def test_create_romancista_integrity_error(client, token):
    with (
        patch(
            'sqlalchemy.ext.asyncio.AsyncSession.commit',
            new_callable=AsyncMock,
        ) as mock_commit,
        patch(
            'sqlalchemy.ext.asyncio.AsyncSession.rollback',
            new_callable=AsyncMock,
        ) as mock_rollback,
    ):
        mock_commit.side_effect = IntegrityError(
            'INSERT INTO romancistas',
            {},
            Exception('Unique constraint violation'),
        )

        response = client.post(
            '/romancista/',
            headers={'Authorization': f'Bearer {token}'},
            json={'nome': 'Machado de Assis'},
        )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Romancista already exists',
    }

    mock_commit.assert_awaited_once()
    mock_rollback.assert_awaited_once()


def test_create_romancista_normalization(client, token):
    response = client.post(
        '/romancista/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': '  MACHADO    DE    ASSIS  '},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['nome'] == 'MACHADO DE ASSIS'


def test_create_romancista_empty_name(client, token):
    response = client.post(
        '/romancista/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': '  '},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert 'The name cannot be empty' in response.json()['detail'][0]['msg']


def test_read_romancistas(client, romancista):
    response = client.get(
        '/romancista/',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'romancistas': [{'id': romancista.id, 'nome': romancista.nome}]
    }


def test_read_romancistas_empty(client):
    response = client.get(
        '/romancista/',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'romancistas': []}


@pytest.mark.asyncio
async def test_read_romancistas_filter_name(client, romancista, session):
    outro_romancista = Romancista(nome='clarice lispector')

    session.add(outro_romancista)
    await session.commit()

    response = client.get(
        '/romancista/',
        params={'nome': 'machado'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'romancistas': [{'id': romancista.id, 'nome': 'machado de assis'}]
    }


@pytest.mark.asyncio
async def test_read_romancistas_partial_name(client, romancista):
    response = client.get(
        '/romancista/',
        params={'nome': 'assis'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'romancistas': [{'id': romancista.id, 'nome': 'machado de assis'}]
    }


@pytest.mark.asyncio
async def test_read_romancista_pagination(client, session, romancista):

    clarice = Romancista(nome='Clarice Lispector')
    jose = Romancista(nome='Jose de Alencar')

    session.add_all([clarice, jose])
    await session.commit()
    await session.refresh(clarice)

    response = client.get('/romancista/', params={'limit': 1, 'offset': 1})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'romancistas': [{'id': clarice.id, 'nome': 'Clarice Lispector'}]
    }


def test_read_romancista_normalization(client, romancista):
    response = client.get(
        '/romancista/', params={'nome': '  MACHADO    DE    ASSIS  '}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'romancistas': [{'id': romancista.id, 'nome': 'machado de assis'}]
    }


def test_read_romancistas_no_match(client, romancista):
    response = client.get('/romancista/', params={'nome': 'tolkien'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'romancistas': []}


def test_read_romancista_by_id(client, romancista):
    response = client.get(f'/romancista/{romancista.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': romancista.id, 'nome': romancista.nome}


def test_read_romancist_by_id_not_found(client):
    response = client.get('/romancista/99999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista not found'}


def test_read_romancista_invalid_id(client):
    response = client.get('/romancista/abc')

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_romancista(client, romancista, token):
    response = client.put(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'clarice lispector'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': romancista.id,
        'nome': 'clarice lispector',
    }


def test_update_romancista_not_found(client, token):
    response = client.put(
        '/romancista/99999',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'clarice lispector'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista not found'}


@pytest.mark.asyncio
async def test_update_romancista_duplicated(
    client, token, romancista, session
):

    clarice = Romancista(nome='Clarice Lispector')

    session.add(clarice)
    await session.commit()
    await session.refresh(clarice)

    response = client.put(
        f'/romancista/{clarice.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'machado de assis'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Romancista already exists'}


def test_update_romancista_without_token(romancista, client):
    response = client.put(
        f'/romancista/{romancista.id}',
        json={'nome': 'clarice lispector'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_romancista_invalid_token(romancista, client):
    response = client.put(
        f'/romancista/{romancista.id}',
        headers={'Authorization': 'Bearer invalid_token'},
        json={'nome': 'clarice lispector'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_update_romancista_empty_name(client, romancista, token):
    response = client.put(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': '   '},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_romancista_normalization(client, romancista, token):
    response = client.put(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': '  CLARICE    LISPECTOR  '},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': romancista.id,
        'nome': 'CLARICE LISPECTOR',
    }


def test_update_romancista_persistence(client, romancista, token):
    response = client.put(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'clarice lispector'},
    )

    assert response.status_code == HTTPStatus.OK

    response_get = client.get(f'/romancista/{romancista.id}')

    assert response_get.status_code == HTTPStatus.OK
    assert response_get.json() == {
        'id': romancista.id,
        'nome': 'clarice lispector',
    }


def test_delete_romancista(client, romancista, token):
    response = client.delete(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_romancista_not_found(client, token):
    response = client.delete(
        '/romancista/99999',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista not found'}


def test_delete_romancista_without_token(client, romancista):
    response = client.delete(
        '/romancista/{romancista.id}',
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_delete_romancista_invalid_token(client, romancista):
    response = client.delete(
        '/romancista/{romancista.id}',
        headers={'Authorization': 'Bearer invalid_token'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_delete_romancista_persistence(client, romancista, token):
    response = client.delete(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    response_get = client.get(f'/romancista/{romancista.id}')

    assert response_get.status_code == HTTPStatus.NOT_FOUND
    assert response_get.json() == {'detail': 'Romancista not found'}
