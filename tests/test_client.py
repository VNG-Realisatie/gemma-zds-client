from unittest.mock import patch

import pytest

from zds_client import Client, extract_params, get_operation_url
from zds_client.client import get_headers


@pytest.mark.parametrize(
    "detail_url,expected_base_path",
    [
        (
            "https://example.com/api/v1/zaken/7C61204C-BFD8-4A66-B826-5DF8CB7F9A60",
            "/api/v1/",
        ),
        (
            "https://example.com/api/v1/zaken/7c61204c-bfd8-4a66-b826-5df8cb7f9a60",
            "/api/v1/",
        ),
        (
            "https://api.example.com/v1/zaken/7c61204c-bfd8-4a66-b826-5df8cb7f9a60",
            "/v1/",
        ),
        ("https://api.example.com/zaken/7c61204c-bfd8-4a66-b826-5df8cb7f9a60", "/"),
        (
            "https://example.com/api/v1/zaken/7c61204c-bfd8-4a66-b826-5df8cb7f9a60/"
            "informatieobjecten/a7bdfe04-fb17-46f8-9884-541f5d7611f8",
            "/api/v1/",
        ),
    ],
)
def test_client_from_detail_url(detail_url, expected_base_path):
    client = Client.from_url(detail_url)
    assert client.base_path == expected_base_path


def test_client_from_url_thread_safe():
    client1 = Client.from_url(
        "https://example.com/api/v1/zaken/7C61204C-BFD8-4A66-B826-5DF8CB7F9A60"
    )
    client2 = Client.from_url(
        "https://example2.com/api/v2/zaken/7C61204C-BFD8-4A66-B826-5DF8CB7F9A60"
    )

    assert client1.base_url == "https://example.com/api/v1/"
    assert client2.base_url == "https://example2.com/api/v2/"


def test_fetch_schema_caching():
    """
    Assert that the same schema is not necessarily downloaded multiple times.
    """
    Client.load_config(
        dummy={"scheme": "https", "host": "example.com"},
        dummy2={"scheme": "https", "host": "example2.com"},
    )
    client = Client("dummy")

    with patch("zds_client.oas.requests.get") as mock_get:
        mock_get.return_value.content = "openapi: 3.0.0"
        mock_get.return_value.headers = {}

        client.fetch_schema()

        mock_get.assert_called_once_with(
            "https://example.com/api/v1/schema/openapi.yaml", {"v": "3"}
        )

        # fetch it again - no extra calls should be made
        client.fetch_schema()

        mock_get.assert_called_once_with(
            "https://example.com/api/v1/schema/openapi.yaml", {"v": "3"}
        )

        # different URL, even different client instance
        client2 = Client("dummy2")

        client2.fetch_schema()

        assert mock_get.call_count == 2
        mock_get.assert_called_with(
            "https://example2.com/api/v1/schema/openapi.yaml", {"v": "3"}
        )


def test_schema_with_local_references():
    Client.load_config(
        dummy={"scheme": "https", "host": "example.com"},
    )
    client = Client("dummy")

    client._schema = {
        "openapi": "3.0.0",
        "servers": [{"url": "/api/v1"}],
        "paths": {
            "/api/packages/{packageId}": {
                "get": {
                    "tags": ["Packages"],
                    "operationId": "api.packages._packageId.get",
                    "summary": "Retrieves a specified package.",
                    "description": "Retrieves information about a single document package.",
                    "parameters": [{"$ref": "#/components/parameters/packageId"}],
                }
            }
        },
        "components": {
            "parameters": {
                "packageId": {
                    "name": "packageId",
                    "description": "The unique package id.",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "string",
                        "example": "asd0sdf08gdfg3njkfg0345dg=",
                    },
                }
            }
        },
    }

    # Parameter #/components/parameters/packageId has value of 'in' != "headers", so no headers will be returned
    headers = get_headers(spec=client._schema, operation="api.packages._packageId.get")
    assert headers == {}


def test_regression_double_slashes():
    object_url = "http://example.com/api/v1/zaken/28dcfc90-2d26-4d4e-8261-a9202ee56185"
    client = Client.from_url(object_url)
    # prevents http request to fetch the schema
    client._schema = {
        "openapi": "3.0.0",
        "servers": [{"url": "/api/v1"}],
        "paths": {
            "/zaken/{zaak_uuid}/informatieobjecten": {
                "post": {"operationId": "zaakinformatieobject_create"}
            }
        },
    }
    pattern = get_operation_url(
        client.schema, "zaakinformatieobject_create", pattern_only=True
    )
    params = extract_params("{}/irrelevant".format(object_url), pattern)

    url = get_operation_url(
        client.schema, "zaakinformatieobject_create", base_url=client.base_url, **params
    )

    assert (
        url == "/api/v1/zaken/28dcfc90-2d26-4d4e-8261-a9202ee56185/informatieobjecten"
    )
