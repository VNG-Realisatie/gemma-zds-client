import requests_mock

from zds_client import Client

SCHEMA = {
    "openapi": "3.0.0",
    "servers": [{"url": "/api/v1"}],
    "paths": {
        "some-resource/{id}": {
            "delete": {"operationId": "some-resource_delete"},
            "parameters": [],
        },
    },
}


def test_delete_request():
    auth = {"client_id": "yes", "secret": "oh-no"}
    Client.load_config(dummy={"scheme": "https", "host": "example.com", "auth": auth})
    client = Client("dummy")
    client._schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.delete("https://example.com/api/v1/some-resource/1", status_code=204)

        client.delete("some-resource", id=1)

    assert m.last_request.method == "DELETE"
    assert "Authorization" in m.last_request.headers


def test_delete_request_explicit_url():
    auth = {"client_id": "yes", "secret": "oh-no"}
    Client.load_config(dummy={"scheme": "https", "host": "example.com", "auth": auth})
    client = Client("dummy")
    client._schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.delete("https://example.com/api/v1/some-resource/1", status_code=204)

        client.delete("some-resource", url="https://example.com/api/v1/some-resource/1")

    assert m.last_request.method == "DELETE"
    assert "Authorization" in m.last_request.headers
