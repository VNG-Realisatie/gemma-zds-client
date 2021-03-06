import requests_mock

from zds_client import Client


class HookClient(Client):
    schema = {"paths": {}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pre = None
        self.post = None

    def pre_request(self, method, url, *args, **kwargs):
        self.pre = (method, url)

    def post_response(self, pre_id, response_data):
        self.post = response_data


HookClient.load_config(tests={"host": "example.com", "scheme": "https"})


def test_hooks_fire():
    client = HookClient("tests", base_path="/")

    with requests_mock.Mocker() as m:
        m.register_uri("GET", "https://example.com/test", json={"ok": True})
        client.request("test", "get_test")

    assert client.pre == ("GET", "https://example.com/test")
    assert client.post == {"ok": True}
