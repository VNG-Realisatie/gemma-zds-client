import os

from zds_client import Client

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "config.yaml"))


def test_client_from_static_config():
    Client.load_config(CONFIG_FILE)

    client = Client("client1")

    assert (
        repr(client)
        == "<Client: service='client1' base_url='https://example.com/api/v1/'>"
    )

    assert client.base_url == "https://example.com/api/v1/"
    assert client.auth.client_id == "some-client-id"
    assert client.auth.secret == "oh-no"


def test_client_loading():
    Client.load_config(zrc={"scheme": "http", "host": "localhost", "port": 8000})

    client = Client("zrc")
    assert client.base_url == "http://localhost:8000/api/v1/"


def test_load_with_auth():
    Client.load_config(
        zrc={
            "scheme": "http",
            "host": "localhost",
            "port": 8000,
            "auth": {"client_id": "foo", "secret": "bar"},
        }
    )

    client = Client("zrc")
    credentials = client.auth.credentials()

    assert "Authorization" in credentials
    bits = credentials["Authorization"].split(".")
    assert len(bits) == 3


def test_set_client_base_url():
    Client.load_config(CONFIG_FILE)
    client = Client("client1")

    client.base_url = "https://another.example"

    assert client.base_url == "https://another.example"
