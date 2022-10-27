from unittest.mock import patch

from zds_client import Client, extract_params, get_operation_url
from zds_client.client import get_headers


def test_fetch_schema_caching():
    """
    Assert that the same schema is not necessarily downloaded multiple times.
    """
    client = Client("https://example.com/api/v1")
    client2 = Client("https://example2.com/api/v1/", oas_location="schema/openapi.yaml")

    with patch("zds_client.oas.requests.get") as mock_get:
        mock_get.return_value.content = "openapi: 3.0.0"
        mock_get.return_value.headers = {}

        client.fetch_schema()

        mock_get.assert_called_once_with("https://example.com/api/v1/")

        # fetch it again - no extra calls should be made
        client.fetch_schema()

        mock_get.assert_called_once_with("https://example.com/api/v1/")

        # different URL, even different client instance
        client2.fetch_schema()

        assert mock_get.call_count == 2
        mock_get.assert_called_with("https://example2.com/api/v1/schema/openapi.yaml")


def test_schema_with_local_references():
    client = Client("https://example.com/api/v1")
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


def test_schema_with_non_required_header_params():
    client = Client("https://example.com/api/v1/")
    client._schema = {
        "openapi": "3.0.0",
        "servers": [{"url": "/api/v1"}],
        "paths": {
            "/api/packages/": {
                "get": {
                    "tags": ["Packages"],
                    "operationId": "api.packages._packageId.get",
                    "summary": "Retrieves a specified package.",
                    "description": "Retrieves information about a single document package.",
                    "parameters": [
                        {
                            "in": "header",
                            "name": "Accept-Crs",
                            "description": "test param",
                            "schema": {"type": "string", "enum": ["EPSG:4326"]},
                        }
                    ],
                }
            }
        },
    }

    headers = get_headers(spec=client._schema, operation="api.packages._packageId.get")
    assert headers == {}


def test_schema_non_required_header_params_in_local_references():
    client = Client("https://example.com/api/v1")
    client._schema = {
        "openapi": "3.0.0",
        "servers": [{"url": "/api/v1"}],
        "paths": {
            "/api/packages/": {
                "get": {
                    "tags": ["Packages"],
                    "operationId": "api.packages._packageId.get",
                    "summary": "Retrieves a specified package.",
                    "description": "Retrieves information about a single document package.",
                    "parameters": [{"$ref": "#/components/parameters/testHeader"}],
                }
            }
        },
        "components": {
            "parameters": {
                "testHeader": {
                    "in": "header",
                    "name": "Accept-Crs",
                    "description": "test param",
                    "schema": {"type": "string", "enum": ["EPSG:4326"]},
                },
            }
        },
    }

    headers = get_headers(spec=client._schema, operation="api.packages._packageId.get")
    assert headers == {}


def test_regression_double_slashes():
    object_url = "http://example.com/api/v1/zaken/28dcfc90-2d26-4d4e-8261-a9202ee56185"
    schema = {
        "openapi": "3.0.0",
        "servers": [{"url": "/api/v1"}],
        "paths": {
            "/zaken/{zaak_uuid}/informatieobjecten": {
                "post": {"operationId": "zaakinformatieobject_create"}
            }
        },
    }
    pattern = get_operation_url(
        schema, "zaakinformatieobject_create", pattern_only=True
    )
    params = extract_params("{}/irrelevant".format(object_url), pattern)

    url = get_operation_url(
        schema,
        "zaakinformatieobject_create",
        base_url="http://example.com/api/v1/",
        **params
    )

    assert (
        url == "/api/v1/zaken/28dcfc90-2d26-4d4e-8261-a9202ee56185/informatieobjecten"
    )
