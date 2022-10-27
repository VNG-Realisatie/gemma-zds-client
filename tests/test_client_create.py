import requests_mock

from zds_client import Client, ClientAuth

SCHEMA = {
    "openapi": "3.0.0",
    "servers": [{"url": "/api/v1"}],
    "paths": {
        "some-resource": {
            "post": {
                "operationId": "some-resource_create",
            },
            "parameters": [],
        },
    },
}


def test_create_request():
    client = Client(
        "https://example.com/api/v1",
        auth=ClientAuth(client_id="yes", secret="oh-no"),
    )
    client.schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.post(
            "https://example.com/api/v1/some-resource", json={"id": 1}, status_code=201
        )

        response = client.create("some-resource", data={"foo": "bar"})

    assert response["id"] == 1
    assert m.last_request.json() == {"foo": "bar"}


def test_create_request_extra_headers():
    client = Client(
        "https://example.com/api/v1",
        auth=ClientAuth(client_id="yes", secret="oh-no"),
    )
    client.schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.post(
            "https://example.com/api/v1/some-resource", json={"id": 1}, status_code=201
        )

        response = client.create(
            "some-resource",
            data={"foo": "bar"},
            request_kwargs={"headers": {"X-Api-Version": "1.0.2"}},
        )

    assert response["id"] == 1
    assert m.last_request.json() == {"foo": "bar"}
    assert m.last_request.headers["X-Api-Version"] == "1.0.2"
