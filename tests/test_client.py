import pytest

from zds_client import Client


@pytest.mark.parametrize("detail_url,expected_base_path", [
    ('https://example.com/api/v1/zaken/7C61204C-BFD8-4A66-B826-5DF8CB7F9A60', '/api/v1/'),
    ('https://example.com/api/v1/zaken/7c61204c-bfd8-4a66-b826-5df8cb7f9a60', '/api/v1/'),
    ('https://api.example.com/v1/zaken/7c61204c-bfd8-4a66-b826-5df8cb7f9a60', '/v1/'),
    ('https://api.example.com/zaken/7c61204c-bfd8-4a66-b826-5df8cb7f9a60', '/'),
    ('https://example.com/api/v1/zaken/7c61204c-bfd8-4a66-b826-5df8cb7f9a60/'
     'informatieobjecten/a7bdfe04-fb17-46f8-9884-541f5d7611f8', '/api/v1/'),
])
def test_client_from_detail_url(detail_url, expected_base_path):
    client = Client.from_url(detail_url)
    assert client.base_path == expected_base_path
