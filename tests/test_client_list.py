import requests_mock

from zds_client import Client

SCHEMA = {
    "openapi": "3.0.0",
    "servers": [{"url": "/api/v1"}],
    "paths": {
        "some-resource": {
            "get": {
                "operationId": "some-resource_list",
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
        },
    },
}


def test_list_request():
    auth = {"client_id": "yes", "secret": "oh-no"}
    Client.load_config(dummy={"scheme": "https", "host": "example.com", "auth": auth})
    client = Client("dummy")
    client._schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.get("https://example.com/api/v1/some-resource?foo=bar", json=[{"ok": "yes"}])

        response = client.list("some-resource", params={"foo": "bar"})

    assert response == [{"ok": "yes"}]
    assert m.last_request.query == "foo=bar"
    assert "Some-Header" in m.last_request.headers
    assert m.last_request.headers["Some-Header"] == "some-value"
    assert "Authorization" in m.last_request.headers


def test_kwargs_forwarded_to_requests():
    Client.load_config(dummy={"scheme": "https", "host": "example.com"})
    client = Client("dummy")
    client._schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.get("https://example.com/api/v1/some-resource", json=[{"ok": "yes"}])

        client.list(
            "some-resource",
            request_kwargs={
                "headers": {
                    "Other-Header": "value",
                }
            },
        )

    assert "Other-Header" in m.last_request.headers
    assert m.last_request.headers["Other-Header"] == "value"
