import requests_mock

from zds_client import Client

SCHEMA = {
    "openapi": "3.0.0",
    "paths": {},
}


def test_client_level_logging_hook():
    logs = []

    def log(response, *args, **kwargs):
        logs.append((response.request, response))

    client = Client("https://example.com/api/v1", request_hooks={"response": log})
    client.schema = SCHEMA

    with requests_mock.Mocker() as m:
        m.get("https://example.com/api/v1/foo", json={"mocked": "response"})

        data = client.request("foo", "some-operation")

    assert data == {"mocked": "response"}
    assert len(logs) == 1
    (request, response) = logs[0]
    assert request.method == "GET"
    assert request.path == "/api/v1/foo"
    assert response.status_code == 200
