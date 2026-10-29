from http import HTTPStatus


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
