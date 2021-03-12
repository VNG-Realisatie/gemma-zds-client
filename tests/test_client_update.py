import requests_mock

from zds_client import Client

SCHEMA = {
    "openapi": "3.0.0",
    "servers": [{"url": "/api/v1"}],
    "paths": {
        "some-resource/{id}": {
            "put": {
                "operationId": "some-resource_update",
            },
            "patch": {
                "operationId": "some-resource_partial_update",
            },
            "parameters": [],
        },
    },
}


def test_update_request():
    auth = {"client_id": "yes", "secret": "oh-no"}
    Client.load_config(dummy={"scheme": "https", "host": "example.com", "auth": auth})
    client = Client("dummy")
    client._schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.put(
            "https://example.com/api/v1/some-resource/1",
            json={"id": 1},
            status_code=200,
        )

        response = client.update("some-resource", id=1, data={"foo": "bar"})

    assert response["id"] == 1
    assert m.last_request.json() == {"foo": "bar"}
    assert m.last_request.method == "PUT"
    assert "Authorization" in m.last_request.headers


def test_update_request_explicit_url():
    auth = {"client_id": "yes", "secret": "oh-no"}
    Client.load_config(dummy={"scheme": "https", "host": "example.com", "auth": auth})
    client = Client("dummy")
    client._schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.put(
            "https://example.com/api/v1/some-resource/1",
            json={"id": 1},
            status_code=200,
        )

        response = client.update(
            "some-resource",
            url="https://example.com/api/v1/some-resource/1",
            data={"foo": "bar"},
        )

    assert response["id"] == 1
    assert m.last_request.json() == {"foo": "bar"}
    assert m.last_request.method == "PUT"
    assert "Authorization" in m.last_request.headers


def test_partial_update_request():
    auth = {"client_id": "yes", "secret": "oh-no"}
    Client.load_config(dummy={"scheme": "https", "host": "example.com", "auth": auth})
    client = Client("dummy")
    client._schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.patch(
            "https://example.com/api/v1/some-resource/1",
            json={"id": 1},
            status_code=200,
        )

        response = client.partial_update("some-resource", id=1, data={"foo": "bar"})

    assert response["id"] == 1
    assert m.last_request.json() == {"foo": "bar"}
    assert m.last_request.method == "PATCH"
    assert "Authorization" in m.last_request.headers


def test_partial_update_request_explicit_url():
    auth = {"client_id": "yes", "secret": "oh-no"}
    Client.load_config(dummy={"scheme": "https", "host": "example.com", "auth": auth})
    client = Client("dummy")
    client._schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.patch(
            "https://example.com/api/v1/some-resource/1",
            json={"id": 1},
            status_code=200,
        )

        response = client.partial_update(
            "some-resource",
            url="https://example.com/api/v1/some-resource/1",
            data={"foo": "bar"},
        )

    assert response["id"] == 1
    assert m.last_request.json() == {"foo": "bar"}
    assert m.last_request.method == "PATCH"
    assert "Authorization" in m.last_request.headers
