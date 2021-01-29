import requests_mock

from zds_client import Client

SCHEMA = {
    "openapi": "3.0.0",
    "servers": [{"url": "/api/v1"}],
    "paths": {
        "some-resource/{id}": {
            "get": {
                "operationId": "some-resource_read",
                "parameters": [
                    {
                        "name": "Some-Header",
                        "in": "header",
                        "required": True,
                        "schema": {
                            "type": "string",
                            "enum": [
                                "some-value",
                            ],
                        },
                    },
                ],
            },
            "parameters": [],
        },
    },
}


def test_read_request():
    auth = {"client_id": "yes", "secret": "oh-no"}
    Client.load_config(dummy={"scheme": "https", "host": "example.com", "auth": auth})
    client = Client("dummy")
    client._schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.get("https://example.com/api/v1/some-resource/1", json={"ok": "yes"})

        response = client.retrieve("some-resource", id=1)

    assert response == {"ok": "yes"}
    assert "Some-Header" in m.last_request.headers
    assert m.last_request.headers["Some-Header"] == "some-value"
    assert "Authorization" in m.last_request.headers


def test_read_request_explicit_url():
    Client.load_config(dummy={"scheme": "https", "host": "example.com"})
    client = Client("dummy")
    client._schema = SCHEMA
    resource_url = "https://example.com/api/v1/some-resource/2"

    with requests_mock.Mocker() as m:
        m.get(resource_url, json={"ok": "yarp"})

        response = client.retrieve("some-resource", url=resource_url)

    assert response == {"ok": "yarp"}
    assert m.last_request.url == resource_url


def test_kwargs_forwarded_to_requests():
    Client.load_config(dummy={"scheme": "https", "host": "example.com"})
    client = Client("dummy")
    client._schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.get("https://example.com/api/v1/some-resource/1", json=[{"ok": "yes"}])

        client.retrieve(
            "some-resource",
            id=1,
            request_kwargs={
                "headers": {
                    "Other-Header": "value",
                }
            },
        )

    assert "Other-Header" in m.last_request.headers
    assert m.last_request.headers["Other-Header"] == "value"
