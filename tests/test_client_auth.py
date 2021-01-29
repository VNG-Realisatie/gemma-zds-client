import base64
import json

import jwt

from zds_client import ClientAuth


def test_credentials_header():
    auth = ClientAuth(client_id="client_id", secret="secret")
    credentials = auth.credentials()

    assert "Authorization" in credentials
    parts = credentials["Authorization"].split(" ")
    assert parts[0] == "Bearer"


def test_client_id_in_body():
    auth = ClientAuth(client_id="client id", secret="secret")
    credentials = auth.credentials()["Authorization"]

    token = credentials.split(" ")[1]

    payload = jwt.decode(
        token,
        algorithms=["HS256"],
        options={"verify_signature": False},
    )

    assert "client_id" in payload
    assert "zds" not in payload
    assert payload["client_id"] == "client id"


def test_explicit_alg():
    auth = ClientAuth("dummy", "dummy")
    credentials = auth.credentials()["Authorization"]
    token = credentials.split(" ")[1]
    header = token.split(".")[0].encode()
    # taken from django.utils.http.urlsafe_base64_decode
    decoded = base64.urlsafe_b64decode(
        header.ljust(len(header) + len(header) % 4, b"=")
    )

    jwt_header = json.loads(decoded)

    assert jwt_header["alg"] == "HS256"
